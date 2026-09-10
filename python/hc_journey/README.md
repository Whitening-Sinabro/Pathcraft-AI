# HC Journey DB (POE2 하드코어 니치)

크리에이터의 **발행 밴드 PoB + 실캐릭 ninja 스냅샷**을 diff 해서 "따라 할 여정"을 자동으로 만들고,
VOD/자막/연구에서 뽑은 **비용·조건·함정·왜(20%)**를 붙이는 SQLite DB. POE2 하드코어(→이후 SSF) 전용.

## 왜 이 구조인가

임성빈 케이스로 검증한 사실: 밴드 PoB diff만으로 **WHAT/WHEN(무엇을 언제 바꾸나)은 자동 100%** 나온다.
자동이 못 주는 것(전환 비용·조건·함정·오프스트림 구매)이 정확히 **HC/SSF가 가장 원하는 것**이라,
그 20%를 `transition_note`로 물리적으로 분리해 담는다. 자동층은 재생성·확장 가능, 큐레이션층은 사람이 채운다.

## 스키마 3층 (`schema.sql`)

1. **정본 게임데이터** — (후속) GGPK 파생 연결. 현재 증명본은 미포함.
2. **빌드·스냅샷** — `creator` / `build` / `snapshot` / `snapshot_skill` / `snapshot_item`.
3. **여정** — `transition` + `transition_change`(자동 diff) + `transition_note`(큐레이션 20%).

`game` 컬럼은 'poe2' 고정이나 이후 POE1 포팅 시 데이터만 추가한다.

## 사용

```
python -X utf8 python/hc_journey/build_db.py --build   # DB 생성 + 임성빈 1건 적재
python -X utf8 python/hc_journey/build_db.py --query    # 여정 출력
python -X utf8 -m pytest python/tests/test_hc_journey_db.py -q
```

DB 파일 `data/hc_journey/pathcraft_hc.db`는 적재로 재생성되는 산출물이라 git 제외.

## 다음

- 크리에이터 다수 적재: HC 명부(`.claude/status/poe2_hardcore_sources.md`)의 밴드 PoB·ninja ID 수집.
- 큐레이션 노트 파이프라인: 전환점 자막/VOD 채굴(반자동)로 `transition_note` 채우기.
- 정본 게임데이터(Layer 1) 연결: 스킬/아이템/트리 노드 → GGPK 파생.
- 그다음 UI/API.
