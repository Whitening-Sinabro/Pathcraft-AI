"""Bounded 37–52 minute purchase audit from the saved public VOD sources."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import argparse, json, subprocess, sys, time

HERE = Path(__file__).resolve().parent
VOD = HERE.parent
ROOT = VOD.parents[1]
JOBS = [('purchase_37_42', 2220, 2520), ('purchase_42_47', 2520, 2820), ('purchase_47_52', 2820, 3120)]

def asr():
    sys.path.insert(0, str(ROOT / 'deliverables/skadoosh_hc_2026-09-07/broadcast_audit'))
    import transcribe_broadcasts as common
    import soundfile as sf
    from faster_whisper import WhisperModel
    model = WhisperModel(str(ROOT / '.tmp/skadoosh-broadcast-asr/verification-model'), device='cuda', compute_type='int8_float16', cpu_threads=4)
    for label, start, end in JOBS:
        target = HERE / (label + '_asr.json')
        if target.exists():
            data = json.loads(target.read_text(encoding='utf-8'))
        else:
            with sf.SoundFile(VOD / 'audio.flac') as f:
                f.seek((start-5)*16000)
                wave = f.read((end-start+10)*16000, dtype='float32')
            segments, info = model.transcribe(wave, language='en', beam_size=5, temperature=0, vad_filter=False, condition_on_previous_text=False, word_timestamps=True)
            data = {'model': 'large-v3', 'interval': [start-5,end+5], 'automatic_transcription': True, 'segments': [{'start':start-5+s.start,'end':start-5+s.end,'text':s.text.strip()} for s in segments]}
            target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        (HERE / (label + '_asr.txt')).write_text('\n'.join(f'[{common.stamp(s["start"])}] {s["text"]}' for s in data['segments']), encoding='utf-8')
        print('asr', label, 'complete', flush=True)

def video():
    import requests
    base='https://dgeft87wbj63p.cloudfront.net/51b661c9b1227bdf020a_skadoosh_c_316804162645_1788888412/720p60/'
    segments=[];at=0;duration=0
    for line in (VOD/'video720.m3u8').read_text().splitlines():
        if line.startswith('#EXTINF:'):duration=float(line.split(':')[1].split(',')[0])
        elif line and not line.startswith('#'):
            segments.append((at,duration,line));at+=duration
    cache=VOD/'video_fragments';cache.mkdir(exist_ok=True)
    def download(row):
        start,duration,name=row;p=cache/f'{start:09.3f}.ts'
        if not p.exists():
            for attempt in range(4):
                try:
                    r=requests.get(urljoin(base,name),timeout=35);r.raise_for_status();p.write_bytes(r.content);break
                except Exception:
                    if attempt==3:raise
                    time.sleep(attempt+1)
        return p
    for label,start,end in JOBS:
        dest=HERE/(label+'.mp4');meta=HERE/(label+'.json')
        if dest.exists() and meta.exists():continue
        selected=[s for s in segments if s[0]<end and s[0]+s[1]>start]
        with ThreadPoolExecutor(8) as pool:paths=list(pool.map(download,selected))
        joined=HERE/(label+'.ts')
        with joined.open('wb') as f:
            for p in paths:f.write(p.read_bytes())
        temporary=HERE/(label+'.partial.mp4')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(joined),'-ss',str(start-selected[0][0]),'-t',str(end-start),'-vf','fps=30','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-c:a','aac','-movflags','+faststart',str(temporary)],check=True)
        temporary.replace(dest)
        meta.write_text(json.dumps({'video_id':'2868822161','requested_start':start,'requested_end':end,'first_source_segment':selected[0][0],'source_segments':[s[2] for s in selected],'public_source':base+'index-dvr.m3u8'},indent=2),encoding='utf-8')
        print('video',label,'complete',flush=True)

def frames():
    import cv2
    from PIL import Image,ImageDraw
    out=HERE/'frames';out.mkdir(exist_ok=True)
    for label,start,end in JOBS:
        cap=cv2.VideoCapture(str(HERE/(label+'.mp4')))
        shots=[]
        for second in range(start,end,10):
            cap.set(cv2.CAP_PROP_POS_MSEC,(second-start)*1000);ok,f=cap.read();assert ok,(label,second)
            im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB));im.save(out/f'vod_{second}.jpg');shots.append((second,im))
        cap.release()
        for page in range(3):
            board=Image.new('RGB',(1280,385*5),(12,18,25));draw=ImageDraw.Draw(board)
            for i,(second,im) in enumerate(shots[page*10:(page+1)*10]):
                im.thumbnail((640,360));x=i%2*640;y=i//2*385;board.paste(im,(x,y+25));draw.text((x+8,y+4),f'{second//3600:02}:{second//60%60:02}:{second%60:02}',fill='white')
            board.save(out/f'{label}_contact_{page}.jpg')
        print('frames',label,'complete',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['asr','video','frames']);a=p.parse_args();globals()[a.mode]()
