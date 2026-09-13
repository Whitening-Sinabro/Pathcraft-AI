"""핵심 발언 구간만 VAD 없이 재전사해 1차 전사의 판독을 검증한다.

1차 transcript.txt 는 VAD + batch 로 빠르게 훑은 결과라 고유명사가 뭉개진다.
빌드 구성이 바뀐 정황이 있는 구간만 좁혀서 다시 읽는다.
"""
import json
import logging
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNTIME = ROOT / ".tmp/skadoosh-broadcast-asr/runtime"

for _dll_dir in (RUNTIME / "nvidia/cublas/bin", RUNTIME / "nvidia/cudnn/bin", RUNTIME / "ctranslate2"):
    if _dll_dir.is_dir():
        os.add_dll_directory(str(_dll_dir))
        os.environ["PATH"] = f"{_dll_dir}{os.pathsep}{os.environ['PATH']}"

import soundfile as sf  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

MODEL_DIR = ROOT / ".tmp/skadoosh-broadcast-asr/model"

WINDOWS = [
    ("echo_stacks", 4180, 4320),
    ("armour_break", 4570, 4720),
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("verify")


def stamp(seconds):
    total = int(seconds)
    return f"{total // 3600:02}:{total % 3600 // 60:02}:{total % 60:02}"


def main():
    audio = HERE / "audio.wav"
    model = WhisperModel(str(MODEL_DIR), device="cuda", compute_type="float16", cpu_threads=4)
    out = HERE / "verified_asr"
    out.mkdir(exist_ok=True)

    for label, start, end in WINDOWS:
        with sf.SoundFile(audio) as handle:
            handle.seek(start * 16000)
            wave = handle.read((end - start) * 16000, dtype="float32")
        segments, _info = model.transcribe(
            wave,
            language="en",
            task="transcribe",
            beam_size=10,
            vad_filter=False,
            condition_on_previous_text=False,
            temperature=0,
            word_timestamps=False,
        )
        rows = [
            {"start": start + s.start, "end": start + s.end, "text": s.text.strip(), "avg_logprob": s.avg_logprob}
            for s in segments
        ]
        (out / f"{label}.json").write_text(
            json.dumps({"window": [start, end], "human_checked": False, "segments": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (out / f"{label}.txt").write_text(
            "".join(f"[{stamp(r['start'])}] {r['text']}\n" for r in rows), encoding="utf-8"
        )
        log.info("%s %s-%s segments=%d", label, stamp(start), stamp(end), len(rows))

    log.info("COMPLETE")


if __name__ == "__main__":
    main()
