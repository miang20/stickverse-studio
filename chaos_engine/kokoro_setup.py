"""Kokoro installation verification and voice smoke test for Colab/Linux.
Fails loudly; never substitutes robotic TTS.
"""
import argparse, importlib.util, subprocess, shutil, sys
from pathlib import Path

def install():
    if not shutil.which("espeak-ng"):
        if shutil.which("apt-get"):
            subprocess.run(["apt-get","update"],check=True)
            subprocess.run(["apt-get","install","-y","espeak-ng","ffmpeg"],check=True)
        else:raise RuntimeError("Install espeak-ng using your OS package manager")
    subprocess.run([sys.executable,"-m","pip","install","--upgrade","kokoro","soundfile","numpy"],check=True)

def verify(output,voice):
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    pipeline=KPipeline(lang_code="a")
    script="The internet loved the story. But behind the viral headlines, something did not add up."
    parts=[]
    for _,_,audio in pipeline(script,voice=voice,speed=0.98):
        parts.append(np.asarray(audio,dtype=np.float32))
    if not parts:raise RuntimeError("Kokoro returned no audio")
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    data=np.concatenate(parts)
    if len(data)<24000:raise RuntimeError("Generated audio unexpectedly short")
    sf.write(str(output),data,24000)
    with sf.SoundFile(str(output)) as f:
        if f.samplerate!=24000 or f.frames<24000:raise RuntimeError("Invalid WAV output")
    print(f"PASS Kokoro voice={voice} wav={output} seconds={len(data)/24000:.2f}")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--install",action="store_true")
    p.add_argument("--voice",default="am_michael")
    p.add_argument("--output",default="output/kokoro_voice_test.wav")
    args=p.parse_args()
    if args.install:install()
    verify(args.output,args.voice)
