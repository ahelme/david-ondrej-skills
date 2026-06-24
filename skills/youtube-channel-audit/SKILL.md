---
name: youtube-channel-audit
description: Fetch the last N long-form uploads of a YouTube channel (titles, upload dates, view counts via CSV + full-res PNG thumbnails) with yt-dlp, then analyze packaging patterns — winning title formats, thumbnail styles, topics — and write a concise high-signal report.md. Use when the user wants a channel audit, "analyze my last 50 videos", "which titles/thumbnails work", "what's performing on my channel", or bulk video metadata + thumbnail pulls.
---

# YouTube Channel Audit

Pull metadata + thumbnails for a channel's recent long-form uploads, mine them for packaging patterns, write a report. Default N = 50.

## Output structure

All files in one new subfolder (e.g. `docs/data/youtube-last-50/` in the workspace, or where the user says):

- `videos.csv` — `rank,title,upload_date,view_count,duration_sec,video_id,url,thumbnail_file`
- `thumbnails/NN_<videoid>.png` — full resolution
- `report.md` — the analysis

## Step 1 — Fetch video IDs (long-form only)

The channel's `/videos` tab already excludes Shorts. Fetch ~20% extra as buffer for failed lookups:

```bash
mkdir -p OUTDIR/thumbnails && cd OUTDIR
yt-dlp --flat-playlist --playlist-end 60 --print "%(id)s" \
  "https://www.youtube.com/@HANDLE/videos" > ids.txt
```

## Step 2 — Metadata in parallel

```bash
cat ids.txt | xargs -P 4 -I VID yt-dlp --skip-download --no-warnings \
  --print "%(id)s ||| %(title)s ||| %(upload_date)s ||| %(view_count)s ||| %(duration)s ||| %(thumbnail)s" \
  "https://www.youtube.com/watch?v=VID" >> meta_raw.txt 2>fetch_errors.log
```

## Step 3 — Build CSV + thumbnail job list

```bash
python3 << 'EOF'
import csv
order = [l.strip() for l in open("ids.txt") if l.strip()]
meta = {}
for line in open("meta_raw.txt"):
    parts = [p.strip() for p in line.split(" ||| ")]
    if len(parts) == 6:
        meta[parts[0]] = parts
rows = []
for vid in order:
    if vid in meta and len(rows) < 50:   # N
        _, title, ud, views, dur, thumb = meta[vid]
        rows.append({"rank": len(rows)+1, "title": title,
            "upload_date": f"{ud[:4]}-{ud[4:6]}-{ud[6:]}",
            "view_count": int(views), "duration_sec": int(dur),
            "video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail_file": f"thumbnails/{len(rows)+1:02d}_{vid}.png",
            "_thumb_url": thumb})
with open("videos.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["rank","title","upload_date","view_count",
        "duration_sec","video_id","url","thumbnail_file"], extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
with open("thumb_jobs.txt", "w") as f:
    for r in rows:
        f.write(f"{r['rank']:02d}_{r['video_id']}\t{r['_thumb_url']}\n")
EOF
```

## Step 4 — Thumbnails as full-res PNG

```bash
# macOS (sips). On Linux use ImageMagick: magick in.tmp out.png
cat thumb_jobs.txt | xargs -P 8 -L1 sh -c \
  'curl -fsSL "$1" -o "thumbnails/$0.tmp" && sips -s format png "thumbnails/$0.tmp" --out "thumbnails/$0.png" >/dev/null 2>&1 && rm "thumbnails/$0.tmp"'
```

Verify count matches CSV rows before proceeding. Delete intermediates (`ids.txt`, `meta_raw.txt`, `thumb_jobs.txt`, `fetch_errors.log`) after success.

## Step 5 — Performance metric (critical)

Raw views/day is recency-biased (new uploads always spike). Compute BOTH:

- `vpd` = views / age_days — shows current heat
- `rel` = views / median(views of videos from the same upload month) — **the ranking metric**. 1.0x = average month performance. Use `rel` for all winner/loser claims.

## Step 6 — Analysis

1. **Titles**: bucket by regex (recurring templates, numbers, drama words like destroyed/killed/RIP, question marks, length, tool names, "tutorial/course"). Report median `rel` AND `n` per bucket — small n must be flagged, not hidden.
2. **Thumbnails**: Read the PNGs in batches of ~5 with the image-capable Read tool. For each note: face (whose — own face vs famous person), exact text on image, style (template/mascot/screenshot/logo-only), distinctive artifact. Correlate against `rel`.
3. **Topics**: cluster videos by subject, median `rel` per cluster, rank clusters.

## Step 7 — report.md

Concise and high-signal. Structure: TL;DR (5 biggest signals) → top 10 vs bottom 10 table (`rel` multiples) → title patterns that work → thumbnail patterns that work → topic hierarchy → action rules. Every claim carries a number (rel multiple + n). End with concrete do/stop-doing rules, not generic advice.

## Failure handling

- yt-dlp failure: run `yt-dlp -U` once, retry once, then stop.
- **429 / "Sign in to confirm you're not a bot"** = IP flagged. STOP — do not retry in a loop.
- Some IDs failing metadata is fine — the buffer exists for this. Proceed if you have ≥ N rows; otherwise report the shortfall.
- Thumbnail URL 404: retry with `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`, fall back to `hqdefault.jpg`.
