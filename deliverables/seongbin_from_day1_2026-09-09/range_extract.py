"""Download exact DASH sidx segments for a requested VOD interval, preserving source timing."""
from pathlib import Path
import json, struct, sys, requests, subprocess, datetime, hashlib
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
vid=sys.argv[1]; start=float(sys.argv[2]); duration=float(sys.argv[3]); fid=sys.argv[4] if len(sys.argv)>4 else '299'
source=O/'sources'/f'{vid}.resume.info.json'
if not source.exists(): source=O/'sources'/f'{vid}.info.json'
info=json.loads(source.read_text(encoding='utf-8'))
fmt=next(f for f in info['formats'] if f['format_id']==fid)
session=requests.Session()
def fetch(a,b):
    r=session.get(fmt['url'],headers={**fmt.get('http_headers',{}),'Range':f'bytes={a}-{b}'},timeout=(15,35))
    if r.status_code!=206: raise RuntimeError(f'Media HTTP {r.status_code} for byte interval {a}-{b}')
    expected=f'bytes {a}-{b}/'
    if not r.headers.get('Content-Range','').startswith(expected) or len(r.content)!=b-a+1:
        raise RuntimeError(f"Wrong range: requested {a}-{b}, received {r.headers.get('Content-Range')} length {len(r.content)}")
    return r.content
head=fetch(0,1048575)
pos=0; refs=[]; init_end=None
while pos+8<=len(head):
    size,kind=struct.unpack_from('>I4s',head,pos)
    if size==1: size=struct.unpack_from('>Q',head,pos+8)[0]
    print('atom',pos,size,kind.decode(errors='replace'),flush=True)
    if kind==b'sidx':
        version=head[pos+8]; timescale=struct.unpack_from('>I',head,pos+16)[0]
        q=pos+20
        if version==0: earliest,offset=struct.unpack_from('>II',head,q);q+=8
        else: earliest,offset=struct.unpack_from('>QQ',head,q);q+=16
        count=struct.unpack_from('>H',head,q+2)[0];q+=4
        bytepos=pos+size+offset; t=earliest/timescale;init_end=pos
        for n in range(count):
            length,dur,sap=struct.unpack_from('>III',head,q);q+=12
            if length>>31:raise RuntimeError('Nested sidx unsupported')
            refs.append({'offset':bytepos,'size':length,'start':t,'duration':dur/timescale})
            bytepos+=length;t+=dur/timescale
        break
    if size<8:raise RuntimeError('Invalid atom size')
    pos+=size
if not refs:raise RuntimeError('No complete sidx in first MiB')
selected=[r for r in refs if r['start']+r['duration']>start and r['start']<start+duration]
if not selected:raise RuntimeError('No matching segments')
folder=O/'media';folder.mkdir(exist_ok=True)
dest=folder/f'{vid}_{int(start):05}_{int(duration):03}_{fid}.mp4'
raw=dest.with_suffix('.dash.mp4')
with raw.open('wb') as f:
    f.write(head[:init_end])
    for r in selected:
        f.write(fetch(r['offset'],r['offset']+r['size']-1))
        print('segment',r['start'],r['size'],flush=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-map','0:v:0','-c','copy','-avoid_negative_ts','make_zero',str(dest)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)],text=True))
receipt={'video_id':vid,'requested_start':start,'requested_duration':duration,'source_start':selected[0]['start'],'source_end':selected[-1]['start']+selected[-1]['duration'],'format_id':fid,'segments':selected,'file':dest.relative_to(O).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'probe':probe,'audio':False}
dest.with_suffix('.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('SAVED',dest,flush=True)
