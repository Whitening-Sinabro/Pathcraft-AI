"""Timestamped source frames for broadcast audit; no game interaction."""
from pathlib import Path
import argparse, json, subprocess
import cv2
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--times',type=float,nargs='+');p.add_argument('--scan',action='store_true');p.add_argument('--hd',action='store_true');a=p.parse_args()
folder=HERE/a.video;out=folder/'frames';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
def stamp(t):
    s=int(t);return f'{s//3600:02}:{s//60%60:02}:{s%60:02}'
if a.hd:
    import yt_dlp
    with yt_dlp.YoutubeDL({'quiet':True,'no_warnings':True,'format':'best[height=1080]/best'}) as ydl:
        info=ydl.extract_info('https://www.twitch.tv/videos/'+a.video,download=False)
    for t in a.times:
        dest=out/f'hd_{int(t):06}.jpg'
        if not dest.exists():
            subprocess.run(['ffmpeg','-v','error','-nostdin','-ss',str(t),'-i',info['url'],'-frames:v','1','-q:v','2',str(dest)],check=True)
        print(str(dest),flush=True)
else:
    capture=cv2.VideoCapture(str(folder/'video.mp4'))
    duration=capture.get(cv2.CAP_PROP_FRAME_COUNT)/capture.get(cv2.CAP_PROP_FPS)
    times=list(range(0,int(duration),30)) if a.scan else a.times
    cells=[];index=[]
    for t in times:
        capture.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=capture.read()
        assert ok,(a.video,t,'frame unavailable')
        image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        file=out/f'{int(t):06}.jpg';image.save(file,quality=88)
        index.append({'seconds':t,'file':str(file)})
        cell=Image.new('RGB',(384,240),'#151515');image.thumbnail((384,216));cell.paste(image,(0,0))
        ImageDraw.Draw(cell).text((6,217),stamp(t),fill='white',font=font);cells.append(cell)
    for start in range(0,len(cells),25):
        group=cells[start:start+25];sheet=Image.new('RGB',(1920,240*((len(group)+4)//5)),'#151515')
        for i,c in enumerate(group):sheet.paste(c,(384*(i%5),240*(i//5)))
        file=out/f'board_{int(times[start]):06}.jpg';sheet.save(file,quality=92);print(str(file),flush=True)
    (out/('index_scan.json' if a.scan else 'index_selected.json')).write_text(json.dumps(index,indent=2),encoding='utf-8')
    capture.release()
