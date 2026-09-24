"""Focused independent ASR pass. Raw recognitions remain labelled automatic."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'deliverables/skadoosh_hc_2026-09-07/broadcast_audit'))
import transcribe_broadcasts as common
import soundfile as sf
from faster_whisper import WhisperModel
jobs=[('helmet',745,925),('life_cost',1320,1470),('recovery_and_sets',4200,4510),('sunder_precision',9085,9550),('sunder_verdict',9580,9770),('fourth_ascendancy',11265,11395),('soul_cores',11505,11640),('set_warning_exact',4500,4570),('sunder_return',9760,9920),('life_cost_exact',1470,1580)]
out=HERE/'verified_asr';out.mkdir(exist_ok=True)
model=WhisperModel(str(ROOT/'.tmp/skadoosh-broadcast-asr/verification-model'),device='cuda',compute_type='int8_float16',cpu_threads=4)
for label,start,end in jobs:
    target=out/(label+'.json')
    if target.exists():data=json.loads(target.read_text(encoding='utf-8'))
    else:
        with sf.SoundFile(HERE/'audio.flac') as f:
            f.seek(round(start*16000));wave=f.read(round((end-start)*16000),dtype='float32')
        segments,info=model.transcribe(wave,language='en',task='transcribe',beam_size=5,temperature=0,vad_filter=False,condition_on_previous_text=False,word_timestamps=True)
        data={'model':'large-v3','interval':[start,end],'human_checked':False,'segments':[{'start':start+s.start,'end':start+s.end,'text':s.text.strip(),'no_speech_prob':s.no_speech_prob,'avg_logprob':s.avg_logprob} for s in segments]}
        common.save(target,data)
    (out/(label+'.txt')).write_text('\n'.join(f'[{common.stamp(s["start"])}] {s["text"]}' for s in data['segments'])+'\n',encoding='utf-8')
    print('Verified ASR '+label,flush=True)
