"""Licensed moving video asset discovery via Wikimedia Commons.
Downloads only candidate video files with permissive license metadata.
All files and rights must be manually reviewed before publication.
"""
import json, re, urllib.parse, urllib.request
from pathlib import Path
from html import unescape

def query_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"ChaosEngine/0.3 (prototype research client)"})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.load(response)

def clean(value):
    return unescape(re.sub(r"<[^>]+>","",value or "")).strip()

def discover(query, destination, max_results=4):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    url=("https://commons.wikimedia.org/w/api.php?action=query&generator=search"
         "&gsrsearch="+urllib.parse.quote(query+" filetype:video")
         +"&gsrnamespace=6&gsrlimit=30&prop=imageinfo&iiprop=url|extmetadata&format=json")
    pages=query_json(url).get("query",{}).get("pages",{})
    results=[]
    for page in pages.values():
        info=(page.get("imageinfo") or [{}])[0]
        metadata=info.get("extmetadata",{})
        license_name=clean(metadata.get("LicenseShortName",{}).get("value",""))
        if not any(v in license_name.lower() for v in ("cc by","cc0","public domain")):continue
        original=info.get("url","")
        if not re.search(r"\.(webm|ogv|ogg)(?:\?|$)",original,re.I):continue
        ext=original.split("?")[0].rsplit(".",1)[-1].lower()
        path=destination/f"clip_{len(results):02}.{ext}"
        try:
            req=urllib.request.Request(original,headers={"User-Agent":"ChaosEngine/0.3"})
            with urllib.request.urlopen(req,timeout=90) as response, path.open("wb") as output:
                total=0
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    total+=len(block)
                    if total>80*1024*1024:raise ValueError("Video exceeds 80 MB safety limit")
                    output.write(block)
        except Exception:
            path.unlink(missing_ok=True);continue
        results.append({"path":str(path),"source":info.get("descriptionurl",""),"license":license_name,
                        "license_url":clean(metadata.get("LicenseUrl",{}).get("value","")),
                        "author":clean(metadata.get("Artist",{}).get("value",""))[:500],
                        "review_required":True})
        if len(results)>=max_results:break
    (destination/"video_licenses.json").write_text(json.dumps(results,indent=2))
    return results

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("query");p.add_argument("--out",default="output/licensed_clips")
    args=p.parse_args()
    print(json.dumps(discover(args.query,args.out),indent=2))
