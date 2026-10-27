"use strict";
const $=id=>document.getElementById(id),c=$("canvas"),g=c.getContext("2d");let pics=[],urls=[],busy=false,stopFlag=false,rec=null,raf=0,trackAudio=null;
function msg(s){$("status").textContent=s}
function estimate(){const n=pics.length,seconds=Number($("seconds").value)||8;$("estimate").textContent=n?n+" images × "+seconds+" seconds = "+(n*seconds/60).toFixed(1)+" min. Images repeat if audio runs longer.":"Upload images to estimate duration."}
$("images").onchange=async e=>{urls.forEach(URL.revokeObjectURL);urls=[];pics=[];for(const f of [...e.target.files].slice(0,150)){const url=URL.createObjectURL(f);urls.push(url);const im=new Image();try{await new Promise((res,rej)=>{im.onload=res;im.onerror=rej;im.src=url});pics.push(im)}catch{}}estimate();if(pics.length)draw(0)};
$("seconds").oninput=estimate;
function draw(t){const w=c.width,h=c.height;g.fillStyle="#050a11";g.fillRect(0,0,w,h);if(!pics.length){g.fillStyle="white";g.font="bold 36px sans-serif";g.fillText("Upload cinematic photos to begin",60,h/2);return}
const secs=Number($("seconds").value)||8,i=Math.floor(t/secs)%pics.length,progress=(t%secs)/secs,im=pics[i],zoom=1.04+progress*.12;
const scale=Math.max(w/im.width,h/im.height)*zoom,iw=im.width*scale,ih=im.height*scale;
const drift=(progress-.5)*w*.06;g.drawImage(im,(w-iw)/2+drift,(h-ih)/2,iw,ih);
const shade=g.createLinearGradient(0,0,0,h);shade.addColorStop(0,"#0009");shade.addColorStop(.5,"#0000");shade.addColorStop(1,"#000c");g.fillStyle=shade;g.fillRect(0,0,w,h);
g.fillStyle="white";g.font="bold "+Math.round(w*.023)+"px system-ui";g.fillText($("channel").value.toUpperCase(),w*.045,h*.09);
g.font="bold "+Math.round(w*.03)+"px system-ui";const title=$("title").value.slice(0,58);g.fillText(title,w*.045,h*.9,w*.9)}
function toggle(b){busy=b;$("preview").disabled=b;$("export").disabled=b;$("stop").disabled=!b}
$("stop").onclick=()=>{stopFlag=true;cancelAnimationFrame(raf);if(rec&&rec.state==="recording")rec.stop();if(trackAudio){trackAudio.pause();trackAudio.currentTime=0}toggle(false);msg("Stopped.")};
async function run(exporting){if(busy)return;if(!pics.length){msg("First upload realistic photos.");return}const seconds=Number($("seconds").value);if(!Number.isFinite(seconds)||seconds<3||seconds>30){msg("Seconds per image must be 3-30.");return}
const audioFile=$("audio").files[0];let duration=pics.length*seconds;let audio=null,stream=null,context=null;
if(audioFile){audio=new Audio(URL.createObjectURL(audioFile));audio.preload="auto";try{await new Promise((resolve,reject)=>{audio.onloadedmetadata=resolve;audio.onerror=reject;setTimeout(()=>reject(Error("Audio load timeout")),12000)});if(Number.isFinite(audio.duration)&&audio.duration>0)duration=audio.duration}catch(e){msg("Could not load audio: "+e.message);return}}
stopFlag=false;toggle(true);c.width=Number($("quality").value);c.height=Math.round(c.width*9/16);draw(0);
let mime="",chunks=[];if(exporting){if(!c.captureStream||!window.MediaRecorder){toggle(false);msg("Browser recording unavailable.");return}
mime=["video/mp4;codecs=avc1.42E01E","video/webm;codecs=vp8","video/webm"].find(v=>MediaRecorder.isTypeSupported(v));if(!mime){toggle(false);msg("No supported video format.");return}
stream=c.captureStream(24);
if(audio){try{context=new (window.AudioContext||window.webkitAudioContext)();const src=context.createMediaElementSource(audio),dest=context.createMediaStreamDestination();src.connect(dest);src.connect(context.destination);dest.stream.getAudioTracks().forEach(t=>stream.addTrack(t));await context.resume()}catch(e){msg("Audio capture failed: "+e.message);toggle(false);return}}
try{rec=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:2600000});rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};rec.onstop=()=>{stream.getTracks().forEach(t=>t.stop());if(context)context.close();if(chunks.length){const blob=new Blob(chunks,{type:mime}),u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download="cinematic-"+Date.now()+"."+(mime.startsWith("video/mp4")?"mp4":"webm");a.textContent="Download video ("+(blob.size/1048576).toFixed(1)+" MB)";a.className="btn";$("downloads").replaceChildren(a);msg("Recording ready. Tap Download.")}else msg("No recording data. Try shorter 360p video.")};rec.start(1000)}catch(e){toggle(false);msg("Recorder error: "+e.message);return}}
const start=performance.now();if(audio){try{await audio.play();trackAudio=audio}catch(e){if(rec&&rec.state==="recording")rec.stop();toggle(false);msg("Audio playback blocked: "+e.message);return}}
function tick(now){if(stopFlag)return;const t=Math.min(duration,(now-start)/1000);draw(t);$("progress").value=100*t/duration;msg((exporting?"Recording":"Previewing")+" "+Math.round(t)+"/"+Math.round(duration)+" seconds. Keep browser open.");if(t>=duration){toggle(false);if(audio)audio.pause();if(exporting&&rec.state==="recording")rec.stop();else msg("Preview finished.");return}raf=requestAnimationFrame(tick)}raf=requestAnimationFrame(tick)}
$("preview").onclick=()=>run(false);$("export").onclick=()=>run(true);draw(0);
