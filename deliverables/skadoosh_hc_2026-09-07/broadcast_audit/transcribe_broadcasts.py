"""Resumeable complete ASR, retaining raw segments and exact source intervals.

No transcript is labelled human checked by this script. review_status.json is
separate from processing coverage. Five-second overlaps protect chunk borders.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, sys, json, time, argparse, hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RUNTIME=ROOT/'.tmp/skadoosh-broadcast-asr/runtime'
sys.path.insert(0,str(RUNTIME))
DLL_HANDLES=[]
for folder in RUNTIME.glob('nvidia/*/bin'):
    DLL_HANDLES.append(os.add_dll_directory(str(folder)))
    os.environ['PATH']=str(folder)+os.pathsep+os.environ.get('PATH','')

def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def stamp(t):
    s=int(t);return f'{s//3600:02}:{s//60%60:02}:{s%60:02}'

def srt_stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def main():
    import soundfile as sf
    from faster_whisper import WhisperModel, BatchedInferencePipeline
    args=argparse.ArgumentParser();args.add_argument('--video',choices=['2865212551','2866065347','2866749730'])
    args.add_argument('--model',choices=['turbo','large-v3'],default='turbo')
    a=args.parse_args()
    model_path=ROOT/('.tmp/skadoosh-broadcast-asr/model' if a.model=='turbo' else '.tmp/skadoosh-broadcast-asr/verification-model')
    suffix='' if a.model=='turbo' else '_large_v3'
    model_name='large-v3-turbo' if a.model=='turbo' else 'large-v3'
    print('Loading '+model_name+' on CUDA, batch 4, beam 5',flush=True)
    model=WhisperModel(str(model_path),device='cuda',compute_type='float16' if a.model=='turbo' else 'int8_float16',cpu_threads=4)
    pipe=BatchedInferencePipeline(model=model)
    vids=[a.video] if a.video else ['2865212551','2866065347','2866749730']
    for vid in vids:
        folder=HERE/vid;audio=folder/'audio.flac';coverage=folder/'audio_coverage.json'
        while not coverage.exists():
            print('Waiting for complete audio '+vid,flush=True);time.sleep(30)
        dur=sf.info(audio).duration;chunks=folder/('chunks'+suffix);chunks.mkdir(exist_ok=True)
        records=[];intervals=[];started=time.monotonic()
        for index,nominal in enumerate(range(0,int(dur)+1,1200)):
            start=max(0,nominal-5);end=min(dur,nominal+1200)
            if end<=start:continue
            target=chunks/f'{index:03}.json'
            if target.exists():
                data=json.loads(target.read_text(encoding='utf-8'))
            else:
                with sf.SoundFile(audio) as f:
                    assert f.samplerate==16000 and f.channels==1
                    f.seek(round(start*16000));wave=f.read(round((end-start)*16000),dtype='float32')
                segments,info=pipe.transcribe(wave,language='en',task='transcribe',beam_size=5,batch_size=4,
                    vad_filter=True,vad_parameters={'threshold':0.4,'min_silence_duration_ms':500},
                    condition_on_previous_text=False,temperature=0,word_timestamps=False)
                rows=[]
                for s in segments:
                    rows.append({'start':start+s.start,'end':start+s.end,'text':s.text.strip(),
                                 'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob})
                data={'video_id':vid,'interval':[start,end],'model':model_name,
                      'language':'en','vad':True,'threshold':0.4,'beam':5,'initial_prompt':None,
                      'segments':rows,'human_checked':False,'completed_utc':datetime.now(timezone.utc).isoformat()}
                save(target,data)
                (chunks/f'{index:03}.txt').write_text('\n'.join(f'[{stamp(s["start"])}] {s["text"]}' for s in rows)+'\n',encoding='utf-8')
            records.extend(data['segments']);intervals.append(data['interval'])
            print(f'{vid} {index+1}/{int(dur)//1200+1} ASR {stamp(end)} / {stamp(dur)} ({int(time.monotonic()-started)}s elapsed)',flush=True)
        # Keep overlap rows in JSON for provenance; remove only exact near-time
        # repeats in the readable export. Never silently rewrite recognised words.
        cleaned=[]
        for s in sorted(records,key=lambda s:s['start']):
            if any(s['text']==p['text'] and abs(s['start']-p['start'])<3 for p in cleaned[-5:]):continue
            cleaned.append(s)
        save(folder/('transcript'+suffix+'.json'),{'segments':cleaned,'raw_overlap_rows_retained_in_chunks':True,'human_checked':False})
        (folder/('transcript'+suffix+'.txt')).write_text('\n'.join(f'[{stamp(s["start"])}] {s["text"]}' for s in cleaned)+'\n',encoding='utf-8')
        (folder/('transcript'+suffix+'.srt')).write_text('\n\n'.join(f'{i}\n{srt_stamp(s["start"])} --> {srt_stamp(s["end"])}\n{s["text"]}' for i,s in enumerate(cleaned,1))+'\n',encoding='utf-8')
        assert intervals[0][0]==0 and abs(intervals[-1][1]-dur)<0.1
        assert all(a[1]>=b[0] for a,b in zip(intervals,intervals[1:]))
        save(folder/('asr_coverage'+suffix+'.json'),{'video_id':vid,'audio_duration_seconds':dur,'processed_intervals':intervals,
             'complete_audio_processed':True,'segments':len(cleaned),'human_checked':False,
             'model_config_sha256':hashlib.sha256((model_path/'config.json').read_bytes()).hexdigest()})
        print('COMPLETE ASR '+vid,flush=True)

if __name__=='__main__':main()
