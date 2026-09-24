"""Recheck bounded survival scenes from the preserved Twitch audio.

Produces ASR evidence, not a claim of human listening or complete video review.
Keeps the previous audit and all original media unchanged.
"""
from pathlib import Path
import hashlib
import json
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
AUDIT = ROOT / 'deliverables/skadoosh_hc_2026-09-07/broadcast_audit'
sys.path.insert(0, str(AUDIT))
import transcribe_broadcasts  # Initializes the existing CUDA runtime paths.
import soundfile as sf
from faster_whisper import WhisperModel

# Source offsets are broad on purpose: the old batched ASR merged long silences.
SCENES = [
    ('day1_start_flasks', '2865212551', 5460, 460),
    ('day1_totem_duration', '2865212551', 7580, 280),
    ('day1_no_sprint_mists', '2865212551', 9060, 420),
    ('day1_fire_resistance', '2865212551', 11490, 120),
    ('day1_armour_break_ritual', '2865212551', 13260, 600),
    ('day2_damage_vs_res', '2866065347', 1290, 110),
    ('day2_block_near_miss', '2866065347', 4220, 180),
    ('day2_sprint_warning', '2866065347', 5850, 150),
    ('day2_optional_ritual', '2866065347', 6160, 180),
    ('day2_skip_repeat', '2866065347', 7560, 420),
    ('day1_totem_duration_followup', '2865212551', 7855, 150),
    ('day1_resistance_followup', '2865212551', 11600, 400),
    ('day2_block_followup', '2866065347', 4380, 350),
]

def stamp(t):
    s = int(t)
    return f'{s//3600:02}:{s//60%60:02}:{s%60:02}'

def main():
    model = None
    manifest = []
    for name, vod, start, duration in SCENES:
        target = OUT / (name + '.json')
        if target.exists():
            data = json.loads(target.read_text(encoding='utf-8'))
        else:
            if model is None:
                model = WhisperModel(str(ROOT / '.tmp/skadoosh-broadcast-asr/verification-model'),
                                     device='cuda', compute_type='int8_float16', cpu_threads=4)
            with sf.SoundFile(AUDIT / vod / 'audio.flac') as f:
                sample_rate = f.samplerate
                f.seek(start * sample_rate)
                wave = f.read(duration * sample_rate, dtype='float32')
            segments, _ = model.transcribe(wave, language='en', beam_size=5, temperature=0,
                vad_filter=False, condition_on_previous_text=False, word_timestamps=True)
            rows = [{'start': start + s.start, 'end': start + s.end, 'text': s.text.strip(),
                     'avg_logprob': s.avg_logprob} for s in segments]
            data = {'video_id': vod, 'interval': [start, start + duration],
                    'model': 'large-v3', 'vad_filter': False, 'initial_prompt': None,
                    'human_audio_listened': False, 'segments': rows}
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (OUT / (name + '.txt')).write_text('\n'.join(
            f'[{stamp(s["start"])}–{stamp(s["end"])}] {s["text"]}' for s in data['segments']) + '\n', encoding='utf-8')
        manifest.append({'name': name, 'video': vod, 'interval': data['interval'],
                         'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
        print(name, len(data['segments']), 'segments', flush=True)
    (OUT / 'focus_coverage.json').write_text(json.dumps({'scenes': manifest,
        'audio_seconds_processed': sum(s[3] for s in SCENES), 'human_audio_listened': False}, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
