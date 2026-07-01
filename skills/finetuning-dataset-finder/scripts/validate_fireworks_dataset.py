#!/usr/bin/env python3
"""Validate a JSONL dataset against Fireworks AI supervised fine-tuning rules.

Checks the OpenAI-style chat schema Fireworks expects plus the documented limits,
then prints a human-readable report. Exit code 0 = ready to upload, 1 = hard errors.

    python validate_fireworks_dataset.py train.jsonl
    python validate_fireworks_dataset.py train.jsonl --max-context 32768 --recommend-min 1000

`validate_records(records, max_context)` is importable and returns
(errors, warnings, stats) so other scripts can reuse it.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

VALID_ROLES = {"system", "user", "assistant", "tool"}
HARD_MIN, HARD_MAX = 3, 3_000_000  # Fireworks per-dataset example bounds


def _content_len(content) -> int:
    """Character length of a message's content (string or list-of-parts)."""
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):  # multimodal / parts form
        return sum(len(p.get("text", "")) for p in content if isinstance(p, dict))
    return 0


def validate_records(records, max_context: int = 32768):
    errors, warnings = [], []
    roles = Counter()
    approx_tokens = []
    for i, rec in enumerate(records):
        loc = f"line {i + 1}"
        if not isinstance(rec, dict):
            errors.append(f"{loc}: record is not a JSON object")
            continue
        msgs = rec.get("messages")
        if not isinstance(msgs, list) or not msgs:
            errors.append(f"{loc}: missing or empty 'messages' array")
            continue
        root_w = rec.get("weight")
        if root_w is not None and not isinstance(root_w, (int, float)):
            errors.append(f"{loc}: root 'weight' must be a number")

        if any(m.get("role") == "system" for m in msgs if isinstance(m, dict)) \
                and (not isinstance(msgs[0], dict) or msgs[0].get("role") != "system"):
            errors.append(f"{loc}: a 'system' message must be the FIRST message")

        total_chars = 0
        last_role = None
        has_trainable_assistant = False
        for j, m in enumerate(msgs):
            if not isinstance(m, dict):
                errors.append(f"{loc} msg {j}: message is not an object")
                continue
            role = m.get("role")
            if role not in VALID_ROLES:
                errors.append(f"{loc} msg {j}: invalid role {role!r}")
            else:
                roles[role] += 1
            tcs = m.get("tool_calls")
            if "content" not in m and not tcs:
                errors.append(f"{loc} msg {j}: needs 'content' or 'tool_calls'")
            for tc in tcs or []:
                args = (tc.get("function") or {}).get("arguments")
                if args is not None and not isinstance(args, str):
                    errors.append(f"{loc} msg {j}: tool_call arguments must be a JSON string, not {type(args).__name__}")
            if role == "tool" and not m.get("tool_call_id"):
                warnings.append(f"{loc} msg {j}: tool result has no 'tool_call_id' to link it to its call")
            w = m.get("weight")
            if w is not None and w not in (0, 1):
                errors.append(f"{loc} msg {j}: message 'weight' must be 0 or 1, got {w!r}")
            total_chars += _content_len(m.get("content")) + len(m.get("reasoning_content") or "")
            for tc in tcs or []:
                fn = tc.get("function") or {}
                total_chars += len(fn.get("name", "")) + len(str(fn.get("arguments", "")))
            last_role = role
            if role == "assistant" and m.get("weight", 1) != 0 \
                    and (_content_len(m.get("content")) > 0 or tcs):
                has_trainable_assistant = True

        if not has_trainable_assistant:
            warnings.append(f"{loc}: no trainable assistant turn (nothing to learn from)")
        if last_role != "assistant":
            warnings.append(f"{loc}: conversation does not end with an assistant turn")
        approx = total_chars // 4  # rough chars/4 heuristic
        approx_tokens.append(approx)
        if approx > max_context:
            warnings.append(f"{loc}: ~{approx} tokens exceeds max context {max_context} (will be truncated)")

    return errors, warnings, {"roles": dict(roles), "approx_tokens": approx_tokens}


def load_jsonl(path):
    """Return (records, parse_errors). Malformed lines are reported, not raised."""
    records, parse_errors = [], []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                parse_errors.append(f"line {i + 1}: invalid JSON ({e})")
    return records, parse_errors


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="path to the .jsonl file to validate")
    ap.add_argument("--max-context", type=int, default=32768)
    ap.add_argument("--recommend-min", type=int, default=1000)
    args = ap.parse_args()

    records, parse_errors = load_jsonl(args.path)
    errors, warnings, stats = validate_records(records, args.max_context)
    errors = parse_errors + errors

    n = len(records)
    if n < HARD_MIN:
        errors.append(f"dataset has {n} examples; Fireworks requires at least {HARD_MIN}")
    if n > HARD_MAX:
        errors.append(f"dataset has {n:,} examples; Fireworks allows at most {HARD_MAX:,}")
    if HARD_MIN <= n < args.recommend_min:
        warnings.append(f"only {n} examples; ~{args.recommend_min}+ recommended for SFT "
                        f"(below this, consider RFT)")

    print(f"\n=== Fireworks dataset validation: {args.path} ===")
    print(f"examples: {n}")
    at = stats["approx_tokens"]
    if at:
        print(f"approx tokens/example: avg {sum(at) // len(at)}, max {max(at)}  (heuristic: chars/4)")
    print(f"role turns: {stats['roles']}")

    print(f"\nERRORS ({len(errors)}):")
    for e in errors[:50]:
        print("  x " + e)
    if len(errors) > 50:
        print(f"  ... and {len(errors) - 50} more")

    print(f"\nWARNINGS ({len(warnings)}):")
    for w in warnings[:50]:
        print("  ! " + w)
    if len(warnings) > 50:
        print(f"  ... and {len(warnings) - 50} more")

    ok = not errors
    print("\n" + ("READY: passes Fireworks hard requirements."
                  if ok else "NOT READY: fix the errors above before uploading."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
