import json, subprocess, shutil, re, argparse
from pathlib import Path

def stamp(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02},{ms%1000:03}'

def render(manifest_path, output):
    if not shutil.which('ffmpeg'): raise RuntimeError('FFmpeg required')
    manifest=json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    scenes=manifest['scenes']
    if not scenes: raise ValueError('No scenes')
    out=Path(output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    work=out.parent / 'chaos_segments'; work.mkdir(exist_ok=True)
    parts=[]
    for i,s in enumerate(scenes):
        duration=float(s.get('duration',4))
        if not 0.5<=duration<=120: raise ValueError('Invalid duration')
        color=s.get('color','0x101522')
        if not re.fullmatch(r'0x[0-9a-fA-F]{6}',color): raise ValueError('Invalid color')
        subtitle=work/f'scene_{i:03}.srt'
        title=str(s.get('text',''))[:180].replace('\n',' ')
        subtitle.write_text(f'1\n{stamp(0)} --> {stamp(duration)}\n{title}\n',encoding='utf-8')
        clip=work/f'scene_{i:03}.mp4'
        vf=f"subtitles={subtitle.name}:force_style='FontSize=27,Alignment=5,Outline=2'"
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'color=c={color}:s=1280x720:r=24','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',str(duration),'-vf',vf,'-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(clip)]
        subprocess.run(cmd,cwd=work,check=True)
        parts.append(clip)
    concat=work/'concat.txt';concat.write_text(''.join(f"file '{p.name}'\n" for p in parts))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat.name,'-c','copy',str(out)],cwd=work,check=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output',default='output/chaos_preview.mp4');a=p.parse_args();print(render(a.manifest,a.output))
