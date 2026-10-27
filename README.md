# STICKVERSE STUDIO

Standalone Android-friendly **procedural 2D stickman animation** tool. **No NotebookLM and no mandatory paid AI API.**

## Implemented prototype
- Script split into scenes, keyword-driven movement (walk/run/jump/fall/fight/fear/think)
- Six niche color palettes: psychology, science, horror, survival, history, comedy
- Actual animated frame sequences, parallax-style backgrounds, expressive faces and dynamic captions
- 16:9 MP4 output in 720p or 1080p via FFmpeg
- Optional online Edge TTS English narration (needs internet)
- Scene-plan JSON, Gradio UI and password-protected temporary Colab share link

## Launch from Android Google Colab
Open a new Colab notebook, add one code cell, run:

```python
!python - <<'PY'
import urllib.request
url="https://raw.githubusercontent.com/miang20/stickverse-studio/main/COLAB_LAUNCH.py"
urllib.request.urlretrieve(url,"/content/stickverse_launch.py")
PY
!python /content/stickverse_launch.py
```

The notebook installs dependencies, clones/pulls the repository, prints a login username/password and launches a temporary Gradio link. Keep Colab running. Do not share the password.

## Important limitations
This is an **initial working-code prototype, not a verified production renderer**. Actions are selected by simple English keyword matching; no AI semantic direction or advanced character rigging yet. The same base stickman and backgrounds are reused. Voice timing is not synchronized to scenes: long narration may be cut off, and short narration may end before video. 10–15 minute videos will be CPU-intensive and slow on free Colab; sessions may expire. Online TTS is not guaranteed. Free GPU or permanent hosting is not included. No automatic viral success or monetization guarantee. Originality, YouTube policy compliance and rights clearance remain the creator's responsibility.

## Development tests
`python -m unittest discover -s tests -v`
