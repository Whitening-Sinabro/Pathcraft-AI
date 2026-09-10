# HC Journey DB (POE2 하드코어 니치)

크리에이터의 **발행 밴드 PoB + 실캐릭 ninja 스냅샷**을 diff 해서 "따라 할 여정"을 자동으로 만들고,
VOD/자막/연구에서 뽑은 **비용·조건·함정·왜(20%)**를 붙이는 SQLite DB. POE2 하드코어(→이후 SSF) 전용.

## 왜 이 구조인가

임성빈 케이스로 검증한 사실: 밴드 PoB diff만으로 **WHAT/WHEN(무엇을 언제 바꾸나)은 자동 100%** 나온다.
자동이 못 주는 것(전환 비용·조건·함정·오프스트림 구매)이 정확히 **HC/SSF가 가장 원하는 것**이라,
그 20%를 `transition_note`로 물리적으로 분리해 담는다.

## 큐레이션은 초반 창에서만 손으로 한다 — 이후는 규칙이 대신한다

손 큐레이션(`source='hand'`)은 DB가 커지면 노동이 안 따라온다. 그래서 **초반 창에 해야 할 일은 손노트를 다는 게
아니라, 그 지식을 `curation_rule`로 뽑아내는 것**이다. 규칙은 한 번 정의되면 이후 **모든 빌드에 자동 적용**된다:

- `keystone` 규칙 — 그 키스톤을 든 빌드에 자동. (예: 혈마법 = 생명력으로 비용 지불)
- `skill_added` 규칙 — 그 스킬을 쓰는 빌드에 자동. (예: 화염파 = 집중 유지형·요구 지능 높음)
- `item_slot_change` 규칙 — 그 슬롯 변화가 있는 빌드에 자동. (예: 세트 II 무기 도입 주의)

**증명:** Skadoosh는 손노동 0인데도 혈마법·선대의 유대 큐레이션을 규칙에서 **공짜로 상속**했다.
즉 초반에 규칙을 쌓아두면, DB가 커진 뒤 새 크리에이터는 큐레이션을 상속만 받는다. 손노동은 **진짜 그 빌드에만
해당하는 것**(정확한 비용 수치·오프스트림 구매 등)으로 줄어든다.

## 스키마 3층 (`schema.sql`)

1. **정본 게임데이터** — (후속) GGPK 파생 연결. 현재 증명본은 미포함.
2. **빌드·스냅샷** — `creator` / `build` / `snapshot` / `snapshot_skill` / `snapshot_item`.
3. **여정** — `transition` + `transition_change`(자동 diff) + `transition_note`(큐레이션 20%).

`game` 컬럼은 'poe2' 고정이나 이후 POE1 포팅 시 데이터만 추가한다.

## 적재 현황 (다중 크리에이터)

- **임성빈** — 젬링 화염파 → 검은화염 카오스 (Gemling Legionnaire). 큐레이션 11건.
- **Skadoosh** — 워브링어 타락 함성 토템 (Warbringer, Ancestral Bond·Blood Magic). 큐레이션 2건(ninja 실측).

두 어센던시가 한 DB에 공존한다. 크리에이터를 늘리면 **자동층(밴드 diff)은 공짜로 커지고, 큐레이션(20%)만 노동**이다.

입력 .build 는 `data/hc_journey/creators/<slug>/` 에 커밋된 픽스처(재현 가능). 크리에이터 추가 = 픽스처 넣고 `CREATORS` 에 한 항목.

## 사용

```
python -X utf8 python/hc_journey/build_db.py --build         # DB 생성 + 전체 적재
python -X utf8 python/hc_journey/build_db.py --query         # 전체 빌드 여정
python -X utf8 python/hc_journey/build_db.py --query --id 2  # 특정 빌드
python -X utf8 -m pytest python/tests/test_hc_journey_db.py -q
```

DB 파일 `data/hc_journey/pathcraft_hc.db`는 적재로 재생성되는 산출물이라 git 제외.

## 규칙 자동 초안 (`rule_autodraft.py`) — 규칙 쓰기 자체를 반자동화

규칙을 손으로 쓰는 것이 마지막 병목이라, 전환점 근처 자막에서 규칙 **후보**를 뽑아 승인 대기 파일로 낸다.

```
python -X utf8 python/hc_journey/rule_autodraft.py            # data/hc_journey/rule_candidates.json
python -X utf8 python/hc_journey/rule_autodraft.py --dry-run  # 요약만
python -X utf8 -m pytest python/tests/test_rule_autodraft.py -q
```

- **전환점** = `build_db` 와 같은 diff(`skill_added`·`item_changed`) + 설정(어센던시·키스톤). trigger_key 는 여기서만 온다.
- **시각 앵커** = 사람 판독(`deliverables/.../precision_findings.py` ROWS 의 (영상, 초, 관측)). 판독의 "N레벨"을 forward-fill 해
  전환 시작 레벨 이전 판독은 버리고, 시간순 앞쪽 클러스터(기본 2개)만 본다.
- **신호** = 앵커 전후 90초 자막에서 cost/condition/pitfall/why/survival 정규식. 후보 text 는 자막 **원문 그대로**.
- **정직성**: 자동 자막은 고유명사가 깨지므로 이름을 자막에서 확정하지 않는다(별칭은 판독 검색 힌트일 뿐).
  같은 자막 창이 여러 트리거에 걸리면(스킬 창 판독은 스킬을 전부 나열) 하나에만 귀속하고 나머지는 `also_matches`.
- **승인 게이트**: `CURATION_RULES` 를 읽기만 한다. 사람이 후보 파일에서 골라 규칙에 옮긴다. 이미 있는 (kind,key,note_type) 은 `existing_rule` 표시.
- 소스는 크리에이터별(`CREATOR_SOURCES`). 소스 없는 크리에이터(Skadoosh)는 후보 0 — 다른 크리에이터의 영상을 빌리지 않는다.

## 다음

- 크리에이터 다수 적재: HC 명부(`.claude/status/poe2_hardcore_sources.md`)의 밴드 PoB·ninja ID 수집.
- 규칙 후보 승인 루프: `rule_candidates.json` 검토 → 채택분을 `CURATION_RULES` 로. 판독(사람 검증 텍스트)도 신호원으로 쓸지 결정.
- 정본 게임데이터(Layer 1) 연결: 스킬/아이템/트리 노드 → GGPK 파생.
- 그다음 UI/API.
