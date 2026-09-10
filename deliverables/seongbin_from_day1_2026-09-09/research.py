from pathlib import Path
import json, sys, datetime, hashlib, concurrent.futures
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
IDS=['zKJQyBm4VnI','GtC5-b4QXec','C_tkSubXWDk','i6_tfxyQfeQ']
def metadata(vid):
    import yt_dlp
    try:
        with yt_dlp.YoutubeDL({'quiet':True,'skip_download':True,'socket_timeout':25,'retries':1,'js_runtimes':{'node':{}}}) as y:
            d=y.extract_info('https://www.youtube.com/watch?v='+vid,download=False)
        save(OUT/'sources'/f'{vid}.info.json',d)
        keys=['id','title','channel','channel_id','channel_url','uploader_id','upload_date','timestamp','release_timestamp','duration','was_live','live_status','description','webpage_url']
        result={k:d.get(k) for k in keys}
        result['retrieved_utc']=now()
        save(OUT/'sources'/f'{vid}.metadata.json',result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    except Exception as e:
        save(OUT/'sources'/f'{vid}.error.json',{'retrieved_utc':now(),'error':str(e)})
        print(vid,str(e),flush=True)
def index():
    for vid in IDS:
        p=ROOT/'data/_cache/subs'/f'seongbin_{vid}.ko-orig.json3'
        d=json.loads(p.read_text(encoding='utf-8'))
        rows=[]
        for e in d.get('events',[]):
            txt=''.join(s.get('utf8','') for s in e.get('segs',[])).strip()
            if txt: rows.append({'start':e['tStartMs']/1000,'duration':e.get('dDurationMs',0)/1000,'text':txt})
        save(OUT/'transcripts'/f'{vid}.json',{'video_id':vid,'automatic':True,'source':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'segments':rows})
        (OUT/'transcripts'/f'{vid}.txt').write_text('\n'.join(f"[{int(r['start'])//3600:02}:{int(r['start'])//60%60:02}:{int(r['start'])%60:02}] {r['text']}" for r in rows),encoding='utf-8')
        print(vid,len(rows),rows[:6],rows[-3:])
if __name__=='__main__':
    if sys.argv[1]=='metadata':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: list(ex.map(metadata,IDS))
    elif sys.argv[1]=='index': index()
    elif sys.argv[1]=='channel':
        import yt_dlp
        with yt_dlp.YoutubeDL({'quiet':True,'extract_flat':True,'playlistend':60,'socket_timeout':25}) as y:
            d=y.extract_info('https://www.youtube.com/channel/UCvj_myZNbqdHBBFT2IjKJWw/streams',download=False)
        save(OUT/'sources/channel_streams.json',d)
        for e in d.get('entries',[]): print(json.dumps({k:e.get(k) for k in ['id','title','duration','release_timestamp','timestamp','url']},ensure_ascii=False))
    elif sys.argv[1]=='summary':
        for p in sorted((OUT/'sources').glob('*.metadata.json')):
            d=json.loads(p.read_text(encoding='utf-8'))
            print(d['id'],d['title'],d['duration'])
            for k in ['release_timestamp','timestamp']:
                if d[k]: print(k,datetime.datetime.fromtimestamp(d[k],datetime.timezone(datetime.timedelta(hours=9))).isoformat())
            info=json.loads(p.with_name(d['id']+'.info.json').read_text(encoding='utf-8'))
            print([(f['format_id'],f.get('height'),f.get('protocol'),f.get('filesize') or f.get('filesize_approx')) for f in info['formats']])
    elif sys.argv[1]=='extra':
        for vid in ['39kHWKUhwhU','xnREtaV3m1A','rsKbeELo0TM']: metadata(vid)
    elif sys.argv[1]=='frame':
        import subprocess
        vid=sys.argv[2]; secs=list(map(float,sys.argv[3].split(',')))
        d=json.loads((OUT/'sources'/f'{vid}.info.json').read_text(encoding='utf-8'))
        fmt=next(f for f in d['formats'] if f['format_id']=='298')
        folder=OUT/'frames'/vid; folder.mkdir(parents=True,exist_ok=True)
        for sec in secs:
            dest=folder/f'{sec:09.2f}.jpg'
            if dest.exists(): continue
            headers=''.join(f'{k}: {v}\r\n' for k,v in fmt.get('http_headers',{}).items())
            r=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-headers',headers,'-ss',str(sec),'-i',fmt['url'],'-frames:v','1','-q:v','2',str(dest)],capture_output=True,timeout=55)
            print(vid,sec,r.returncode,'captured' if r.returncode==0 else 'media request failed',flush=True)
    elif sys.argv[1]=='fetch_character':
        sys.path.insert(0,str(ROOT/'scripts'))
        from track_poe2_character import fetch,decode_pob
        stamp=now(); p=OUT/'sources'/'character_20260909'
        try:
            d=fetch('dtq03087-0345','임성빈_화염파_젬링','hc-forbidden-rites')
            save(p.with_suffix('.json'),d)
            save(OUT/'sources/character_retrieval.json',{'retrieved_utc':stamp,'data_updated_utc':d.get('updatedUtc'),'level':d.get('level'),'status':'public_snapshot_not_proof_of_current_survival'})
            if d.get('pathOfBuildingExport'): p.with_suffix('.xml').write_text(decode_pob(d['pathOfBuildingExport']),encoding='utf-8')
            print({k:d.get(k) for k in ['name','level','updatedUtc','league']})
        except Exception as e: save(OUT/'sources/character_retrieval.json',{'retrieved_utc':stamp,'error':str(e)})
    elif sys.argv[1]=='watch_raw':
        import requests,re
        for vid in IDS:
            s=requests.get('https://www.youtube.com/watch?v='+vid,timeout=25).text
            match=re.search(r'(?:var )?ytInitialPlayerResponse\s*=\s*',s)
            if match:
                d,end=json.JSONDecoder().raw_decode(s[match.end():])
                save(OUT/'sources'/f'{vid}.player.json',d)
                print(vid,d.get('microformat',{}).get('playerMicroformatRenderer',{}).get('liveBroadcastDetails'),flush=True)
                spec=d.get('storyboards',{}).get('playerStoryboardSpecRenderer',{}).get('spec','')
                print('storyboard specs',[x.split('#')[:6] for x in spec.split('|')[1:]],flush=True)
