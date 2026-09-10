from pathlib import Path
import json,sys,requests
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parent
vid=sys.argv[1] if len(sys.argv)>1 else 'zKJQyBm4VnI'
d=json.loads((OUT/'sources'/f'{vid}.info.json').read_text(encoding='utf-8'))
results=[]
for fid in ['18','134','298','sb0']:
    f=next(f for f in d['formats'] if f['format_id']==fid)
    url=f['fragments'][0]['url'] if fid=='sb0' else f['url']
    try:
        r=requests.get(url,headers={**f.get('http_headers',{}),'Range':'bytes=0-1023'},timeout=20)
        row={'format':fid,'status':r.status_code,'bytes':len(r.content),'content_type':r.headers.get('Content-Type')}
        if fid=='sb0' and r.status_code==200:
            (OUT/'sources'/f'{vid}_storyboard0.jpg').write_bytes(r.content)
    except Exception as e: row={'format':fid,'error':str(e)}
    results.append(row);print(row,flush=True)
(OUT/'sources'/f'{vid}.media_access.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
