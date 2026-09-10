from pathlib import Path
import yt_dlp,json,sys,datetime
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent
for vid in sys.argv[1:]:
    with yt_dlp.YoutubeDL({'quiet':True,'skip_download':True,'socket_timeout':20,'retries':1,'js_runtimes':{'node':{}}}) as y:
        d=y.extract_info('https://www.youtube.com/watch?v='+vid,download=False)
    (O/'sources'/f'{vid}.resume.info.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
    print(vid,d['title'],d['duration'],datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
