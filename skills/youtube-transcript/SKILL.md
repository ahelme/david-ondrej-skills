---
name: youtube-transcript
description: Use whenever the user needs the transcript of a YouTube video — fetching, extracting, downloading, or pulling captions/subtitles/transcript text from a YouTube URL. Triggers on "get the transcript", "transcript of this video", "pull the captions", "download subtitles", "what does this YouTube video say".
---

# YouTube Transcript (via yt-dlp)

Fetch a YouTube video's captions (no video download) and save a clean raw `.txt` transcript.

## Save location
- If the user is in a real project/working dir → save there.
- Otherwise (no dir given, or cwd makes no sense) → save to `~/Downloads`.

## Fastest path

```bash
OUT="$(pwd)"            # or ~/Downloads if cwd makes no sense
META=$(yt-dlp --print "%(channel)s|%(title)s" --skip-download "URL")
NAME=$(echo "$META" | tr '| ' '__' | tr -cd '[:alnum:]_.-')   # "Channel_Title", spaces -> _, strip unsafe chars
yt-dlp --skip-download --write-subs --write-auto-subs \
  --sub-langs "en.*" --sub-format json3 \
  -o "$OUT/$NAME.%(ext)s" "URL"
```

**Always name the file `Channel_Title` with spaces replaced by `_`** (e.g. `Example_Channel_title_of_video.txt`). Fall back `channel` → `uploader` → `uploader_id` if `channel` is null.

- `--skip-download` = captions only. `--write-subs` + `--write-auto-subs` = manual first, auto as fallback (yt-dlp prefers manual automatically).
- **Always use `json3`, never VTT/SRT** — auto VTT repeats every line twice (rolling captions). json3 is clean structured JSON.

## Flatten json3 → raw text

```bash
python3 - "$OUT" <<'PY'
import json, html, re, glob, sys, pathlib
f = glob.glob(sys.argv[1] + "/*.json3")
if not f: sys.exit("no json3 file")
data = json.load(open(f[0], encoding="utf-8"))
parts = ["".join(s.get("utf8","") for s in e.get("segs") or []) for e in data.get("events", [])]
txt = re.sub(r"\s+", " ", html.unescape(" ".join(p.strip() for p in parts if p.strip()))).strip()
out = pathlib.Path(f[0]).with_suffix(".txt")
out.write_text(txt, encoding="utf-8"); print(out)
PY
```

Output: `<Channel_Title>.txt` in the chosen dir. Report the path; print the text if short.

## Notes
- Non-English / unknown language: run `yt-dlp --list-subs "URL"` first, then set `--sub-langs`.
- Newer yt-dlp may need `deno` on PATH for YouTube extraction.

## Failure handling
- On first failure: run `yt-dlp -U` once, retry once, then stop.
- **429 / "Sign in to confirm you're not a bot"** = IP flagged. STOP — do NOT retry in a loop (makes it worse).
- Empty / "no subtitles" = video has no captions. Report it; don't retry, don't switch tools.
- Never fall back to downloading audio for Whisper unless the user explicitly asks.
