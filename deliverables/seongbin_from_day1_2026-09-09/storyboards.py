from pathlib import Path
import json,requests,sys,concurrent.futures,math
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parent
vid=sys.argv[1]
d=json.loads((OUT/'sources'/f'{vid}.info.json').read_text(encoding='utf-8'))
f=next(x for x in d['formats'] if x['format_id']=='sb0')
folder=OUT/'storyboards'/vid;folder.mkdir(parents=True,exist_ok=True)
def fetch(pair):
    n,frag=pair;p=folder/f'{n:03}.jpg'
    if p.exists(): return
    try:
        r=requests.get(frag['url'],timeout=20);r.raise_for_status();p.write_bytes(r.content)
    except Exception as e:print(n,str(e)[:150],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:list(ex.map(fetch,enumerate(f['fragments'])))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
# YouTube storyboard interval is nominal 10 s; exact interval must be checked
# against original storyboard spec before using a tile as exact execution time.
def tile(sec):
    index=int(sec/10);sheet=index//9;cell=index%9
    p=folder/f'{sheet:03}.jpg'
    if not p.exists():return Image.new('RGB',(320,180),'gray')
    im=Image.open(p);return im.crop((cell%3*320,cell//3*180,cell%3*320+320,cell//3*180+180))
for start in range(0,int(d['duration']),1800):
    contact=Image.new('RGB',(1280,7*207),'white');draw=ImageDraw.Draw(contact)
    for n,sec in enumerate(range(start,min(start+1800,int(d['duration'])),70)):
        x=n%4*320;y=n//4*207;contact.paste(tile(sec),(x,y))
        draw.text((x+3,y+182),f'{vid} ~{sec//3600:02}:{sec//60%60:02}:{sec%60:02}',fill='black',font=font)
    contact.save(folder/f'survey_{start:05}.jpg',quality=92)
print(vid,'storyboards',len(list(folder.glob('[0-9]*.jpg'))),'surveys',len(list(folder.glob('survey*'))),flush=True)
