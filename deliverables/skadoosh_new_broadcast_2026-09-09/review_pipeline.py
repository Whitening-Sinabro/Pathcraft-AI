"""Public VOD audio acquisition and automatic transcript, never visual-review claims."""
from pathlib import Path
import sys, json, time, subprocess, threading, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'https://dgeft87wbj63p.cloudfront.net/51b661c9b1227bdf020a_skadoosh_c_316804162645_1788888412/'
sys.path.insert(0, str(ROOT/'deliverables/skadoosh_hc_2026-09-07/broadcast_audit'))
import transcribe_broadcasts as common

def main():
    manifest = (HERE/'audio.m3u8').read_text()
    names = [x.strip() for x in manifest.splitlines() if x and not x.startswith('#')]
    expected = sum(float(x.split(':')[1].split(',')[0]) for x in manifest.splitlines() if x.startswith('#EXTINF:'))
    folder = HERE/'audio_fragments'; folder.mkdir(exist_ok=True)
    local = threading.local()
    def fetch(pair):
        index, name = pair
        target = folder/f'{index:04}.ts'
        if target.exists() and target.stat().st_size: return target
        if not hasattr(local, 'session'): local.session = requests.Session()
        for attempt in range(6):
            try:
                response = local.session.get(urljoin(BASE+'audio_only/', name), timeout=40)
                response.raise_for_status()
                assert len(response.content)>0
                target.write_bytes(response.content)
                return target
            except Exception:
                if attempt==5: raise
                time.sleep(attempt+1)
    audio = HERE/'audio.flac'
    if not (HERE/'audio_coverage.json').exists():
        with ThreadPoolExecutor(max_workers=16) as pool:
            tasks = [pool.submit(fetch, pair) for pair in enumerate(names)]
            for n, task in enumerate(as_completed(tasks), 1):
                task.result()
                if n%100==0 or n==len(names): print(f'Audio fragments {n}/{len(names)}', flush=True)
        joined = HERE/'audio.ts'
        with joined.open('wb') as out:
            for i in range(len(names)): out.write((folder/f'{i:04}.ts').read_bytes())
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(joined),'-vn','-ac','1','-ar','16000','-c:a','flac',str(audio)], check=True)
        import soundfile as sf
        duration = sf.info(audio).duration
        assert abs(expected-duration)<2, (expected,duration)
        common.save(HERE/'audio_coverage.json', {'video_id':'2868822161','expected_seconds':expected,'audio_seconds':duration,'segments':len(names),'missing_segments':0,'source':BASE+'audio_only/index-dvr.m3u8','audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest()})
    import soundfile as sf
    from faster_whisper import WhisperModel, BatchedInferencePipeline
    duration = sf.info(audio).duration
    print('Loading existing large-v3-turbo CUDA model', flush=True)
    model=WhisperModel(str(ROOT/'.tmp/skadoosh-broadcast-asr/model'),device='cuda',compute_type='float16',cpu_threads=4)
    pipe=BatchedInferencePipeline(model)
    chunks=HERE/'chunks';chunks.mkdir(exist_ok=True)
    rows=[]; intervals=[]
    for index, nominal in enumerate(range(0,int(duration)+1,1200)):
        start=max(0,nominal-5);end=min(duration,nominal+1200)
        if end<=start:continue
        target=chunks/f'{index:03}.json'
        if target.exists(): data=json.loads(target.read_text(encoding='utf-8'))
        else:
            with sf.SoundFile(audio) as f:
                f.seek(round(start*16000)); wave=f.read(round((end-start)*16000),dtype='float32')
            segments,info=pipe.transcribe(wave,language='en',task='transcribe',beam_size=5,batch_size=4,vad_filter=True,vad_parameters={'threshold':.4,'min_silence_duration_ms':500},condition_on_previous_text=False,temperature=0,word_timestamps=False)
            data={'video_id':'2868822161','interval':[start,end],'model':'large-v3-turbo','human_checked':False,'segments':[{'start':start+s.start,'end':start+s.end,'text':s.text.strip(),'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob} for s in segments]}
            common.save(target,data)
        (chunks/f'{index:03}.txt').write_text('\n'.join(f'[{common.stamp(s["start"])}] {s["text"]}' for s in data['segments'])+'\n',encoding='utf-8')
        rows.extend(data['segments']); intervals.append(data['interval'])
        print(f'ASR {index+1}/11 complete to {common.stamp(end)}',flush=True)
    cleaned=[]
    for s in sorted(rows,key=lambda s:s['start']):
        if any(s['text']==p['text'] and abs(s['start']-p['start'])<3 for p in cleaned[-5:]):continue
        cleaned.append(s)
    common.save(HERE/'transcript.json',{'segments':cleaned,'human_checked':False,'raw_overlap_rows_retained_in_chunks':True})
    (HERE/'transcript.txt').write_text('\n'.join(f'[{common.stamp(s["start"])}] {s["text"]}' for s in cleaned)+'\n',encoding='utf-8')
    assert intervals[0][0]==0 and abs(intervals[-1][1]-duration)<.1
    assert all(a[1]>=b[0] for a,b in zip(intervals,intervals[1:]))
    common.save(HERE/'asr_coverage.json',{'complete_audio_processed':True,'audio_duration_seconds':duration,'processed_intervals':intervals,'segments':len(cleaned),'human_checked':False,'model':'large-v3-turbo'})
    print('COMPLETE',flush=True)

if __name__=='__main__': main()
