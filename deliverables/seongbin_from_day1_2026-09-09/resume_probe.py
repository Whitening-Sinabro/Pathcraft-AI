from pathlib import Path
import concurrent.futures, json, sys, requests, datetime
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
d=json.loads((O/'sources/zKJQyBm4VnI.info.json').read_text(encoding='utf-8'))
def probe(fid):
    f=next(f for f in d['formats'] if f['format_id']==fid)
    row={'format':fid,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with requests.get(f['url'],headers={**f.get('http_headers',{}),'Range':'bytes=0-65535'},timeout=(10,15),stream=True) as r:
            row.update(status=r.status_code,headers={k:v for k,v in r.headers.items() if k.lower() in ['content-range','content-length','content-type','accept-ranges']})
            b=next(r.iter_content(65536),b'')
            row.update(bytes=len(b),signature=b[:16].hex())
    except requests.RequestException as e: row['error_type']=type(e).__name__
    print(json.dumps(row),flush=True)
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(probe,['134','298','299']))
(O/'sources/resume_media_probe.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
