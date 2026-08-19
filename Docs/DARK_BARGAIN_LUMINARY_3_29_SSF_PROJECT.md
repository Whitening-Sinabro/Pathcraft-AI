# Dark Bargain Intuitive Link Luminary — 3.29 SSF 프로젝트

## 결정

캠페인 설명은 생략한다. 이 프로젝트는 맵 진입 직후부터 시작해 아틀라스, 제작, 각 리그 메커닉, 피나클, T17, 우버를 순서대로 경험하는 Softcore SSF 실험이다.

주력은 `Dark Bargain`이다. `Intuitive Link`를 건 근접 아군이 적을 때리면 `Summon Skeletons`가 적 위치에서 발동하고, 플레이어는 자동 생성된 해골을 Dark Bargain으로 연쇄 폭발시킨다.

이 빌드는 검증 완료된 우버 가이드가 아니다. 공개 원안은 스스로를 미검증 힙스터 빌드라고 표시했으며, 현재 3.29 SSF에서 같은 상호작용을 사용한 리그 스타트 보고까지만 확인됐다. 따라서 각 단계의 종료 조건을 통과할 때만 다음 단계로 간다.

## 세 가지 형태

1. 맵 진입: `Vaal Summon Skeletons + Dark Bargain` 2버튼형
2. 노란/빨간 맵: `Intuitive Link` 자동 해골 공급형
3. 피나클 이후: 7,000+ ES, 회복과 블록을 확보한 CI형

원버튼 엔진이 실패하면 빌드가 실패한 것이 아니다. 즉시 2버튼형으로 돌아가 장비와 아틀라스를 계속 진행한다.

## 첫 아틀라스 순서

1. 맵 수급과 Kirac
2. Essence로 생명력/ES/저항 희귀 장비 제작
3. Ritual에서 지원용 완전체 시체 탐색
4. 용병 노드에서 방어적 근접 지원 용병 탐색
5. Harvest로 저항·속성·ES 제작 보정
6. Betrayal, Expedition, Delve로 제작 기반 확장

## 메커닉 학습 규칙

메커닉 하나에 15~20맵을 배정한다. 해당 블록이 끝나면 다음 네 항목을 기록한다.

- 최종 조우 또는 보스를 완료했는가
- 실패 원인은 피해, 방어, 해골 위치, 링크 대상 AI, 지식 중 무엇인가
- 이 메커닉이 빌드 업그레이드에 실제로 무엇을 주는가
- 다시 전문화할 가치가 있는가

순회 대상은 Abyss, Blight, Breach, Delirium, Expedition, Harvest, Heist, Legion, Ritual, Sanctum, Delve, Ultimatum이다. 이후 일반 피나클과 초대장, T17, 우버로 간다.

## 금지된 지름길

- 공개 PoB의 약 7천만 DPS를 실전 수치로 인용하지 않는다.
- 15 Wither, 충전, Vaal 해골, 용병 오라를 항상 켜진 조건으로 두지 않는다.
- 7,000 ES와 회복 수단 전에 CI로 전환하지 않는다.
- 링크 대상이 죽는 문제를 플레이어 딜 투자로 덮지 않는다.
- 특정 고유 아이템이 나오기 전까지 진행을 멈추지 않는다.

## Pathcraft 사용

```powershell
python python/dark_bargain_luminary_knowledge.py search "루미너리 원버튼 링크가 안 돼"
python python/dark_bargain_luminary_knowledge.py diagnose --state '{"is_ci":true,"energy_shield":5200,"link_trigger_reliable":false,"linked_allies_survive":false}'
python python/dark_bargain_luminary_knowledge.py index --db data/indexes/dark_bargain_luminary_3_29.db
```

정본 데이터는 `data/guide_sources/poe1_dark_bargain_intuitive_link_luminary_3_29_v1.json`이다. 생성되는 SQLite 인덱스는 폐기 가능하며 JSON이 항상 우선한다.
