#!/usr/bin/env python3
"""Convert a raw dataset into Fireworks-ready SFT JSONL (train + eval split).

Handles the shapes you actually get from Hugging Face or your own logs:
  * rows that already contain a `messages` list (OpenAI style)   -> passthrough + clean
  * agentic `trajectory` datasets (SWE-agent / OpenHands traces) -> --messages-field trajectory
  * ShareGPT rows with a `conversations` list of {from,value}    -> remap roles
  * flat rows with separate instruction/response columns         -> assemble a turn

It normalizes to Fireworks' schema ({"messages":[...]} + optional root "tools"),
optionally enforces a single consistent system prompt, keeps agentic tool-calling
turns intact, drops empty + over-length rows, de-dupes, shuffles deterministically,
splits train/eval, and validates the result.

Agentic-trajectory handling (automatic — no flag needed):
  * assistant turns that ONLY emit tool_calls (empty content) are valid targets;
  * tool_calls[].function.arguments is coerced to a JSON *string* (Fireworks wants
    a string, not an object);
  * a `role:"tool"` message missing `tool_call_id` is linked (FIFO) to the ids in
    the preceding assistant's tool_calls (SWE-agent/OpenHands traces omit them);
  * pass `--tools-field tools` to promote a `tools` column to the root-level `tools`
    array, and `--filter resolved=1` to keep only successful trajectories.

Examples
--------
  # HF dataset already in messages form (like cfahlgren1/react-code-instructions)
  python prepare_fireworks_dataset.py --input hf:cfahlgren1/react-code-instructions \
      --out ./out --keep-only-messages --eval-size 50 --dedup

  # Agentic SWE trajectories, successful only, carrying tool defs (SWE-rebench shape)
  python prepare_fireworks_dataset.py \
      --input hf:nebius/SWE-rebench-openhands-trajectories \
      --messages-field trajectory --tools-field tools --filter resolved=1 \
      --keep-only-messages --max-context 65536 --out ./out

  # nvidia/Open-SWE-Traces (has configs + model-named splits; no tools column;
  # tool_call_ids are reconstructed automatically). Point at hf: or a parquet dir.
  python prepare_fireworks_dataset.py --input hf:nvidia/Open-SWE-Traces \
      --hf-config sweagent --hf-split minimax_m25 \
      --messages-field trajectory --filter resolved=1 \
      --keep-only-messages --max-context 65536 --out ./out

  # Local ShareGPT-style file, inject one consistent system prompt
  python prepare_fireworks_dataset.py --input data.jsonl \
      --conversations-field conversations --system @system_prompt.txt --out ./out

  # Flat CSV with prompt/completion columns
  python prepare_fireworks_dataset.py --input pairs.csv \
      --user-col prompt --assistant-col completion \
      --system "You are a helpful assistant." --out ./out
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import random
import sys

ALLOWED_MSG_KEYS = {"role", "content", "weight", "tool_calls",
                    "tool_call_id", "name", "reasoning_content"}
SHAREGPT_ROLE = {"system": "system", "human": "user", "user": "user",
                 "gpt": "assistant", "assistant": "assistant", "tool": "tool"}


def read_system(value):
    """Literal string, or @path to read the prompt from a file."""
    if value is None:
        return None
    if value.startswith("@"):
        with open(value[1:], encoding="utf-8") as f:
            return f.read().strip()
    return value


def _iter_parquet(path):
    """Stream rows from a .parquet file or a directory of them, row-group by row-group,
    so an 18 GB dataset never lands in memory. Prefers pyarrow; falls back to pandas."""
    files = ([path] if path.endswith(".parquet")
             else sorted(glob.glob(os.path.join(path, "**", "*.parquet"), recursive=True)))
    if not files:
        sys.exit(f"No .parquet files found at {path}")
    try:
        import pyarrow.parquet as pq
    except ImportError:
        try:
            import pandas as pd
        except ImportError:
            sys.exit("Reading .parquet needs `pip install pyarrow` (or pandas).")
        for fp in files:
            for _, row in pd.read_parquet(fp).iterrows():
                yield row.to_dict()
        return
    for fp in files:
        pf = pq.ParquetFile(fp)
        for batch in pf.iter_batches(batch_size=64):
            for row in batch.to_pylist():
                yield row


def load_rows(spec, hf_config=None, hf_split=None):
    """Yield dict rows from hf:owner/name[:split], a parquet dir, .parquet, .jsonl, .json, .csv."""
    if spec.startswith("hf:"):
        try:
            from datasets import load_dataset
        except ImportError:
            sys.exit("Reading hf: sources needs `pip install datasets`.")
        ref, split = spec[3:], hf_split or "train"
        if ":" in ref and not hf_split:
            ref, split = ref.rsplit(":", 1)
        kwargs = {"split": split}
        if hf_config:
            kwargs["name"] = hf_config
        for r in load_dataset(ref, **kwargs):
            yield dict(r)
        return

    if os.path.isdir(spec) or spec.endswith(".parquet"):
        yield from _iter_parquet(spec)
        return

    ext = os.path.splitext(spec)[1].lower()
    if ext in (".jsonl", ".ndjson"):
        with open(spec, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    elif ext == ".json":
        with open(spec, encoding="utf-8") as f:
            data = json.load(f)
        for r in (data if isinstance(data, list) else data.get("data", [])):
            yield r
    elif ext == ".csv":
        import csv  # stdlib — no pandas needed for the common spreadsheet case
        with open(spec, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                yield dict(row)
    else:
        sys.exit(f"Unsupported input: {spec}")


def _norm_tool_calls(tcs, mint_prefix):
    """Return OpenAI-shaped tool_calls, arguments kept as a JSON *string*, ids minted if missing."""
    out = []
    for j, tc in enumerate(tcs or []):
        if not isinstance(tc, dict):
            continue
        fn = tc.get("function") or {}
        args = fn.get("arguments")
        if args is None:
            args = ""
        elif not isinstance(args, str):        # Fireworks wants arguments as a string
            args = json.dumps(args, ensure_ascii=False)
        out.append({
            "id": tc.get("id") or f"{mint_prefix}_{j}",
            "type": tc.get("type") or "function",
            "function": {"name": fn.get("name", ""), "arguments": args},
        })
    return out


def clean_message(m, idx=0):
    """Keep only schema keys; normalize agentic tool-calling turns."""
    out = {k: v for k, v in m.items() if k in ALLOWED_MSG_KEYS and v is not None}
    if out.get("role") == "assistant" and out.get("tool_calls"):
        out["tool_calls"] = _norm_tool_calls(out["tool_calls"], f"call_{idx}")
        out.setdefault("content", "")  # tool-only assistant turns must carry a content key
    return out


def link_tool_call_ids(msgs):
    """Fill missing tool_call_id/name on tool turns from the preceding assistant's
    tool_calls (FIFO). SWE-agent/OpenHands traces store ids on the call but not the
    result; this reconstructs the link so the sample is valid OpenAI tool format."""
    pending = []  # queue of (id, name)
    for m in msgs:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            pending = [(tc["id"], tc["function"]["name"]) for tc in m["tool_calls"]]
        elif m.get("role") == "tool" and not m.get("tool_call_id") and pending:
            tc_id, tc_name = pending.pop(0)
            m["tool_call_id"] = tc_id
            m.setdefault("name", tc_name)
    return msgs


def to_messages(row, args, system, idx):
    """Normalize one source row into a list of Fireworks chat messages (or None)."""
    mf = args.messages_field
    if mf and isinstance(row.get(mf), list):                        # 1) messages / trajectory
        msgs = [clean_message(m, idx) for m in row[mf]
                if isinstance(m, dict) and m.get("role")]
        msgs = link_tool_call_ids(msgs)
    elif args.conversations_field and isinstance(row.get(args.conversations_field), list):
        msgs = []                                                   # 2) ShareGPT conversations
        for t in row[args.conversations_field]:
            role = SHAREGPT_ROLE.get(str(t.get(args.sharegpt_role_key, "")).lower())
            if role:
                msgs.append({"role": role, "content": t.get(args.sharegpt_content_key, "")})
    elif args.user_col:                                             # 3) flat columns
        msgs = []
        if args.system_col and row.get(args.system_col):
            msgs.append({"role": "system", "content": str(row[args.system_col])})
        msgs.append({"role": "user", "content": str(row.get(args.user_col, ""))})
        msgs.append({"role": "assistant", "content": str(row.get(args.assistant_col, ""))})
    else:
        return None

    if system is not None:  # enforce ONE consistent system prompt
        msgs = [m for m in msgs if m.get("role") != "system"]
        msgs.insert(0, {"role": "system", "content": system})
    # Fireworks requires the system message (if any) to be first.
    if msgs and any(m.get("role") == "system" for m in msgs) and msgs[0].get("role") != "system":
        sys_msgs = [m for m in msgs if m.get("role") == "system"]
        msgs = sys_msgs[:1] + [m for m in msgs if m.get("role") != "system"]
    return msgs or None


def has_trainable_assistant(msgs):
    """An assistant turn is trainable if it has non-empty content OR emits tool_calls."""
    for m in msgs:
        if m.get("role") != "assistant" or m.get("weight", 1) == 0:
            continue
        if str(m.get("content") or "").strip() or m.get("tool_calls"):
            return True
    return False


def approx_tokens(msgs):
    """chars/4 heuristic, counting content + reasoning_content + tool_calls (args matter
    a lot for agentic data — omitting them badly under-counts length)."""
    total = 0
    for m in msgs:
        c = m.get("content")
        if isinstance(c, str):
            total += len(c)
        elif isinstance(c, list):
            total += sum(len(p.get("text", "")) for p in c if isinstance(p, dict))
        total += len(m.get("reasoning_content") or "")
        for tc in m.get("tool_calls") or []:
            fn = tc.get("function", {})
            total += len(fn.get("name", "")) + len(str(fn.get("arguments", "")))
    return total // 4


def parse_filters(pairs):
    """['resolved=1', 'lang=python'] -> [('resolved','1'), ('lang','python')]"""
    out = []
    for p in pairs or []:
        if "=" not in p:
            sys.exit(f"--filter must be COL=VALUE, got {p!r}")
        col, val = p.split("=", 1)
        out.append((col.strip(), val.strip()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True,
                    help="hf:owner/name[:split] | parquet dir | .parquet | .jsonl | .json | .csv")
    ap.add_argument("--out", required=True, help="output dir (writes train.jsonl + eval.jsonl)")
    ap.add_argument("--messages-field", default="messages",
                    help="column holding a messages list (use 'trajectory' for agent traces)")
    ap.add_argument("--tools-field", help="column of tool/function defs -> promoted to root 'tools'")
    ap.add_argument("--filter", action="append", metavar="COL=VALUE",
                    help="keep only rows where str(row[COL])==VALUE (repeatable, e.g. resolved=1)")
    ap.add_argument("--hf-config", help="HF dataset config/subset name (e.g. sweagent)")
    ap.add_argument("--hf-split", help="HF split name (e.g. minimax_m25; default train)")
    ap.add_argument("--conversations-field", help="ShareGPT column of {from,value} turns")
    ap.add_argument("--sharegpt-role-key", default="from")
    ap.add_argument("--sharegpt-content-key", default="value")
    ap.add_argument("--user-col")
    ap.add_argument("--assistant-col")
    ap.add_argument("--system-col")
    ap.add_argument("--system", help="literal system prompt or @file; injected as one consistent system message")
    ap.add_argument("--keep-only-messages", action="store_true", help="strip non-schema columns (recommended)")
    ap.add_argument("--eval-size", type=int, default=50, help="eval examples to carve out (capped at 10%%)")
    ap.add_argument("--max-context", type=int, default=32768, help="drop examples longer than this (approx tokens)")
    ap.add_argument("--limit", type=int, help="only read the first N source rows")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dedup", action="store_true", help="drop exact-duplicate conversations")
    args = ap.parse_args()

    system = read_system(args.system)
    filters = parse_filters(args.filter)
    out, seen = [], set()
    dropped_filter = dropped_empty = dropped_long = dropped_dup = 0

    for i, row in enumerate(load_rows(args.input, args.hf_config, args.hf_split)):
        if args.limit and i >= args.limit:
            break
        if filters and any(str(row.get(c)) != v for c, v in filters):
            dropped_filter += 1
            continue
        msgs = to_messages(row, args, system, i)
        if not msgs or not has_trainable_assistant(msgs):
            dropped_empty += 1  # nothing to learn from (no assistant content or tool_call)
            continue
        if approx_tokens(msgs) > args.max_context:
            dropped_long += 1
            continue
        rec = {"messages": msgs}
        tools = row.get(args.tools_field) if args.tools_field else None
        if tools:
            rec["tools"] = tools
        if not args.keep_only_messages:
            for k, v in row.items():
                if k not in (args.messages_field, args.tools_field) and k not in rec:
                    rec[k] = v
        if args.dedup:
            h = hashlib.sha1(json.dumps(rec["messages"], sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
            if h in seen:
                dropped_dup += 1
                continue
            seen.add(h)
        out.append(rec)

    random.Random(args.seed).shuffle(out)
    n = len(out)
    k = min(args.eval_size, max(0, n // 10))  # never starve train on tiny sets
    eval_rows, train_rows = out[:k], out[k:]

    os.makedirs(args.out, exist_ok=True)
    train_path = os.path.join(args.out, "train.jsonl")
    eval_path = os.path.join(args.out, "eval.jsonl")
    for path, rows in ((train_path, train_rows), (eval_path, eval_rows)):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

    print(f"kept {n} examples  (dropped: filtered {dropped_filter}, empty/unmappable {dropped_empty}, "
          f"over-context {dropped_long}, duplicate {dropped_dup})")
    print(f"  train: {len(train_rows):>6} -> {train_path}")
    print(f"  eval : {len(eval_rows):>6} -> {eval_path}")

    try:  # reuse the validator so output is guaranteed-checked
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from validate_fireworks_dataset import validate_records
        errors, warnings, _ = validate_records(train_rows, args.max_context)
        verdict = "READY" if not errors else "FIX ERRORS (run validate_fireworks_dataset.py)"
        print(f"validation: {len(errors)} errors, {len(warnings)} warnings on train.jsonl  -> {verdict}")
    except Exception as e:  # noqa: BLE001 - validation is best-effort here
        print(f"(skipped inline validation: {e})")


if __name__ == "__main__":
    main()
