"""CHAOS ENGINE integrated renderer.
Requires rights-approved footage, reviewed script and installed Kokoro/FFmpeg.
Never labels an unverified output production-ready.
"""
import argparse, json, subprocess, shutil, sys
from pathlib import Path
from scene_planner import plan
from pipeline_v2 import kokoro_voice, duration_seconds

def run(cmd):
    subprocess.run(cmd,check=True)

def render(script_path,assets_path,out_dir):
    root=Path(out_dir).resolve();root.mkdir(parents=True,exist_ok=True)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe required")
    script=Path(script_path).read_text(encoding="utf-8").strip()
    assets=json.loads(Path(assets_path).read_text(encoding="utf-8"))
    shotplan=plan(script,assets)
    (root/"shot_plan.json").write_text(json.dumps(shotplan,indent=2),encoding="utf-8")
    lines=[s["narration"] for s in shotplan["scenes"]]
    audio=root/"narration.wav"
    kokoro_voice(lines,audio)
    actual_duration=duration_seconds(audio)
    estimated=shotplan["duration_estimate"]
    if actual_duration<=0:raise RuntimeError("Empty narration")
    scale=actual_duration/estimated
    shots=[]
    for i,scene in enumerate(shotplan["scenes"]):
        src=Path(scene["visual"]).resolve()
        seconds=max(0.4,scene["duration"]*scale)
        dest=root/f"shot_{i:03}.mp4"
        # Supports video or stills. Input is always a locally approved asset.
        is_image=src.suffix.lower() in (".jpg",".jpeg",".png",".webp")
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y"]
        if is_image:cmd+=["-loop","1"]
        cmd+=["-i",str(src),"-t",str(seconds),"-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24,format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(dest)]
        run(cmd);shots.append(dest)
    concat=root/"concat.txt"
    concat.write_text("".join("file '"+p.name+"'\n" for p in shots),encoding="utf-8")
    silent=root/"silent.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    video=root/"final.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-t",str(actual_duration),"-c:v","copy","-c:a","aac","-movflags","+faststart",str(video)])
    if not video.exists() or video.stat().st_size<1000:raise RuntimeError("Output video invalid")
    (root/"render_report.json").write_text(json.dumps({"video":str(video),"seconds":actual_duration,"scene_count":len(shots),"review_required":True},indent=2))
    return video

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--script",required=True);p.add_argument("--assets",required=True);p.add_argument("--out",default="output/final")
    a=p.parse_args();print(render(a.script,a.assets,a.out))
