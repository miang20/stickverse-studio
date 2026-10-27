"""Android-friendly Gradio interface for STICKVERSE."""
import asyncio, os, tempfile, subprocess
from pathlib import Path
import gradio as gr
from engine import render_video, plan, split_script

EXAMPLE="The last human walked through an abandoned city. He wondered why everyone had vanished. Suddenly, a dark shadow appeared behind him. Terrified, he started to run. He jumped over a broken bridge. Then he realized the shadow was his own reflection."
NICHES=["Psychology","Science","Horror","Survival","History","Comedy"]
VOICES={"American Male":"en-US-GuyNeural","American Female":"en-US-JennyNeural","British Male":"en-GB-RyanNeural"}

async def synthesize(text,voice,path):
    import edge_tts
    await edge_tts.Communicate(text,VOICES[voice]).save(path)

def generate(script,niche,resolution,scene_seconds,voice,subtitles,progress=gr.Progress()):
    if not script or len(script.strip())<20:raise gr.Error("Enter at least 20 characters of script.")
    if len(split_script(script))>100:raise gr.Error("Please shorten the script to 100 scenes.")
    folder=Path(tempfile.mkdtemp(prefix="stickverse_"))
    audio=None
    # Edge TTS is a free online service and requires network access.
    if voice!="No narration":
        audio=str(folder/"voice.mp3")
        try:asyncio.run(synthesize(script,voice,audio))
        except Exception as exc:raise gr.Error("Narration failed (internet/Edge TTS): "+str(exc)[:180])
    output=str(folder/"stickverse.mp4")
    try:render_video(script,output,niche,resolution,float(scene_seconds),subtitles,audio,progress)
    except Exception as exc:raise gr.Error("Rendering failed: "+str(exc)[:250])
    return output,str(folder/"stickverse.json"),f"Rendered {len(split_script(script))} animated scenes. Note: scene timing is fixed; narration may end early or be cut short."
with gr.Blocks(title="STICKVERSE STUDIO",theme=gr.themes.Soft()) as demo:
    gr.Markdown("# STICKVERSE STUDIO\n**Script → Moving stickman scenes → MP4** | No NotebookLM · No paid video API")
    script=gr.Textbox(label="English story / narration",value=EXAMPLE,lines=8)
    with gr.Row():
        niche=gr.Dropdown(NICHES,value="Psychology",label="Niche")
        resolution=gr.Dropdown(["720p","1080p"],value="720p",label="Resolution")
    with gr.Row():
        duration=gr.Slider(2,12,value=4,step=1,label="Seconds per scene")
        voice=gr.Dropdown(["No narration",*VOICES],value="American Male",label="Narration")
        captions=gr.Checkbox(value=True,label="Dynamic captions")
    run=gr.Button("Generate Animated MP4",variant="primary")
    result=gr.Video(label="Generated video")
    scene_file=gr.File(label="Scene plan JSON")
    status=gr.Textbox(label="Render status")
    run.click(generate,[script,niche,resolution,duration,voice,captions],[result,scene_file,status])
if __name__=="__main__":
    # Colab's share link is temporary. Keep credentials out of GitHub.
    pwd=os.environ.get("STICKVERSE_PASSWORD")
    demo.queue().launch(server_name="0.0.0.0",share=True,auth=("studio",pwd) if pwd else None,show_error=True)
