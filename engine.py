"""STICKVERSE procedural 2D renderer. Offline visuals; no AI video API."""
from __future__ import annotations
import math, re, os, random, subprocess, tempfile, wave, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio_ffmpeg

PALETTES={
 "Psychology":((13,18,30),(76,232,218),(237,244,250)),
 "Science":((8,17,39),(92,183,255),(239,248,255)),
 "Horror":((19,12,23),(251,78,104),(251,235,239)),
 "Survival":((15,26,24),(245,186,75),(241,245,226)),
 "History":((32,23,23),(233,191,118),(251,237,207)),
 "Comedy":((24,23,43),(247,127,221),(250,245,255)),
}
ACTIONS={
 "run":("run","escape","chase","rush","flee","sprint"),
 "fight":("fight","punch","battle","attack","hit"),
 "fall":("fall","collapse","trip","drop","crash"),
 "jump":("jump","leap","fly","gravity"),
 "fear":("fear","scared","terrified","horror","shadow","monster","danger"),
 "think":("think","wonder","why","question","imagine","remember","realize"),
 "walk":("walk","enter","move","travel","explore","approach"),
}
def split_script(script, max_words=27):
    script=re.sub(r"\s+"," ",script).strip()
    if not script: raise ValueError("Paste an English script first.")
    sentences=re.split(r"(?<=[.!?])\s+",script)
    out=[]; current=[]
    for sentence in sentences:
        words=sentence.split()
        while len(words)>max_words:
            if current:out.append(" ".join(current));current=[]
            out.append(" ".join(words[:max_words]));words=words[max_words:]
        if current and len(current)+len(words)>max_words:
            out.append(" ".join(current));current=[]
        current+=words
    if current:out.append(" ".join(current))
    return out[:150]
def action_for(text):
    s=text.lower()
    for action,terms in ACTIONS.items():
        if any(re.search(r"\b"+re.escape(w)+r"\b",s) for w in terms):return action
    return "walk"
def get_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        if os.path.isfile(p):return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def draw_frame(w,h,t,duration,scene,idx,niche,subtitles=True):
    bg,accent,fg=PALETTES.get(niche,PALETTES["Psychology"])
    im=Image.new("RGB",(w,h),bg);d=ImageDraw.Draw(im)
    scale=w/1280
    floor=int(h*.79)
    rng=random.Random(idx+42)
    # Layered parallax buildings and glowing atmosphere
    for j in range(14):
        x=int((j*119-50-(t*18 if idx%2==0 else -t*12))% (w+140)-70)
        bh=int(h*(.14+.16*rng.random()))
        d.rectangle((x,floor-bh,x+int(77*scale),floor),fill=tuple(min(255,int(c*.60+14)) for c in bg))
        for row in range(3):
            d.rectangle((x+int(14*scale),floor-bh+int((row+1)*27*scale),x+int(22*scale),floor-bh+int((row+1)*27*scale)+int(8*scale)),fill=tuple(int(c*.30) for c in accent))
    d.ellipse((int(w*.74),int(h*.11),int(w*.86),int(h*.32)),outline=tuple(int(c*.28) for c in accent),width=max(2,int(3*scale)))
    d.line((0,floor,w,floor),fill=tuple(int(c*.45) for c in accent),width=max(2,int(4*scale)))
    action=action_for(scene)
    phase=t*({"run":15,"fight":11,"walk":7}.get(action,5))
    progress=min(1,t/max(.01,duration))
    x=int(w*(.24+.42*progress)) if action in ("run","walk") else int(w*(.47+0.035*math.sin(t*.8)))
    y=floor-int(100*scale)
    if action=="jump":y-=int(abs(math.sin(t*2.7))*125*scale)
    elif action=="fall":y+=int(45*scale*min(1,progress*2))
    else:y+=int(math.sin(phase)*4*scale)
    unit=scale
    head=int(25*unit)
    cy=y-int(136*unit)
    thick=max(3,int(8*unit))
    def limb(points,width=thick):
        d.line(points,fill=accent,width=width,joint="curve")
    d.ellipse((x-head,cy-head,x+head,cy+head),outline=accent,width=thick)
    # Eyes give basic emotional acting
    eye=int(5*unit)
    if action=="fear":
        d.ellipse((x-int(12*unit),cy-int(5*unit),x-int(6*unit),cy+int(5*unit)),fill=fg)
        d.ellipse((x+int(6*unit),cy-int(5*unit),x+int(12*unit),cy+int(5*unit)),fill=fg)
    else:
        d.ellipse((x-int(11*unit),cy-int(4*unit),x-int(7*unit),cy),fill=fg)
        d.ellipse((x+int(7*unit),cy-int(4*unit),x+int(11*unit),cy),fill=fg)
    shoulder=cy+head+int(12*unit);hip=y-int(36*unit)
    limb([(x,shoulder),(x,hip)])
    swing=math.sin(phase)*35*unit
    if action=="think":
        limb([(x,shoulder),(x-int(25*unit),shoulder+int(35*unit))])
        limb([(x,shoulder),(x+int(28*unit),cy+int(22*unit))])
        d.ellipse((x+int(68*unit),cy-int(70*unit),x+int(84*unit),cy-int(54*unit)),outline=fg,width=max(2,int(3*unit)))
    elif action=="fight":
        limb([(x,shoulder),(x+int(75*unit),shoulder-int(25*unit)+int(swing*.5))])
        limb([(x,shoulder),(x-int(42*unit),shoulder+int(16*unit))])
        d.ellipse((x+int(72*unit),shoulder-int(30*unit),x+int(90*unit),shoulder-int(12*unit)),outline=fg,width=3)
    elif action=="fear":
        limb([(x,shoulder),(x-int(48*unit),shoulder-int(50*unit))])
        limb([(x,shoulder),(x+int(48*unit),shoulder-int(50*unit))])
    else:
        limb([(x,shoulder),(x-int(36*unit),shoulder+int(52*unit)+int(swing))])
        limb([(x,shoulder),(x+int(36*unit),shoulder+int(52*unit)-int(swing))])
    leg_swing=swing if action in ("run","walk") else 12*unit*math.sin(phase)
    limb([(x,hip),(x-int(28*unit)+int(leg_swing),y+int(62*unit))])
    limb([(x,hip),(x+int(28*unit)-int(leg_swing),y+int(62*unit))])
    # Scene metadata and dynamic captions
    d.text((int(45*unit),int(35*unit)),niche.upper()+"  /  "+str(idx+1).zfill(2),font=get_font(max(14,int(20*unit))),fill=accent)
    if subtitles:
        words=scene.split()
        portion=max(1,math.ceil(len(words)*progress))
        displayed=" ".join(words[max(0,portion-11):portion])
        f=get_font(max(18,int(31*unit)))
        bbox=d.textbbox((0,0),displayed,font=f)
        tx=max(20,(w-(bbox[2]-bbox[0]))//2)
        ty=int(h*.89)
        d.rounded_rectangle((tx-int(16*unit),ty-int(9*unit),min(w-10,tx+bbox[2]+int(16*unit)),ty+bbox[3]+int(15*unit)),radius=int(9*unit),fill=(4,8,15))
        d.text((tx,ty),displayed,font=f,fill=fg)
    return np.asarray(im)
def plan(script,niche="Psychology",seconds_per_scene=4):
    return [{"index":i+1,"text":s,"action":action_for(s),"duration":seconds_per_scene} for i,s in enumerate(split_script(script))]
def render_video(script,output,niche="Psychology",resolution="720p",seconds_per_scene=4,subtitles=True,voice_audio=None,progress=None):
    w,h=(1920,1080) if resolution=="1080p" else (1280,720)
    fps=24
    scenes=split_script(script)
    if not 1<=seconds_per_scene<=20:raise ValueError("Scene duration must be 1–20 seconds")
    output=str(Path(output).resolve())
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    # Stream RGB frames directly to ffmpeg to avoid huge temporary frame files.
    cmd=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r",str(fps),"-i","pipe:0"]
    if voice_audio:cmd+=["-i",str(voice_audio),"-map","0:v:0","-map","1:a:0","-af","apad","-t",str(len(scenes)*seconds_per_scene),"-c:a","aac","-b:a","160k"]
    cmd+=["-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-movflags","+faststart",output]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i,s in enumerate(scenes):
            for n in range(round(seconds_per_scene*fps)):
                proc.stdin.write(draw_frame(w,h,n/fps,seconds_per_scene,s,i,niche,subtitles).tobytes())
            if progress:progress((i+1)/len(scenes),desc=f"Rendering scene {i+1}/{len(scenes)}")
        proc.stdin.close()
        error=proc.stderr.read().decode(errors="replace")
        if proc.wait()!=0:raise RuntimeError("FFmpeg failed: "+error[-1200:])
    except Exception:
        proc.kill();proc.wait()
        try:proc.stdin.close()
        except Exception:pass
        raise
    Path(output).with_suffix(".json").write_text(json.dumps({"niche":niche,"scenes":plan(script,niche,seconds_per_scene)},indent=2))
    return output
