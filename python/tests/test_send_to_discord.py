"""`scripts/send_to_discord.py` — 보낼 목록 유도 · 비밀값 처리 · 배치 분할.

이 도구가 조용히 틀릴 수 있는 지점은 셋이다.

1. 보낼 목록을 손으로 적으면 빌드한 것과 보낸 것이 갈린다 -> `_meta.outputs`
   에서 유도하는지 고정한다.
2. **이 레포는 공개다.** 토큰이 로그·예외 본문에 실려 나가면 그대로 유출이다
   -> `redact()` 가 모든 출구를 덮는지 확인한다.
3. 첨부 10개 / 8MB 한계를 넘으면 디스코드가 400 을 주는데, 그때는 이미
   일부만 올라간 뒤다 -> 보내기 전에 쪼개는지 확인한다.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "send_to_discord.py"


def _load():
    spec = importlib.util.spec_from_file_location("send_to_discord", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


dc = _load()
TOKEN = "MTIzNDU2.fake.token-value"


class Recorder:
    """post_message 자리에 끼워 넣어 호출을 기록한다. 네트워크에 닿지 않는다."""

    def __init__(self):
        self.calls = []

    def __call__(self, channel_id, token, content, paths):
        self.calls.append({"channel": channel_id, "token": token, "content": content,
                           "paths": [Path(p).name for p in paths]})
        return {"id": f"msg{len(self.calls)}",
                "attachments": [{"filename": Path(p).name, "size": Path(p).stat().st_size}
                                for p in paths]}


def write(path: Path, size: int = 16) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    return path


# --------------------------------------------------------------------------- #
# 비밀값


def test_dotenv_keeps_equals_inside_value(tmp_path: Path):
    """토큰에 `=` 가 들어가는 일이 있다. 첫 `=` 에서만 잘라야 한다."""
    env = tmp_path / ".env"
    env.write_text('DISCORD_BOT_TOKEN="abc=def=ghi"\n# 주석\nOTHER=1\n', encoding="utf-8")
    assert dc.read_dotenv(env)["DISCORD_BOT_TOKEN"] == "abc=def=ghi"


def test_dotenv_missing_file_is_empty_not_error(tmp_path: Path):
    assert dc.read_dotenv(tmp_path / "nope.env") == {}


def test_resolve_precedence_cli_over_env_over_dotenv(tmp_path: Path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("DISCORD_BOT_TOKEN=from_dotenv\n", encoding="utf-8")

    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    assert dc.resolve("DISCORD_BOT_TOKEN", None, env) == "from_dotenv"

    monkeypatch.setenv("DISCORD_BOT_TOKEN", "from_env")
    assert dc.resolve("DISCORD_BOT_TOKEN", None, env) == "from_env"
    assert dc.resolve("DISCORD_BOT_TOKEN", "from_cli", env) == "from_cli"


def test_resolve_missing_says_where_to_put_it(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    with pytest.raises(SystemExit) as e:
        dc.resolve("DISCORD_BOT_TOKEN", None, tmp_path / "nope.env")
    assert "DISCORD_BOT_TOKEN" in str(e.value) and "커밋하지 않는다" in str(e.value)


def test_redact_removes_token():
    assert dc.redact(f"Authorization: Bot {TOKEN} failed", TOKEN) == "Authorization: Bot *** failed"


def test_redact_with_empty_token_is_identity():
    assert dc.redact("아무것도 없음", "") == "아무것도 없음"


def test_network_error_body_is_redacted(monkeypatch, tmp_path: Path):
    """requests 예외 문자열에 URL·헤더가 섞여도 토큰은 못 나간다."""
    import requests

    def boom(*_a, **_k):
        raise requests.RequestException(f"connect failed for Bot {TOKEN}")

    monkeypatch.setattr(dc.requests, "post", boom)
    with pytest.raises(SystemExit) as e:
        dc.post_message("123", TOKEN, "hi", [write(tmp_path / "a.txt")])
    assert TOKEN not in str(e.value) and "***" in str(e.value)


def test_http_error_body_is_redacted(monkeypatch, tmp_path: Path):
    class Resp:
        ok = False
        status_code = 401
        text = f"401 Unauthorized (token {TOKEN})"

    monkeypatch.setattr(dc.requests, "post", lambda *_a, **_k: Resp())
    with pytest.raises(SystemExit) as e:
        dc.post_message("123", TOKEN, "hi", [write(tmp_path / "a.txt")])
    assert TOKEN not in str(e.value) and "401" in str(e.value)


# --------------------------------------------------------------------------- #
# 보낼 목록


def test_spec_outputs_comes_from_meta_outputs():
    """손으로 적은 목록이 아니라 스펙에서 나와야 build_all_filters 와 갈리지 않는다."""
    paths = dc.spec_outputs("poe2_infinite_ignite")
    spec = json.loads(
        (dc.SPEC_DIR / "poe2_infinite_ignite_arserina_0_5_5.json").read_text(encoding="utf-8"))
    assert [p.name for p in paths] == [o["file"] for o in spec["_meta"]["outputs"]]
    assert all(p.parent == dc.FILTER_DIR for p in paths)


def test_spec_selector_must_be_unambiguous():
    with pytest.raises(SystemExit, match="여러 개"):
        dc.spec_outputs("poe2")


def test_spec_selector_unknown_reports_search_dir():
    with pytest.raises(SystemExit, match="스펙을 못 찾았다"):
        dc.spec_outputs("존재하지않는스펙")


def test_planner_prefix_selects_only_that_build():
    ignite = dc.planner_files("Ignite")
    assert ignite and all(p.name.startswith("Ignite") for p in ignite)
    assert all(p.suffix == ".build" for p in ignite)
    assert not set(ignite) & set(dc.planner_files("Fartfinder"))


def test_planner_prefix_unknown_raises():
    with pytest.raises(SystemExit, match="플래너 파일이 없다"):
        dc.planner_files("존재하지않는접두사")


def test_check_payload_points_at_the_build_command(tmp_path: Path):
    with pytest.raises(SystemExit) as e:
        dc.check_payload([tmp_path / "gone.filter"])
    assert "build_all_filters" in str(e.value)


def test_check_payload_rejects_oversized(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(dc, "MAX_MESSAGE_BYTES", 64)
    with pytest.raises(SystemExit, match="넘는다"):
        dc.check_payload([write(tmp_path / "big.bin", 128)])


# --------------------------------------------------------------------------- #
# 배치 분할


def test_batches_split_by_attachment_count(tmp_path: Path):
    files = [write(tmp_path / f"f{i}.txt") for i in range(23)]
    got = list(dc.batches(files))
    assert [len(b) for b in got] == [10, 10, 3]
    assert [p.name for b in got for p in b] == [p.name for p in files]


def test_batches_split_by_total_bytes(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(dc, "MAX_MESSAGE_BYTES", 100)
    files = [write(tmp_path / f"f{i}.bin", 60) for i in range(3)]
    assert [len(b) for b in dc.batches(files)] == [1, 1, 1]


def test_batches_empty_input_yields_nothing():
    assert list(dc.batches([])) == []


def test_deliver_puts_body_on_first_message_only(tmp_path: Path):
    files = [write(tmp_path / f"f{i}.txt") for i in range(12)]
    rec = Recorder()
    assert dc.deliver("chan", TOKEN, "본문", files, poster=rec) == 12
    assert [c["content"] for c in rec.calls] == ["본문", ""]


# --------------------------------------------------------------------------- #
# CLI


def test_dry_run_sends_nothing_and_needs_no_secrets(tmp_path: Path, monkeypatch, caplog):
    """비밀값을 못 찾아도 --dry-run 은 성공해야 한다 — 목록 확인이 먼저다."""
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_CHANNEL_ID", raising=False)
    rec = Recorder()
    with caplog.at_level("INFO", logger="send_to_discord"):
        rc = dc.main(["--spec", "poe2_infinite_ignite", "--dry-run",
                      "--env-file", str(tmp_path / "nope.env")], poster=rec)
    assert rc == 0 and rec.calls == []
    assert "보내지 않았다" in caplog.text


def test_main_requires_something_to_send():
    with pytest.raises(SystemExit, match="보낼 게 없다"):
        dc.main([])


def test_main_rejects_overlong_body(tmp_path: Path):
    body = write(tmp_path / "msg.txt")
    body.write_text("가" * (dc.MAX_CONTENT_CHARS + 1), encoding="utf-8")
    with pytest.raises(SystemExit, match="디스코드 한계"):
        dc.main(["--spec", "poe2_infinite_ignite", "--message-file", str(body), "--dry-run"])


def test_main_sends_spec_and_planner_together(monkeypatch, tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text(f"DISCORD_BOT_TOKEN={TOKEN}\nDISCORD_CHANNEL_ID=999\n", encoding="utf-8")
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_CHANNEL_ID", raising=False)

    rec = Recorder()
    rc = dc.main(["--spec", "poe2_infinite_ignite", "--planner", "Ignite",
                  "--env-file", str(env)], poster=rec)
    assert rc == 0
    sent = [name for call in rec.calls for name in call["paths"]]
    assert any(n.endswith(".filter") for n in sent)
    assert any(n.endswith(".build") for n in sent)
    assert {c["channel"] for c in rec.calls} == {"999"}


def test_default_message_lists_every_file(tmp_path: Path):
    files = [write(tmp_path / "a.filter", 2048), write(tmp_path / "b.build", 1024)]
    body = dc.default_message(files)
    assert "a.filter" in body and "b.build" in body
    assert len(body) <= dc.MAX_CONTENT_CHARS
