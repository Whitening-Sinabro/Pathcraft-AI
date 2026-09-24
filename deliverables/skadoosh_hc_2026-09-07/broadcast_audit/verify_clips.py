"""Second ASR from source audio using the full large-v3 model, no vocabulary prompt."""
from transcribe_broadcasts import HERE,ROOT,save,stamp
import argparse
import soundfile as sf
from faster_whisper import WhisperModel

p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('start',type=float);p.add_argument('duration',type=float);a=p.parse_args()
folder=HERE/a.video;out=folder/'second_pass';out.mkdir(exist_ok=True)
with sf.SoundFile(folder/'audio.flac') as f:
    f.seek(round(a.start*f.samplerate));wave=f.read(round(a.duration*f.samplerate),dtype='float32')
model=WhisperModel(str(ROOT/'.tmp/skadoosh-broadcast-asr/verification-model'),device='cuda',compute_type='int8_float16',cpu_threads=4)
segments,info=model.transcribe(wave,language='en',task='transcribe',beam_size=5,temperature=0,
    vad_filter=False,condition_on_previous_text=False,word_timestamps=True)
rows=[]
for s in segments:
    row={'start':a.start+s.start,'end':a.start+s.end,'text':s.text.strip(),'avg_logprob':s.avg_logprob,
         'words':[{'start':a.start+w.start,'end':a.start+w.end,'word':w.word,'probability':w.probability} for w in s.words or []]}
    rows.append(row);print(f'[{stamp(row["start"])}] {row["text"]}',flush=True)
save(out/f'{int(a.start):06}_{int(a.duration):04}.json',{'model':'large-v3','interval':[a.start,a.start+a.duration],
     'initial_prompt':None,'segments':rows,'human_audio_listened':False})
