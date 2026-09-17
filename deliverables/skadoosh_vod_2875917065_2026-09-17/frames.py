"""VOD 의 특정 시각 프레임을 원본 화질로 뽑는다 — 음성이 애매할 때의 다음 사다리.

전체를 받지 않는다. yt_dlp 로 스트림 URL 만 얻어 ffmpeg `-ss` 로 그 시각만 읽는다
(`deliverables/skadoosh_hc_2026-09-07/broadcast_audit/frames.py` 의 `--hd` 경로와 같다).

사용: python frames.py 380 389 396 405
"""
import logging
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO_ID = "2875917065"
OUT = HERE / "frames"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
log = logging.getLogger("frames")


def stamp(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02}:{s // 60 % 60:02}:{s % 60:02}"


def main() -> int:
    times = [float(a) for a in sys.argv[1:]]
    if not times:
        log.error("시각(초)을 하나 이상 줘라")
        return 2
    import yt_dlp

    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                           "format": "best[height<=1080]/best"}) as ydl:
        info = ydl.extract_info(f"https://www.twitch.tv/videos/{VIDEO_ID}", download=False)
    OUT.mkdir(exist_ok=True)
    for t in times:
        dest = OUT / f"{int(t):06}_{stamp(t).replace(':', '')}.jpg"
        if dest.exists():
            log.info("이미 있다 %s", dest.name)
            continue
        done = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-ss", str(t),
                               "-i", info["url"], "-frames:v", "1", "-q:v", "2", str(dest)])
        if done.returncode or not dest.exists():
            log.error("%s 프레임 실패", stamp(t))
            continue
        log.info("%s -> %s", stamp(t), dest.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
