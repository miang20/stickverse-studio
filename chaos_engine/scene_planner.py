"""CHAOS ENGINE scene planner.
Maps factual script sentences to approved footage using transparent lexical scoring.
No fabricated footage or unsupported claims. All matches require editorial review.
"""
import argparse, json, re
from pathlib import Path

STOP={"the","a","an","of","to","and","or","is","are","was","were","in","on","at","with","for","this","that","it","from","as","by","be","have","has","had","you","they","their","into","about"}
def tokens(text):
    return {x for x in re.findall(r"[a-z0-9]+",str(text).lower()) if len(x)>2 and x not in STOP}

def score(sentence,asset):
    terms=tokens(sentence)
    description=" ".join(str(asset.get(k,"")) for k in ("title","description","tags","keywords","source"))
    matched=terms & tokens(description)
    return len(matched)/(max(1,len(terms))**0.5)

def plan(script,assets,seconds_per_word=0.37):
    if not assets:raise ValueError("No rights-reviewed assets supplied")
    for a in assets:
        if not a.get("approved",False):
            raise ValueError("Every asset must have approved=true after human rights review")
        if not a.get("path") or not Path(a["path"]).exists():
            raise FileNotFoundError(a.get("path","missing asset path"))
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+",script) if s.strip()]
    if not sentences:raise ValueError("Empty script")
    scenes=[];t=0.0
    for index,sentence in enumerate(sentences):
        duration=max(2.0,len(sentence.split())*seconds_per_word)
        ranked=sorted(assets,key=lambda a:score(sentence,a),reverse=True)
        chosen=ranked[0]
        confidence=score(sentence,chosen)
        scenes.append({"index":index,"start":round(t,2),"duration":round(duration,2),"narration":sentence,
                       "visual":chosen["path"],"source":chosen.get("source",""),"license":chosen.get("license",""),
                       "match_score":round(confidence,3),"review_required":confidence<0.5})
        t+=duration
    return {"duration_estimate":round(t,2),"scenes":scenes,"warning":"Lexical matching only; verify visuals, timing and facts before publishing"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--script",required=True);p.add_argument("--assets",required=True);p.add_argument("--out",default="shot_plan.json")
    args=p.parse_args()
    script=Path(args.script).read_text(encoding="utf-8")
    assets=json.loads(Path(args.assets).read_text(encoding="utf-8"))
    result=plan(script,assets)
    Path(args.out).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(f"Wrote {len(result['scenes'])} scenes to {args.out}")
if __name__=="__main__":main()
