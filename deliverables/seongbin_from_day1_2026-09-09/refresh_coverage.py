"""Refresh the public streams listing without replacing the inherited snapshot."""
from pathlib import Path
import datetime, json, sys
import yt_dlp
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
with yt_dlp.YoutubeDL({'quiet':True,'extract_flat':True,'playlistend':60,'socket_timeout':25,'retries':1}) as y:
    data=y.extract_info('https://www.youtube.com/channel/UCvj_myZNbqdHBBFT2IjKJWw/streams',download=False)
(O/'sources/channel_streams_20260910.json').write_text(json.dumps({'retrieved_utc':stamp,'data':data},ensure_ascii=False,indent=2),encoding='utf-8')
known={v['id'] for v in json.loads((O/'방송목록.json').read_text(encoding='utf-8'))['videos']}
entries=data.get('entries',[])
for e in entries[:12]:
    print(json.dumps({k:e.get(k) for k in ['id','title','duration','live_status','release_timestamp']},ensure_ascii=False))
print(json.dumps({'retrieved_utc':stamp,'public_entries_returned':len(entries),'known_ids_seen':sorted(known&{e['id'] for e in entries}), 'limit':60,'complete_archive_claim':False},ensure_ascii=False))
