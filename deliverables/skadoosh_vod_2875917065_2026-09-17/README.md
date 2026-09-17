# Skadoosh 9/17 방송(VOD 2875917065) — Lv90 → Lv91 의 근거

- VOD `2875917065` — 2026-09-16T19:05Z 시작(KST 09-17 04:05), 1:30:09.
  제목은 이전과 같은 `0.5.5 HC OG Warbringer Corrupting Cry Totems !Builds…`
- `creator_latest.json` — poe.ninja `latest`(ITheCon-2183 · SkadooshShoutedHard ·
  hc-forbidden-rites). `updatedUtc = 2026-09-16T20:33:01Z` 로 **이 방송 종료 직후**다.
- `live_pob_lv91.xml` — 위 응답의 `pathOfBuildingExport`(base64url + zlib) 해제본.
- 이 스냅샷이 여정 DB 밴드 `skadoosh/10_live_lv91.build` 로 들어갔다.

## 90 → 91 에서 실제로 바뀐 것 (`diff_character.py`)

직전 비교 대상은 `skadoosh_vod_2874116335_2026-09-15/creator_latest.json`(Lv90,
`updatedUtc 2026-09-14T20:37Z`). **두 스냅샷 사이에 방송이 둘(9/16·9/17) 있다** —
아래 변화를 이 방송 하나로 단정하지 않는다. 확인된 발언만 이 방송에 귀속한다.

- 젬: **도약 강타에 보조 4개** — Rapid Attacks III · Hit and Run · Holy Descent ·
  Persistent Ground III. `Holy Descent`·`Persistent Ground III` 는 이 구간 신규 젬이다.
- 젬 레벨: 선대의 전사 토템 Lv18 → 19 (Q20 유지).
- 장비: 장화 `Dire Sole`(Bulwark Greaves) → `Eagle Hoof`(Vaal Greaves) —
  방어도 87% · 생명력 +140 · 방어도의 32% 를 원소 피해에도 · 생명력 재생 10.5/s.
- 주얼 5 → 6(`Ghoul Heart` 루비), 패시브 113 → 114.

## 이 방송에서 본인이 말한 것

### ① 도약 강타 보조 — 본인이 그 자리에서 넣는다 (00:06:29, 검증본)

> "I should have both of those on **Deep Slap** as well. Let's do that now before I free-hit."

`Deep Slap` 은 ASR 이 뭉갠 **Leap Slam** 이다(1차 전사도 같은 자리에서 `Deep Slap`,
01:00:18 에서는 `Deep Lambs`). 1차 전사의 같은 대목에 `Assistant Ground`(= Persistent
Ground)와 "you can actually get permanent **hit or run** doing this"(= Hit and Run)가
붙어 있다. 스냅샷의 보조 4개 중 둘과 이름이 맞는다.

**프레임으로 확정했다**(`frames.py`, 원본 화질 단일 프레임):
- `frames/000428_000708.jpg` — **젬 세공(Gemcutting) 창**이 열려 있고 왼쪽 목록에서
  **도약 강타가 선택**돼 있다. 소켓은 **1개만 채워져 있고 3개가 비었다**. 검색창에 `hi` 를
  치는 중이다 → **Hit and Run**.
- `frames/000456_000736.jpg` — 28초 뒤 **스킬 창**. **도약 강타 Lv20 에 보조 4개가 모두
  채워져 있다**(초록 2 · 빨강 2). 같은 화면에 보조 젬 용량 Str 20/37 · Dex 11/13 · Int 5/8.

즉 스냅샷의 보조 4개는 **이 방송 00:06:30~00:07:36 사이에 들어갔다**. 90 → 91 젬 변화는
이 방송에 귀속된다. **장화는 9/16 방송**이다 — 그쪽 VOD 00:02:02 프레임에 `Eagle Hoof /
Vaal Greaves` 툴팁(모드 5개 일치)과 `Omen of Dextral Crystallisation` 소모 메시지가 있다
(`../skadoosh_vod_2875018329_2026-09-16/README.md`). 주얼 1개는 아직 어느 방송인지 모른다.

### ② 선대의 유대 = 인내 충전 요구 제거 (00:15:20~00:16:25, 검증본 + 채팅 대조)

시청자 Kriisz40 이 채팅 `00:15:15` 에 "선대의 전사 토템이 인내 충전을 요구하지 않게
하려면?" 을 묻고, 본인이 답한다:

> "if you look at my … I made the **starter variant** … you should be able to get everything
> on the passive tree in the starter variant when you reach level 52 or 54 … including this
> **ancestral bond** — your totem is doubled, no charge required for placing totems,
> totems reserve 75 spirit"

레벨은 본인이 두 번 고쳐 말한다(54 → "I said 54, what is it? **52**"). 시청자는 68레벨이라
"그럼 트리에서 이미 다 찍었어야 한다"로 끝나고, 18:53 에 `ohh ye working` 으로 해결된다.

### ③ 토템 배치 (01:00:18, 1차 전사)

> "it seems like putting the totem further away somehow fixes it"

무엇이 고쳐지는지("이동이 느린 증상")는 같은 구간에서 반복되는 본인의 이동 속도 불평과
이어진다 — 확정이 아니라 관찰이다.

### ④ 가이드에 대한 본인 평가 (00:19:29, 1차 전사)

> "I know I'm not very thorough in that guide, so I understand."

## 파이프라인 기록 (다음 사람이 또 밟을 함정)

- `fetch_audio.py` — **이 단계가 지난 두 폴더엔 없었다**(손으로 했다). Twitch `Audio_Only`
  포맷을 받아 ffmpeg 로 **16kHz 모노 WAV** 로 고정한다. `transcribe.py` 가 16000Hz 를
  가정하고 프레임을 seek 하므로 샘플레이트가 다르면 오류 없이 **엉뚱한 구간**을 전사한다.
- `transcribe.py` / `verify_windows.py` — `faster_whisper` 는 전역 파이썬에 없고
  `.tmp/skadoosh-broadcast-asr/runtime` 에 있다. 지난 세션은 환경변수로 넣고 돌려서
  폴더에 흔적이 없었고, 그대로 재실행하면 `ModuleNotFoundError` 다. 이제 스크립트가
  `sys.path` 에 직접 넣는다.
- **1차 전사의 타임스탬프를 인용에 쓰지 마라.** VAD + 배치 전사라 무음을 걷어낸 만큼
  시작 시각이 밀린다. 같은 발언이 1차 00:12:32, 검증본 00:15:20 이고 **채팅(00:15:15)이
  검증본 편이다.** 인용 앵커는 `verified_asr/` 쪽을 쓴다.
- VAD 를 끄면 음악·무음 구간에서 `Thank you` · `We'll be right back` 같은 환각이 섞인다.
  검증본은 고유명사 확인용이고, 문장 유무 판정은 두 전사를 같이 본다.

## 산출물

| 파일 | 내용 |
|---|---|
| `chat.json` / `chat.txt` | 채팅 리플레이 11건(19요청, 300초 재시드) |
| `audio.wav` | 16kHz 모노 5409.2초 |
| `chunks/` + `transcript.txt` / `transcript.json` | 1200초 창 5개(겹침 5초), 세그먼트 26 |
| `asr_coverage.json` | 전 구간 처리 확인(`complete_audio_processed: true`) |
| `verified_asr/` | VAD 끈 재전사 3구간 — `leap_slam_supports` · `ancestral_bond_answer` · `totem_placement` |
| `creator_latest.json` · `live_pob_lv91.xml` | 방송 직후 공개 스냅샷 |
