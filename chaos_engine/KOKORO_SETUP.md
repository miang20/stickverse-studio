# Kokoro — required voice engine

Kokoro is the **only** narrator in this test. There is **no eSpeak/robotic voice fallback**; eSpeak-ng is a phonemization dependency, not the output voice.

In a Google Colab cell:

```python
!git clone -b chaos-engine-v1 https://github.com/miang20/stickverse-studio.git
!python stickverse-studio/chaos_engine/kokoro_setup.py --install --output /content/kokoro_voice_test.wav
```

A successful run prints `PASS Kokoro ...` and writes a 24 kHz WAV file. Listen to the WAV before approving narration quality. If network installation, model download or synthesis fails, it reports an error rather than claiming success.

This script has been committed but **has not passed an online Colab execution test**. It needs an internet-enabled runtime to install packages and download Kokoro weights.
