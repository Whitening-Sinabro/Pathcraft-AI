# Skadoosh 9/16 방송(VOD 2875018329) — 장화가 여기서 나왔다

- VOD `2875018329` — 2026-09-15T18:25Z 시작(KST 09-16 03:25), 2:23:55.
  제목은 이전과 같은 `0.5.5 HC OG Warbringer Corrupting Cry Totems !Builds…`
- 이 방송 직후의 공개 스냅샷은 따로 없다. 다음 갱신이 9/17 방송 종료 직후(Lv91)라
  **장비 변화가 9/16 것인지 9/17 것인지는 스냅샷만으로 못 가른다.** 그래서 화면을 봤다.

## 장화 — `Eagle Hoof / Vaal Greaves` 를 이 방송 첫 2분에 만든다

`frames/000122_000202.jpg`(00:02:02, 원본 화질)에 아이템 툴팁이 그대로 있다:

| 항목 | 값 | 티어 |
|---|---|---|
| 베이스 | Vaal Greaves · **아이템 레벨 81** · 방어도 501 · 요구 75레벨 / 힘 101 | |
| 방어도 증가 | 87(80–91)% | T2 |
| 최대 생명력 | +140(120–149) | **T1** |
| 이동 속도 | 30% 증가 | T2 |
| 방어도의 원소 피해 적용 | +32(32–37)% | T2 |
| 생명력 재생 | 10.5(9.1–13)/초 | T3 |

같은 프레임에 **`Omen of Dextral Crystallisation in your inventory has been consumed`**
와 `The Nameless: Omen of Dextral Crystallisation (Complete)` 가 떠 있다 — 이 장화는
주운 것이 아니라 **오멘을 써서 만든 것**이다.

발언(검증본 `verified_asr/boots_roll.txt`):

- `00:01:27` "moon speed perfect" — 이동 속도 접미가 원하는 대로 붙었다
- `00:01:47` "we hope it doesn't remove **armor applies**" — 방어도의 원소 적용 모드를 지키려 한다
- `00:01:53` "**regen** is not great but…" / `00:02:01` "…some pretty good boots now"
- `00:03:42` "That's a lot of armor, that's honestly not a terrible amount of armor"

이 5개 모드는 Lv91 스냅샷의 장화 모드와 일치한다
(`../skadoosh_vod_2875917065_2026-09-17/creator_latest.json`). 즉 **장화 교체는 9/16**,
도약 강타 보조 4개는 9/17 이다(그쪽 README 의 프레임 근거 참조).

## 시청자 빌드 점검 (01:12~01:26) — 그가 남에게 주는 기준

한 시청자의 캐릭터를 화면에 띄우고 하나씩 고쳐 준다. 본인 캐릭터 변경이 아니라
**남의 빌드를 볼 때 그가 무엇부터 보는가**의 기록이다.

- `01:14:15` "You don't have **Guttural War**? Why didn't you have that? It's one of the best
  **Warcry** notes." — 함성 노드 우선순위
- `01:20:28` 장갑으로 저항을 맞출 수 있으면 정신력을 다른 데 쓸 수 있다는 교환 설명
- `01:22:41`~`01:25:59` 주얼: 5접사 주얼 이야기와 "**3 prefix Ruby**" 가 최선이라는 조언

## 타락 함성·토템 스케일링 (02:17:30~02:20:20, 검증본)

- "Corrupting Cry 는 이제 **근접 레벨 기반**이라 내가 포기하는 게 없다"
- "**하드코어라 토템을 그렇게까지 키우지 않는다. 내 주얼 중 딜을 주는 것은 하나도 없다**"
- "Fortifying Cry 가 **Seismic Cry 범위 밖에 놓인 토템의 스파이크도 터뜨린다**"

세 번째는 운영 규칙 후보다(함성 두 개의 범위 관계). 첫 둘은 하드코어 빌드의 성격 —
딜 주얼을 안 쓴다는 것이 Lv91 주얼 6개가 전부 방어/속성인 이유와 맞는다.

## 커버리지 사고 (다음에 또 밟는다)

1차 전사가 **8478.7초까지만** 돌고 `asr_coverage.json` 에 그 길이를 complete 로 적었다.
실제 오디오는 **8635.4초**다 — ffmpeg 가 파일을 마무리하기 전에 `sf.info()` 가 헤더를
읽어서 뒤 157초가 통째로 빠졌다. 오류는 없었다. 조용히 빠진다.

- `transcribe.py` 에 **헤더 길이 vs 파일 크기** 대조 가드를 넣었다(1초 이상 차이 나면 중단).
- 잘린 마지막 창(`chunks/007.json`)을 지우고 재실행해서 8635.4초 · complete `true` ·
  세그먼트 92 로 맞췄다.
- 교훈: `complete_audio_processed: true` 는 **그때 읽은 길이 기준**이라 그 자체로는 근거가 못 된다.

## 산출물

| 파일 | 내용 |
|---|---|
| `chat.json` / `chat.txt` | 채팅 리플레이 74건(29요청, 300초 재시드) |
| `fetch_audio.py` · `audio.wav` | Twitch `Audio_Only` → 16kHz 모노 8635.4초 |
| `chunks/` + `transcript.txt` / `transcript.json` | 1200초 창 8개(겹침 5초), 세그먼트 92 |
| `asr_coverage.json` | 전 구간 처리(`8635.4`, complete `true`) |
| `verified_asr/` | VAD 끈 재전사 3구간 — `boots_roll` · `boots_move_speed` · `corrupting_cry_scaling` |
| `frames/` | 00:01:50 · 00:02:02 · 00:02:10 — 장화 툴팁과 오멘 소모 메시지 |
