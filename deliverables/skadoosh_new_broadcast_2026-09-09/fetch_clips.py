"""Fetch only requested public 720p VOD segments; preserve timing provenance."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import argparse, json, requests, subprocess, time

HERE=Path(__file__).resolve().parent
BASE='https://dgeft87wbj63p.cloudfront.net/51b661c9b1227bdf020a_skadoosh_c_316804162645_1788888412/720p60/'

def fetch(label,start,end):
    clips=HERE/'clips';clips.mkdir(exist_ok=True)
    dest=clips/(label+'.mp4')
    if dest.exists():return dest
    parts=[]; at=0.; duration=0.
    for line in (HERE/'video720.m3u8').read_text().splitlines():
        if line.startswith('#EXTINF:'): duration=float(line.split(':')[1].split(',')[0])
        elif line and not line.startswith('#'):
            if at<end and at+duration>start:parts.append((at,line))
            at+=duration
    assert parts and start>=0 and end<=at
    cache=HERE/'video_fragments';cache.mkdir(exist_ok=True)
    def get(pair):
        t,name=pair;target=cache/f'{t:09.3f}.ts'
        if not target.exists():
            for attempt in range(5):
                try:
                    r=requests.get(urljoin(BASE,name),timeout=40);r.raise_for_status();target.write_bytes(r.content);break
                except Exception:
                    if attempt==4:raise
                    time.sleep(attempt+1)
        return target
    paths=list(ThreadPoolExecutor(8).map(get,parts))
    concat=clips/(label+'.ts')
    with concat.open('wb') as f:
        for p in paths:f.write(p.read_bytes())
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(concat),'-ss',str(start-parts[0][0]),'-t',str(end-start),'-c:v','libx264','-preset','veryfast','-crf','20','-c:a','aac','-movflags','+faststart',str(dest)],check=True)
    (clips/(label+'.json')).write_text(json.dumps({'video_id':'2868822161','requested_start':start,'requested_end':end,'first_source_segment':parts[0][0],'source_segments':[x[1] for x in parts],'public_source':BASE+'index-dvr.m3u8'},indent=2),encoding='utf-8')
    print(label, start,end,flush=True)
    return dest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');p.add_argument('start',type=float);p.add_argument('end',type=float)
    a=p.parse_args();fetch(a.label,a.start,a.end)
