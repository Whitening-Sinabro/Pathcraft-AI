"""Collect the three public Forbidden Rites broadcasts, with explicit coverage."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, subprocess
import yt_dlp

HERE = Path(__file__).resolve().parent
VODS = ['2865212551', '2866065347', '2866749730']

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def metadata():
    rows=[]
    for day, vid in enumerate(VODS, 1):
        folder=HERE/vid; folder.mkdir(exist_ok=True)
        options={'quiet':True, 'no_warnings':True, 'skip_download':True,
                 'writesubtitles':True, 'writeautomaticsub':True,
                 'subtitleslangs':['all'], 'outtmpl':str(folder/'native.%(ext)s')}
        with yt_dlp.YoutubeDL(options) as ydl:
            info=ydl.extract_info('https://www.twitch.tv/videos/'+vid, download=True)
        row={k:info.get(k) for k in ['id','title','uploader','uploader_id','timestamp','upload_date','duration','webpage_url']}
        row.update(day=day, video_id=vid, retrieved_utc=datetime.now(timezone.utc).isoformat(),
                   subtitles=list(info.get('subtitles',{})), automatic_captions=list(info.get('automatic_captions',{})),
                   formats=[{k:f.get(k) for k in ['format_id','height','width','fps','vcodec','acodec','tbr']} for f in info.get('formats',[])])
        save(folder/'metadata.json',row);rows.append(row)
        print(json.dumps(row,ensure_ascii=True),flush=True)
    save(HERE/'broadcasts.json',rows)

def download(kind):
    for vid in VODS:
        folder=HERE/vid;folder.mkdir(exist_ok=True)
        if kind=='audio' and (folder/'audio.flac').exists():
            print(vid+' audio already exists',flush=True);continue
        if kind=='video' and (folder/'video.mp4').exists():
            print(vid+' video already exists',flush=True);continue
        bucket=[-1]
        def progress(status):
            if status['status']=='downloading':
                total=status.get('total_bytes') or status.get('total_bytes_estimate') or 1
                n=int(10*status.get('downloaded_bytes',0)/total)
                if n>bucket[0]:
                    bucket[0]=n;print(vid+' '+kind+' '+str(min(n*10,100))+'%',flush=True)
        opts={'quiet':True,'noprogress':True,'no_warnings':True,'retries':10,'fragment_retries':10,
              'skip_unavailable_fragments':False, 'concurrent_fragment_downloads':6,
              'format':'bestaudio' if kind=='audio' else 'worst[height>=360]/best',
              'outtmpl':str(folder/(kind+'.%(ext)s')),'progress_hooks':[progress]}
        print('Downloading '+vid+' '+kind,flush=True)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info('https://www.twitch.tv/videos/'+vid,download=True)
            source=Path(ydl.prepare_filename(info))
        if kind=='audio':
            subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(source),'-vn','-ac','1','-ar','16000','-c:a','flac',str(folder/'audio.flac')],check=True)
            source=folder/'audio.flac'
        probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(source)],check=True,capture_output=True,text=True)
        actual=json.loads(probe.stdout)['format']
        assert abs(float(actual['duration'])-float(info['duration']))<5,(vid,'incomplete duration',actual)
        save(folder/(kind+'_coverage.json'),{'path':str(source),'expected_seconds':info['duration'],
              'actual_seconds':float(actual['duration']),'bytes':int(actual['size']),
              'format_id':info['format_id'],'download_completed_utc':datetime.now(timezone.utc).isoformat(),
              'unavailable_fragments_allowed':False})
        print('COMPLETE '+vid+' '+kind+' '+str(actual['duration'])+' seconds',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['metadata','audio','video']);a=p.parse_args()
    metadata() if a.kind=='metadata' else download(a.kind)
