"""Two bounded follow-up ASR checks; preserves automatic transcription labels."""
from pathlib import Path
import sys, json

HERE = Path(__file__).resolve().parent
VOD = HERE.parent
ROOT = VOD.parents[1]
sys.path.insert(0, str(ROOT / 'deliverables/skadoosh_hc_2026-09-07/broadcast_audit'))
import transcribe_broadcasts as common
import soundfile as sf
from faster_whisper import WhisperModel

if __name__ == '__main__':
    model = WhisperModel(str(ROOT / '.tmp/skadoosh-broadcast-asr/verification-model'), device='cuda', compute_type='int8_float16', cpu_threads=4)
    for label, start, end in [('scavenged', 4560, 4705), ('armour_threshold', 6740, 6885)]:
        target = HERE / (label + '_asr.json')
        if target.exists():
            data = json.loads(target.read_text(encoding='utf-8'))
        else:
            with sf.SoundFile(VOD / 'audio.flac') as f:
                f.seek(start * 16000)
                wave = f.read((end - start) * 16000, dtype='float32')
            segments, info = model.transcribe(wave, language='en', beam_size=5, temperature=0, vad_filter=False, condition_on_previous_text=False, word_timestamps=True)
            data = {'model': 'large-v3', 'interval': [start, end], 'automatic_transcription': True, 'segments': [{'start': start+s.start, 'end': start+s.end, 'text': s.text.strip()} for s in segments]}
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        (HERE / (label + '_asr.txt')).write_text('\n'.join(f'[{common.stamp(s["start"])}] {s["text"]}' for s in data['segments']), encoding='utf-8')
        print(label, 'complete', flush=True)
