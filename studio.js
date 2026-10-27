"use strict";
const $=id=>document.getElementById(id);
const canvas=$("canvas"),ctx=canvas.getContext("2d");
const palettes={Psychology:["#101b2b","#45e2d4"],Science:["#0b1936","#68bcff"],Horror:["#1d101f","#ff617e"],Survival:["#13251e","#ffbd64"],History:["#302321","#f2ca8b"],Comedy:["#221936","#ff9adb"]};
const verbs=[["run",/\b(run|ran|running|escape|chase|flee|rushed)\b/i],["jump",/\b(jump|leap|fly|gravity)\b/i],["fight",/\b(fight|punch|battle|attack|hit)\b/i],["fall",/\b(fall|fell|collapse|crash|drop)\b/i],["fear",/\b(fear|scared|terrifying|shadow|monster|danger)\b/i],["think",/\b(think|thought|wonder|why|realize|remember|imagine)\b/i]];
function parseScript(raw){const text=raw.replace(/\s+/g," ").trim();if(!text)throw Error("Please paste a script.");
 const out=[];for(const sentence of text.split(/(?<=[.!?])\s+/)){let words=sentence.split(" ");while(words.length){out.push(words.splice(0,26).join(" "));}}
 if(out.length>500)throw Error("Maximum 500 scenes. Shorten your script.");return out.map((text,i)=>({text,action:(verbs.find(([,re])=>re.test(text))||["walk"])[0],i}));}
let playing=false,abort=false,recorder=null,raf=0;
function line(points,color,width){ctx.beginPath();ctx.moveTo(...points[0]);for(let i=1;i<points.length;i++)ctx.lineTo(...points[i]);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap="round";ctx.lineJoin="round";ctx.stroke();}
function draw(scene,t,duration,niche,captions){
 const w=canvas.width,h=canvas.height,unit=w/1280;
 const [bg,color]=palettes[niche];ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);
 const ground=h*.78;
 for(let i=0;i<14;i++){const x=((i*130-t*17*unit)%(w+200)+w+200)%(w+200)-100;const height=(125+(i*73)%140)*unit;ctx.fillStyle="#243248";ctx.fillRect(x,ground-height,78*unit,height);ctx.fillStyle="#344b60";for(let j=0;j<3;j++)ctx.fillRect(x+15*unit,ground-height+(30+j*27)*unit,9*unit,8*unit);}
 ctx.fillStyle="#152e48";ctx.beginPath();ctx.arc(w*.81,h*.19,70*unit,0,Math.PI*2);ctx.fill();
 line([[0,ground],[w,ground]],color,3*unit);
 // Scene-specific illustrated props and cinematic lighting (offline canvas)
 const mood=scene.i%5;
 ctx.save();ctx.globalAlpha=.18;ctx.fillStyle=color;
 if(mood===0){for(let k=0;k<5;k++){ctx.beginPath();ctx.arc(w*(.1+k*.2),h*.22,(22+k*7)*unit,0,Math.PI*2);ctx.fill();}}
 if(mood===1){for(let k=0;k<7;k++){let xx=(k*.16+.05)*w;ctx.fillRect(xx,ground-(180+k%3*70)*unit,12*unit,(180+k%3*70)*unit);}}
 if(mood===2){ctx.beginPath();ctx.ellipse(w*.73,h*.36,170*unit,95*unit,0,0,Math.PI*2);ctx.fill();}
 if(mood===3){for(let k=0;k<9;k++){let xx=w*(k/9);ctx.fillRect(xx,ground-35*unit,65*unit,35*unit);}}
 if(mood===4){for(let k=0;k<10;k++){ctx.beginPath();ctx.arc(w*(k*.11),h*(.12+(k%3)*.13),8*unit,0,Math.PI*2);ctx.fill();}}
 ctx.restore();
 const vignette=ctx.createRadialGradient(w/2,h/2,h*.1,w/2,h/2,w*.75);
 vignette.addColorStop(0,"#00000000");vignette.addColorStop(1,"#00000088");ctx.fillStyle=vignette;ctx.fillRect(0,0,w,h);
 const phase=t*(scene.action==="run"?14:scene.action==="walk"?8:6);
 const progress=Math.min(1,t/duration);
 const x=w*(scene.action==="run"||scene.action==="walk"?.19+.59*progress:.48);
 let y=ground-95*unit+Math.sin(phase)*4*unit;
 if(scene.action==="jump")y-=Math.abs(Math.sin(t*2.6))*135*unit;
 if(scene.action==="fall")y+=Math.min(1,t)*65*unit;
 const headY=y-135*unit;\n // Animated face reacts to the scene action
 ctx.strokeStyle=color;ctx.lineWidth=8*unit;ctx.beginPath();ctx.arc(x,headY,26*unit,0,Math.PI*2);ctx.stroke();
 ctx.fillStyle="#fff";for(const dx of [-10,10]){ctx.beginPath();ctx.arc(x+dx*unit,headY-3*unit,3.5*unit,0,Math.PI*2);ctx.fill();}
 if(scene.action==="fear"){ctx.beginPath();ctx.ellipse(x,headY+12*unit,6*unit,10*unit,0,0,Math.PI*2);ctx.stroke();}else if(scene.action==="think"){line([[x-9*unit,headY+12*unit],[x+9*unit,headY+10*unit]],color,2*unit);}else{ctx.beginPath();ctx.arc(x,headY+4*unit,12*unit,.15,Math.PI-.15);ctx.stroke();}\n const shoulder=headY+38*unit,hip=y-36*unit,swing=Math.sin(phase)*35*unit;
 line([[x,shoulder],[x,hip]],color,8*unit);
 if(scene.action==="fight"){line([[x,shoulder],[x+75*unit,shoulder-25*unit+swing/3]],color,8*unit);line([[x,shoulder],[x-35*unit,shoulder+35*unit]],color,8*unit);}
 else if(scene.action==="fear"){line([[x,shoulder],[x-45*unit,shoulder-45*unit]],color,8*unit);line([[x,shoulder],[x+45*unit,shoulder-45*unit]],color,8*unit);}
 else if(scene.action==="think"){line([[x,shoulder],[x+30*unit,headY+22*unit]],color,8*unit);line([[x,shoulder],[x-38*unit,shoulder+40*unit]],color,8*unit);}
 else{line([[x,shoulder],[x-38*unit,shoulder+46*unit+swing]],color,8*unit);line([[x,shoulder],[x+38*unit,shoulder+46*unit-swing]],color,8*unit);}
 line([[x,hip],[x-32*unit+swing,y+60*unit]],color,8*unit);
 line([[x,hip],[x+32*unit-swing,y+60*unit]],color,8*unit);
 ctx.fillStyle=color;ctx.font=`bold ${Math.round(23*unit)}px system-ui`;ctx.fillText(`${niche.toUpperCase()} / SCENE ${scene.i+1}`,45*unit,55*unit);
 if(captions){const words=scene.text.split(" ");const count=Math.max(1,Math.ceil(words.length*progress));const caption=words.slice(Math.max(0,count-9),count).join(" ");
 ctx.font=`bold ${Math.round(28*unit)}px system-ui`;const maxWidth=w-80*unit;let shown=caption;while(ctx.measureText(shown).width>maxWidth&&shown.length>4)shown=shown.slice(1);
 const tw=ctx.measureText(shown).width;ctx.fillStyle="#050b14";ctx.fillRect((w-tw)/2-15*unit,h*.87-34*unit,tw+30*unit,53*unit);ctx.fillStyle="#fff";ctx.fillText(shown,(w-tw)/2,h*.87);}
}
function settings(){const scenes=parseScript($("script").value),seconds=Number($("seconds").value),fps=Number($("fps").value);if(!(seconds>=2&&seconds<=15))throw Error("Scene duration must be 2–15 seconds.");return {scenes,seconds,fps,niche:$("niche").value,captions:$("captions").checked};}
function status(msg){$("status").textContent=msg;}
function controls(active){playing=active;$("preview").disabled=active;$("export").disabled=active;$("stop").disabled=!active;}
function stop(){abort=true;if(recorder&&recorder.state==="recording")recorder.stop();cancelAnimationFrame(raf);controls(false);status("Stopped.");}
$("stop").onclick=stop;
async function play(exporting){if(playing)return;let s;try{s=settings();}catch(e){status(e.message);return;}
 abort=false;const {scenes,seconds,fps,niche,captions}=s;const total=scenes.length*seconds;
 if(exporting){canvas.width=Number($("quality").value);canvas.height=Math.round(canvas.width*9/16);}else{canvas.width=1280;canvas.height=720;}
 let chunks=[],mime="",ext="webm";
 if(exporting){
 if(!canvas.captureStream||!window.MediaRecorder){status("This browser cannot record canvas video. Try Chrome on Android.");return;}
 const candidates=["video/mp4;codecs=avc1.42E01E","video/webm;codecs=vp9","video/webm;codecs=vp8","video/webm"];
 mime=candidates.find(x=>MediaRecorder.isTypeSupported(x))||"";
 if(!mime){status("No supported browser video recording format.");return;}
 ext=mime.startsWith("video/mp4")?"mp4":"webm";
 }
 controls(true);$("progress").value=0;
 let start=performance.now(),last=-1;
 if(exporting){
 const stream=canvas.captureStream(fps);
 try{recorder=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:canvas.width>=1920?8000000:4000000});}
 catch(e){controls(false);status("Recorder error: "+e.message);return;}
 recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};
 recorder.onstop=()=>{stream.getTracks().forEach(t=>t.stop());if(chunks.length){const blob=new Blob(chunks,{type:mime});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.className="download";a.href=url;a.download="stickverse-"+Date.now()+"."+ext;a.textContent="Download "+ext.toUpperCase()+" ("+(blob.size/1048576).toFixed(1)+" MB)";$("downloads").replaceChildren(a);status("Export ready. Tap Download. Format: "+ext.toUpperCase()+". Video has no audio.");}else status("Recording stopped without data.");};
 recorder.start(1000);
 }
 function tick(now){
 if(abort)return;
 const elapsed=Math.min(total,(now-start)/1000),index=Math.min(scenes.length-1,Math.floor(elapsed/seconds)),local=elapsed-index*seconds;
 if(!exporting||Math.floor(elapsed*fps)!==last){draw(scenes[index],local,seconds,niche,captions);last=Math.floor(elapsed*fps);}
 $("progress").value=elapsed/total*100;
 status((exporting?"Recording":"Previewing")+" scene "+(index+1)+"/"+scenes.length+" · "+Math.round(elapsed)+"/"+Math.round(total)+" sec. Keep tab visible.");
 if(elapsed>=total){controls(false);if(exporting&&recorder.state==="recording")recorder.stop();else status("Preview complete.");return;}
 raf=requestAnimationFrame(tick);
 }
 draw(scenes[0],0,seconds,niche,captions);raf=requestAnimationFrame(tick);
}
$("preview").onclick=()=>play(false);
$("export").onclick=()=>play(true);
draw({text:"Your animation starts here",action:"walk",i:0},0,4,"Psychology",true);

function estimateDuration(){try{const n=parseScript($("script").value).length;const mins=n*Number($("seconds").value)/60;$("estimate").textContent="Estimated silent video: "+mins.toFixed(1)+" min | "+n+" scenes. Target: 6-15 min. Narration not yet included.";}catch(e){$("estimate").textContent=e.message;}}
$("script").addEventListener("input",estimateDuration);$("seconds").addEventListener("input",estimateDuration);estimateDuration();
