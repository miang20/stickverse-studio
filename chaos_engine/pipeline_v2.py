"""CHAOS ENGINE V2: research -> licensed media -> Kokoro -> rendered video.
Public Wikipedia/Wikimedia APIs; review facts and media rights before publishing.
"""
import argparse, json, re, subprocess, shutil, urllib.parse, urllib.request, textwrap, html
from pathlib import Path

UA="ChaosEnginePrototype/0.2 (educational prototype; contact: local operator)"
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r)
def download(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=50) as r, open(path,"wb") as f: shutil.copyfileobj(r,f)
def wiki_research(topic):
    q=urllib.parse.quote(topic)
    search=get_json("https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="+q+"&srlimit=3&format=json")
    hits=search.get("query",{}).get("search",[])
    if not hits: raise RuntimeError("No Wikipedia result; provide a more specific topic")
    title=hits[0]["title"]
    data=get_json("https://en.wikipedia.org/api/rest_v1/page/summary/"+urllib.parse.quote(title.replace(" ","_")))
    extract=data.get("extract","")
    if not extract: raise RuntimeError("No verified article summary")
    return {"title":title,"summary":extract,"source":data.get("content_urls",{}).get("desktop",{}).get("page",""),"status":"Wikipedia overview only; verify each claim with primary sources"}
def commons_assets(query,folder,limit=4):
    folder.mkdir(parents=True,exist_ok=True)
    api="https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch="+urllib.parse.quote(query+" filetype:bitmap")+"&gsrnamespace=6&gsrlimit=15&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1280&format=json"
    data=get_json(api)
    found=[]
    for page in data.get("query",{}).get("pages",{}).values():
        info=(page.get("imageinfo") or [{}])[0]; meta=info.get("extmetadata",{})
        license_name=html.unescape(re.sub("<[^>]*>","",meta.get("LicenseShortName",{}).get("value",""))).strip()
        if not any(x in license_name.lower() for x in ("cc by","cc0","public domain")): continue
        url=info.get("thumburl") or info.get("url","")
        if not re.search(r"\.(jpe?g|png|webp)(\?|$)",url,re.I): continue
        path=folder/("asset_%02d.jpg"%len(found))
        try: download(url,path)
        except Exception: continue
        found.append({"file":str(path),"source":info.get("descriptionurl",""),"license":license_name,"attribution":re.sub("<[^>]*>","",meta.get("Artist",{}).get("value",""))[:500],"license_url":meta.get("LicenseUrl",{}).get("value","")})
        if len(found)>=limit:break
    return found
def narration_text(research):
    # Transparent: template-based outline, not fabricated investigation or LLM-written reporting.
    summary=research["summary"].replace("\n"," ")
    sentences=re.split(r"(?<=[.!?])\s+",summary)
    return ["Here is a documented story worth investigating."]+[s for s in sentences if len(s)>20][:6]+["Before publishing, check the original sources and the full context."]
def kokoro_voice(lines,out):
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np
    except ImportError as e: raise RuntimeError("Install: pip install kokoro soundfile; plus espeak-ng system package") from e
    pipeline=KPipeline(lang_code="a")
    samples=[]
    for line in lines:
        for _,_,audio in pipeline(line,voice="am_michael",speed=1.05):
            samples.append(audio)
    if not samples: raise RuntimeError("Kokoro produced no audio")
    sf.write(str(out),np.concatenate(samples),24000)
def duration_seconds(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)]).decode().strip())
def make_video(audio,assets,out):
    if not assets: raise RuntimeError("No license-filtered media found; provide approved images manually")
    duration=duration_seconds(audio); segment=duration/len(assets)
    clips=[]
    for i,a in enumerate(assets):
        p=out.parent/("shot_%02d.mp4"%i)
        vf="scale=1400:800:force_original_aspect_ratio=increase,crop=1400:800,zoompan=z='min(zoom+0.0009,1.15)':d=1:s=1280x720:fps=24,format=yuv420p"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",a["file"],"-t",str(segment+0.12),"-vf",vf,"-an","-c:v","libx264","-preset","ultrafast",str(p)],check=True)
        clips.append(p)
    listing=out.parent/"shots.txt"
    listing.write_text("".join("file '"+p.name+"'\n" for p in clips))
    silent=out.parent/"video_only.mp4"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing),"-c","copy",str(silent)],check=True)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-t",str(duration),"-c:v","copy","-c:a","aac","-movflags","+faststart",str(out)],check=True)
def main():
    p=argparse.ArgumentParser();p.add_argument("--topic",required=True);p.add_argument("--out",default="output/chaos_v2");p.add_argument("--approved-assets",default="")
    a=p.parse_args();root=Path(a.out).resolve();root.mkdir(parents=True,exist_ok=True)
    research=wiki_research(a.topic); (root/"research.json").write_text(json.dumps(research,indent=2))
    lines=narration_text(research);(root/"script.txt").write_text("\n".join(lines))
    if a.approved_assets:
        assets=[{"file":str(p.resolve()),"source":"user supplied - verify rights","license":"USER REVIEW REQUIRED","attribution":""} for p in Path(a.approved_assets).glob("*") if p.suffix.lower() in (".png",".jpg",".jpeg")]
    else: assets=commons_assets(a.topic,root/"assets")
    (root/"media_credits.json").write_text(json.dumps(assets,indent=2))
    if not assets: raise RuntimeError("No suitable Commons images found. Add your own approved images with --approved-assets")
    audio=root/"narration.wav";kokoro_voice(lines,audio)
    make_video(audio,assets,root/"video.mp4")
    print("DONE:",root/"video.mp4","\nReview research.json and media_credits.json before publishing")
if __name__=="__main__":main()
