"""임성빈 방송에서 **아틀라스 패시브 트리 화면**을 뽑는다.

자막엔 노드 이름이 안 나온다(`.claude/status/poe2_hc_gemling.md` 아틀라스 절).
그래서 화면 판독이 유일한 경로다.

전체를 받지 않는다. 유튜브는 googlevideo 서명이 player_client 에 묶여 있어서
스트림 URL 을 ffmpeg 에 그냥 넘기면 403 이 난다(트위치용
`deliverables/skadoosh_vod_*/frames.py` 와 다른 점). 그래서 yt_dlp 가 직접
`download_ranges` 로 그 구간만 받게 하고, 받은 조각에서 프레임을 뽑는다.

사용:
    python frames.py <video_id> <초> [<초> ...]
"""
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOW = 4.0          # 구간 길이(초). 키프레임 정렬 때문에 여유를 둔다

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    stream=sys.stdout)
log = logging.getLogger("frames")


def stamp(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02}:{s // 60 % 60:02}:{s % 60:02}"


def grab(video_id: str, t: float, dest: Path) -> bool:
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmp:
        clip = Path(tmp) / "clip.mp4"
        opts = {
            "quiet": True, "no_warnings": True,
            "format": "best[height<=1080]/best",
            "outtmpl": str(clip),
            "download_ranges": lambda _info, _ydl: [
                {"start_time": t, "end_time": t + WINDOW}],
            "force_keyframes_at_cuts": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        except Exception as exc:                      # 네트워크·추출기 실패 전부
            log.error("%s 구간 받기 실패: %s", stamp(t), exc)
            return False
        got = clip if clip.exists() else next(iter(Path(tmp).glob("*")), None)
        if got is None:
            log.error("%s 받은 파일이 없다", stamp(t))
            return False
        done = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(got),
                               "-frames:v", "1", "-q:v", "2", str(dest)])
        return done.returncode == 0 and dest.exists()


def main() -> int:
    if len(sys.argv) < 3:
        log.error("사용: python frames.py <video_id> <초> [<초> ...]")
        return 2
    video_id, times = sys.argv[1], [float(a) for a in sys.argv[2:]]
    out = HERE / video_id
    out.mkdir(parents=True, exist_ok=True)
    for t in times:
        dest = out / f"{int(t):06}_{stamp(t).replace(':', '')}.jpg"
        if dest.exists():
            log.info("이미 있다 %s", dest.name)
            continue
        if grab(video_id, t, dest):
            log.info("%s -> %s", stamp(t), dest.name)
        else:
            log.error("%s 프레임 실패", stamp(t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
