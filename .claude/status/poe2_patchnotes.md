# POE2 패치노트 — 흡수 기록과 영향 판정

받는 법: `python scripts/fetch_poe2_patchnotes.py --since <마지막_thread_id> --pages 2`
원문 캐시: `data/_cache/patchnotes/poe2/<id>_<slug>.txt`(gitignore). 여기엔 **판정만** 남긴다.

**읽는 규칙**: 밸런스 섹션이 없다고 변경이 없는 게 아니다. GGPK 는 Bug Fixes 안에 기능
변경을 섞는다(POE1 3.28 무기 세트 3건 전례). 항목마다 "우리 데이터에 닿나"를 따로 본다.

## 흡수 현황

| 흡수 | 마지막 thread | 다음 조회 기준 |
|---|---|---|
| 2026-09-18 | `4006357` (0.5.5c) | `--since 4006357` |
| 2026-09-05 | `4001365` (0.5.5 Hotfix 5) | — |

## 0.5.5b(9/11) · 핫픽스 6~10 · 0.5.5c(9/18) 판정

**우리 데이터 영향: 없음.** 스킬·밸런스·아이템 베이스 변경 0건. 필터 3단계, 임성빈·
Skadoosh 빌드 데이터, 스펙 어느 것도 재생성이 필요 없다. 리그 관련은 Forbidden Rites 에서
Asinia·Draven 이름 오출력 수정 하나뿐이다.
(미확인: 클라이언트가 패치됐으니 GGPK 추출본과 설치본 버전이 갈렸을 수 있다 —
데이터 변경이 없다는 노트만 보면 재추출은 급하지 않다. 판단 보류.)

### 플레이 규칙이 바뀐 것 (사용자가 하드코어 액트 진행 중)

- **핫픽스 7** — 이미 끝난 Trial of Chaos 에 들어가 어센던시 포인트를 먹던 것 차단.
  **보스가 죽는 순간 인스턴스에 있어야** 포인트를 받는다.
- **0.5.5c** — HC 사망·SSF 이주 후에도 캠페인 Runeseeker 퀘스트의 Runesmithing Knowledge 유지.
- **0.5.5c** — 4막 섬 진입에 Boat Charter 를 Makoru 에게 반납해야 한다.
  *기존 캐릭터는 영향 없음*이라고 명시.
- **0.5.5c** — 세케마 시련 Balbala 에 "아이템 감정" 옵션 추가.

### 엔드게임·파밍

- **0.5.5b** — Expedition 이 엔드게임에서 자연 생성 안 되던 버그 수정 +
  **Expedition·Temple·Delirium 태블릿 드롭률 증가**.
- **핫픽스 10** — Vessel of Kulemak 이 어비스 아틀라스 패시브를 첫 보스 사망이 아니라
  **반지 획득 또는 최종 형태 처치** 시 지급. `Journey to the East` 미드롭 회귀(0.5.5) 수정.
  Unearthed Expedition 몬스터가 태블릿을 못 떨구던 버그 수정.
- **0.5.5c** — Legacy of the Precursors: Origin Spark·Cradle 과 Crisis Fragment 둘 다
  **보스 사망 시 현장에 있어야** 획득. 막혔던 캐릭터는 Arbiter of Ash 처치 후 Doryani 와
  대화해 진행을 푼다.
- **0.5.5c** — Ritual 이연(Deferred) 아이템 비용이 Favour 재굴림마다 다시 오르던 버그 수정.
- **0.5.5c** — Trial of Chaos `Wager of Chaos` 2티어 최소 보상 +1 → **+2**.
- **핫픽스 8** — Expedition Tablet 사용 시 해양 바이옴에 Expedition 3곳이 생기던 버그 수정.

### 나머지

핫픽스 6·9 와 각 노트의 크래시 수정(클라 3+4, 인스턴스 3+2 등)은 우리 쪽 함의 없음.
0.5.5b 의 couch co-op HUD·컨트롤러 탭 정렬 수정도 마찬가지.
