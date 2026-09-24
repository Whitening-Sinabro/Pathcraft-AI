"""Retrieve public VOD intervals and render timestamped inspection frames."""
from pathlib import Path
import argparse, concurrent.futures, datetime, json, subprocess
import cv2
from PIL import Image, ImageDraw, ImageFont
import yt_dlp

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / 'skadoosh_hc_2026-09-07/broadcast_audit'
PLANS = {
    'cry_transition': ('2866065347', 15660, 900),
    'awt_transition': ('2866749730', 1620, 1800),
    'paquate_transition': ('2866749730', 14040, 840),
    'late_weapon': ('2866749730', 22440, 240),
    'third_ascendancy': ('2866749730', 25260, 210),
}


def stamp(t):
    return f'{int(t)//3600:02}:{int(t)//60%60:02}:{t%60:04.1f}'


def download():
    sources = {}
    for vod in sorted({x[0] for x in PLANS.values()}):
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info('https://www.twitch.tv/videos/' + vod, download=False)
        choice = max((f for f in info['formats'] if f.get('height') == 720), key=lambda f: f.get('fps') or 0)
        sources[vod] = choice['url']
        print('Public source resolved', vod, choice['format_id'], flush=True)
    records = []
    def one(item):
        name, (vod, start, duration) = item
        target = HERE / (name + '.mp4')
        if not target.exists():
            p = subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
                '-ss',str(start),'-i',sources[vod],'-t',str(duration),'-c','copy',str(target)], capture_output=True)
            if p.returncode:
                # Avoid printing signed media URLs on error.
                raise RuntimeError(f'ffmpeg download failed for {name}, code {p.returncode}')
        cap = cv2.VideoCapture(str(target)); actual = cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS); cap.release()
        assert abs(actual-duration) < 12, (name, actual, duration)
        row = {'name':name,'vod':vod,'start':start,'duration':duration,'actual_duration':actual,'path':str(target),'bytes':target.stat().st_size}
        print('Downloaded', name, round(actual, 2), 'seconds', flush=True)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(one, PLANS.items()))
    (HERE/'media_coverage.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def boards(name, start, duration, step, crop, explicit_file=None, explicit_origin=0):
    if explicit_file:
        vod = name; origin = explicit_origin; path = Path(explicit_file)
    elif name in PLANS and (HERE/(name+'.mp4')).exists():
        vod, origin, _ = PLANS[name]; path = HERE/(name+'.mp4')
    else:
        vod = name; origin = 0; path = OLD/vod/'video.mp4'
    cap = cv2.VideoCapture(str(path)); assert cap.isOpened(), str(path)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    total = round(duration/step); paths=[]
    for i in range(0,total,8):
        out=Image.new('RGB',(1440,880 if crop=='full' else 1240),'#101820');d=ImageDraw.Draw(out)
        for j in range(min(8,total-i)):
            t=start+(i+j)*step;cap.set(cv2.CAP_PROP_POS_MSEC,(t-origin)*1000);ok,f=cap.read();assert ok,(path,t)
            im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));w,h=im.size
            if crop=='skills':im=im.crop((w*.49,0,w,h*.94))
            elif crop=='left':im=im.crop((0,0,w*.5,h*.94))
            elif crop=='bar':im=im.crop((w*.66,h*.73,w,h))
            iw,ih=(720,405) if crop=='full' else (360,570)
            cols=2 if crop=='full' else 4; x=(j%cols)*iw;y=(j//cols)*(440 if crop=='full' else 620)
            # Full-frame boards use four rows.
            if crop=='full' and j==0 and out.height<1760:
                out=Image.new('RGB',(1440,1760),'#101820');d=ImageDraw.Draw(out)
            im.thumbnail((iw,ih));out.paste(im,(x,y+30));d.text((x+8,y+4),stamp(t),font=font,fill='white')
        p=HERE/f'{name}_{crop}_{int(start)}_{i//8:02}.jpg';out.save(p,quality=90);paths.append(p.name)
    cap.release()
    print(json.dumps({'vod':vod,'source':str(path),'start':start,'duration':duration,'step':step,'frames':total,'boards':paths},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['download','boards']);p.add_argument('--name');p.add_argument('--start',type=float);p.add_argument('--duration',type=float);p.add_argument('--step',type=float,default=10);p.add_argument('--crop',choices=['full','skills','left','bar'],default='full');p.add_argument('--file');p.add_argument('--origin',type=float,default=0);a=p.parse_args()
    download() if a.action=='download' else boards(a.name,a.start,a.duration,a.step,a.crop,a.file,a.origin)
