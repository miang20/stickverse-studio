# CHAOS ENGINE — V1 renderer foundation

First milestone: a reproducible 720p MP4 with scene timing, text overlays and an audio track (silent placeholder). This is **not** yet a narrated 1080p documentary or an AI research tool.

## Run (Linux / Google Colab)

Install FFmpeg (Colab normally includes it), then:

```bash
python chaos_engine/render.py chaos_engine/demo.json --output output/chaos_preview.mp4
```

Requirements: Python 3.9+, FFmpeg with libx264, AAC and subtitles/libass filters.

Next milestones: Kokoro voice integration, visual assets with rights metadata, animated overlays, render validation, source research and mobile interface.

The engine does not download or republish third-party videos without rights review.
