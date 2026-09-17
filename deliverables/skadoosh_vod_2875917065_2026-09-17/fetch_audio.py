"""Twitch VOD 오디오를 16kHz 모노 WAV 로 받는다 — `transcribe.py` 가 읽는 형식.

왜 스크립트로 두나: 지난 두 VOD 는 이 단계만 손으로 했고 그래서 폴더에 남지 않았다
(다음 사람이 파라미터를 다시 추측해야 한다). `transcribe.py` 는 `sf.SoundFile` 로
**16000Hz 로 가정하고** 프레임을 seek 하므로 샘플레이트가 다르면 조용히 어긋난 구간을
전사한다 — 오류가 아니라 잘못된 타임스탬프로 나온다. 그래서 여기서 못 박는다.
"""
import logging
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO_ID = "2875917065"
URL = f"https://www.twitch.tv/videos/{VIDEO_ID}"
DEST = HERE / "audio.wav"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("audio")


def main() -> int:
    if DEST.exists():
        log.info("이미 있다: %s (%.1fMB)", DEST.name, DEST.stat().st_size / 1e6)
        return 0
    cmd = [
        sys.executable, "-m", "yt_dlp", URL,
        "-f", "bestaudio/best",
        "--extract-audio", "--audio-format", "wav",
        "--postprocessor-args", "-ar 16000 -ac 1",
        "-o", str(HERE / "audio.%(ext)s"),
        "--no-warnings", "--no-part",
    ]
    log.info("받는 중 %s", URL)
    done = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace")
    if done.returncode or not DEST.exists():
        log.error("실패 rc=%s — 오디오 없이 전사 단계로 넘어가지 마라", done.returncode)
        return 1
    log.info("완료 %s (%.1fMB)", DEST.name, DEST.stat().st_size / 1e6)
    return 0


if __name__ == "__main__":
    sys.exit(main())
