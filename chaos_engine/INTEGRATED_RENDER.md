# CHAOS ENGINE integrated render (experimental)

The `integrated_render.py` script connects script-based scene selection, **Kokoro**, approved video/image clips and **FFmpeg** to generate an MP4.

**Important:** The script and all media must be reviewed. This is not automatic investigative research, copyright clearance, or production-ready certification. Real clips are supported as input, but not guaranteed by automatic discovery. Captions, sound design, and robust clip synchronization are still limited.

## Inputs
- `script.txt`: reviewed English narration.
- `assets.json`: array of local video or image assets, each with `path`, `title`, `description`, `source`, `license`, and **`approved: true`** after review.

## Command
```bash
python chaos_engine/integrated_render.py --script script.txt --assets assets.json --out output/documentary
```
Outputs `final.mp4`, `narration.wav`, `shot_plan.json` and `render_report.json`.

## Colab dependencies
```bash
apt-get update && apt-get install -y ffmpeg espeak-ng
pip install kokoro soundfile numpy
```

## Known limitations
- No end-to-end render has been run on Google Colab yet.
- Clip timing uses estimated word duration rescaled to final audio, not word-level alignment.
- License tags are not a substitute for checking attribution, rights and usage restrictions.
- Research currently starts with a Wikipedia overview; claims must be checked with reliable primary sources.
