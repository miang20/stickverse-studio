"""CHAOS ENGINE V1: render a real narrated documentary teaser from a scene manifest."""
import argparse, json, math, subprocess, shutil
from pathlib import Path

def render(manifest_path, output):
    if not shutil.which("ffmpeg"): raise RuntimeError("FFmpeg is required")
    manifest=json.loads(Path(manifest_path).read_text())
    scenes=manifest["scenes"]
    if not scenes: raise ValueError("No scenes")
    out=Path(output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    parts=[]
    for i,s in enumerate(scenes):
        duration=float(s.get("duration",4))
        if not (0.5<=duration<=120): raise ValueError("Invalid duration")
        text=s.get("text","").replace("\n"," ")[:180]
        # Draw text via generated subtitle file; no unsafe shell interpolation.
        sub=out.parent/f"chaos_{i:03}.srt"
        sub.write_text(f"1\n00:00:00,000 --> 00:00:{int(duration):02},{int((duration%1)*1000):03}\n{text}\n",encoding="utf-8")
        clip=out.parent/f"chaos_{i:03}.mp4"
        color=s.get("color","0x101522")
        if not __import__("re").fullmatch(r"0x[0-9a-fA-F]{6}",color): raise ValueError("Invalid color")
        vf=f"subtitles={sub.name}:force_style='FontSize=24,Alignment=5,PrimaryColour=&H00FFFFFF,Outline=2'"
        subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"color=c={color}:s=1280x720:r=24","-f","lavfi","-i","anullsrc=r=48000:cl=stereo","-t",str(duration),"-vf",vf,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-shortest",str(clip)],cwd=out.parent,check=True)
        parts.append(clip)
    listing=out.parent/"chaos_concat.txt"
    listing.write_text("".join("file '"+p.name+"'\n" for p in parts))
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listing.name,"-c","copy",str(out)],cwd=out.parent,check=True)
    print(f"Rendered {out}")

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("manifest");ap.add_argument("--output",default="output/chaos_preview.mp4")
    a=ap.parse_args();render(a.manifest,a.output)
