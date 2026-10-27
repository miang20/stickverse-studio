# STICKVERSE STUDIO — Browser Edition

**Primary app:** [index.html](index.html) + [studio.js](studio.js). Runs directly in Android Chrome using HTML Canvas and MediaRecorder. **No Google Colab, NotebookLM, account login, paid API, server, or API key.**

## Features currently implemented
- Paste an English script; split into up to 180 short scenes
- Niche presets: Psychology, Science, Horror, Survival, History, Comedy
- Moving stickman with simple walk, run, jump, fall, fight, fear and think motions, plus scrolling backgrounds
- Captions, 16:9 canvas, 360p/720p/1080p selections, real-time browser recording
- Download WebM on typical Android Chrome; MP4 only on browsers supporting MP4 MediaRecorder
- Preview without exporting

## Open as website (GitHub Pages)
1. Open repository **Settings → Pages**.
2. Set **Build and deployment → Source: GitHub Actions**.
3. GitHub Pages workflow [pages.yml](.github/workflows/pages.yml) deploys the site. Check **Actions** for result.
4. Expected site address after successful deployment: `https://miang20.github.io/stickverse-studio/`. Do not assume it is live until the workflow succeeds.

## Limitations — please read
This is an **early browser-only animation prototype**. It is NOT a professional AI video generator, and its animation actions are selected using basic keywords. Character, backgrounds, and movements are limited. **No narration, audio track, music, lip-sync, automatic thumbnails, or SEO generation yet.** Export runs in **real time** (a 10-minute video takes at least 10 minutes), and Android may interrupt recording when the browser is backgrounded or device memory is low. No universal MP4 export is guaranteed: Chrome may provide WebM only. Long-form 1080p export may fail on phones; start with 360p/720p. Rendering quality and GitHub Pages deployment have not been verified on the user's Android device.

### Legacy prototype
The Python files (`engine.py`, `studio.py`, `COLAB_LAUNCH.py`) are **legacy experiments** and **not needed** by the browser app. No Colab integration is required.

YouTube monetization is not guaranteed. Avoid mass-produced repetitive content; add original storytelling and distinctive production.
