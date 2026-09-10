from pathlib import Path
import json,requests,datetime,hashlib
O=Path(__file__).resolve().parent
for vid in ['39kHWKUhwhU','xnREtaV3m1A']:
    d=json.loads((O/'sources'/f'{vid}.info.json').read_text(encoding='utf8'))
    status={'video_id':vid,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        f=next(x for x in d['automatic_captions']['ko-orig'] if x['ext']=='json3')
        r=requests.get(f['url'],timeout=25);status.update(http_status=r.status_code,bytes=len(r.content));r.raise_for_status()
        raw=r.json();p=O/'sources'/f'{vid}.ko-orig.json3';p.write_bytes(r.content)
        rows=[{'start':e['tStartMs']/1000,'duration':e.get('dDurationMs',0)/1000,'text':''.join(x.get('utf8','') for x in e.get('segs',[])).strip()} for e in raw.get('events',[]) if e.get('segs')]
        data={'video_id':vid,'automatic':True,'source':str(p.relative_to(O)),'sha256':hashlib.sha256(r.content).hexdigest(),'segments':rows}
        (O/'transcripts'/f'{vid}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
        (O/'transcripts'/f'{vid}.txt').write_text('\n'.join(f"[{int(x['start'])//3600:02}:{int(x['start'])//60%60:02}:{int(x['start'])%60:02}] {x['text']}" for x in rows),encoding='utf8')
        status['segments']=len(rows)
    except Exception as e:status['error']=str(e)
    (O/'sources'/f'{vid}.caption_access.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    print(status,flush=True)
