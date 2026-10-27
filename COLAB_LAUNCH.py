"""One-cell Colab launcher: !python COLAB_LAUNCH.py"""
import os,secrets,subprocess,sys
from pathlib import Path
repo=Path("/content/stickverse-studio")
if not repo.exists():
    subprocess.run(["git","clone","https://github.com/miang20/stickverse-studio.git",str(repo)],check=True)
else:
    subprocess.run(["git","-C",str(repo),"pull","--ff-only"],check=True)
os.chdir(repo)
subprocess.run([sys.executable,"-m","pip","install","-q","-r","requirements.txt"],check=True)
subprocess.run([sys.executable,"-m","py_compile","engine.py","studio.py"],check=True)
password=secrets.token_urlsafe(12)
os.environ["STICKVERSE_PASSWORD"]=password
print("LOGIN USERNAME: studio")
print("LOGIN PASSWORD:",password)
print("Open the temporary gradio.live link below. Do not share the password.")
subprocess.run([sys.executable,"studio.py"],check=True)
