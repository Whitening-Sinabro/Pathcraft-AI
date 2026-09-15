"""Skadoosh VOD 2874116335 (2026-09-15 KST 02:14 시작, 3:26:55) 전체 오디오 전사.

이전 세션 deliverables/skadoosh_new_broadcast_2026-09-09/review_pipeline.py 의
ASR 단계를 같은 모델·같은 파라미터로 재사용한다.
"""
import json
import logging
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNTIME = ROOT / ".tmp/skadoosh-broadcast-asr/runtime"

# ctranslate2 는 cublas/cudnn 을 실행 시점에 LoadLibrary 로 찾는다.
# Windows 파이썬은 PATH 만으로는 확장 모듈의 DLL 을 못 찾으므로 명시적으로 등록한다.
for _dll_dir in (RUNTIME / "nvidia/cublas/bin", RUNTIME / "nvidia/cudnn/bin", RUNTIME / "ctranslate2"):
    if _dll_dir.is_dir():
        os.add_dll_directory(str(_dll_dir))
        os.environ["PATH"] = f"{_dll_dir}{os.pathsep}{os.environ['PATH']}"

import soundfile as sf  # noqa: E402
from faster_whisper import WhisperModel, BatchedInferencePipeline  # noqa: E402

VIDEO_ID = "2874116335"
MODEL_DIR = ROOT / ".tmp/skadoosh-broadcast-asr/model"
WINDOW = 1200
OVERLAP = 5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("transcribe")


def stamp(seconds):
    total = int(seconds)
    return f"{total // 3600:02}:{total % 3600 // 60:02}:{total % 60:02}"


def save(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def lines(segments):
    return "".join(f"[{stamp(s['start'])}] {s['text']}\n" for s in segments)


def transcribe_window(pipe, audio, start, end):
    with sf.SoundFile(audio) as handle:
        handle.seek(round(start * 16000))
        wave = handle.read(round((end - start) * 16000), dtype="float32")
    segments, _info = pipe.transcribe(
        wave,
        language="en",
        task="transcribe",
        beam_size=5,
        batch_size=4,
        vad_filter=True,
        vad_parameters={"threshold": 0.4, "min_silence_duration_ms": 500},
        condition_on_previous_text=False,
        temperature=0,
        word_timestamps=False,
    )
    return [
        {
            "start": start + s.start,
            "end": start + s.end,
            "text": s.text.strip(),
            "avg_logprob": s.avg_logprob,
            "no_speech_prob": s.no_speech_prob,
        }
        for s in segments
    ]


def main():
    audio = HERE / "audio.wav"
    if not audio.exists():
        raise SystemExit(f"audio missing: {audio}")
    duration = sf.info(audio).duration
    log.info("audio %.1fs", duration)

    model = WhisperModel(str(MODEL_DIR), device="cuda", compute_type="float16", cpu_threads=4)
    pipe = BatchedInferencePipeline(model)

    chunks = HERE / "chunks"
    chunks.mkdir(exist_ok=True)
    nominals = list(range(0, int(duration) + 1, WINDOW))
    rows, intervals = [], []

    for index, nominal in enumerate(nominals):
        start = max(0, nominal - OVERLAP)
        end = min(duration, nominal + WINDOW)
        if end <= start:
            continue
        target = chunks / f"{index:03}.json"
        if target.exists():
            data = json.loads(target.read_text(encoding="utf-8"))
        else:
            data = {
                "video_id": VIDEO_ID,
                "interval": [start, end],
                "model": "large-v3-turbo",
                "human_checked": False,
                "segments": transcribe_window(pipe, audio, start, end),
            }
            save(target, data)
        (chunks / f"{index:03}.txt").write_text(lines(data["segments"]), encoding="utf-8")
        rows.extend(data["segments"])
        intervals.append(data["interval"])
        log.info("ASR %d/%d to %s", index + 1, len(nominals), stamp(end))

    cleaned = []
    for s in sorted(rows, key=lambda s: s["start"]):
        if any(s["text"] == p["text"] and abs(s["start"] - p["start"]) < 3 for p in cleaned[-5:]):
            continue
        cleaned.append(s)

    save(HERE / "transcript.json", {"segments": cleaned, "human_checked": False})
    (HERE / "transcript.txt").write_text(lines(cleaned), encoding="utf-8")

    assert intervals[0][0] == 0 and abs(intervals[-1][1] - duration) < 0.1
    assert all(a[1] >= b[0] for a, b in zip(intervals, intervals[1:]))
    save(
        HERE / "asr_coverage.json",
        {
            "video_id": VIDEO_ID,
            "complete_audio_processed": True,
            "audio_duration_seconds": duration,
            "processed_intervals": intervals,
            "segments": len(cleaned),
            "human_checked": False,
            "model": "large-v3-turbo",
        },
    )
    log.info("COMPLETE segments=%d", len(cleaned))


if __name__ == "__main__":
    main()
