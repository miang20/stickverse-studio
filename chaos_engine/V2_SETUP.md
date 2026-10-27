# CHAOS ENGINE V2 — Research, licensed visuals, Kokoro
This is an **experimental end-to-end pipeline**, not a verified 12–18-minute production system.

It uses Wikipedia for a **source-linked overview**, Wikimedia Commons for CC BY/CC0/public-domain **still images** (not stock video clips), Kokoro for natural English narration, and FFmpeg for moving Ken Burns-style footage.

## Google Colab
```python
!apt-get -qq update && apt-get -qq install -y ffmpeg espeak-ng
!pip -q install kokoro soundfile numpy
!git clone -b chaos-engine-v1 https://github.com/miang20/stickverse-studio.git
%cd stickverse-studio
!python chaos_engine/pipeline_v2.py --topic "Internet fraud" --out /content/chaos_output
```

Download `/content/chaos_output/video.mp4` from Colab's Files sidebar. Read `research.json` and `media_credits.json` before using any content. You may supply your own rights-cleared images via `--approved-assets /content/my_assets`.

**Limits:** This version is not investigative journalism; Wikipedia summaries alone do not establish allegations. Commons licenses require individual verification (including attribution, derivatives, publicity/privacy rights). Images have motion effects but are not real moving footage. If no suitable assets exist, the pipeline stops rather than fabricating visuals. Colab and Kokoro may need troubleshooting. Do not publish without manual fact checking. No paid API key is required, but GPU availability is not guaranteed.
