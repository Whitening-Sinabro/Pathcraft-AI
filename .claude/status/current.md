**지금**: HC 여정 DB #2 소싱 완료(2026-09-10, 커밋 ffb132a·84721b8). 크리에이터 8(임성빈·Skadoosh·ds lily·Fubgun·탱정·Blazeworks·MisoxShiru·디넬), 규칙 노트 101·거래 링크 770, 손노동 0 상속. 소스 매트릭스 `.claude/status/hc_creator_sourcing.md`(21명, HC 근거 등급 N/S/I, 허락 목록 A~G).
임성빈 화염파 젬링 0.5.5 HC 는 사용자가 직접 플레이 중(플래너 5·필터 3단계 설치, 외부 검증 3회차 반영). 디넬 ninja 폴링은 세션과 함께 끝난다(스냅샷 0).

**다음**: ① **소싱 #2 신규 허락 대기** — `.claude/status/hc_creator_sourcing.md` 허락 목록 **E**(MajorAimless Mobalytics ×3, HCSSF 0.5) · **F**(lolmalice ninja 폴링 + 트위치 VOD 구간 전사, HC 래더 4위). A~D 는 완료(Blazeworks 6밴드·MisoxShiru 7밴드·디넬 1밴드 적재, 크리에이터 8) ② 디넬 폴링(scratchpad `dinel_track/`, 6h, 98렙이라 장비 변화만)이 스냅샷을 남기면 `dinel/` 앞 밴드로 ③ 탱정 0.5.5 실캐릭 4밴드(로컬 xml)는 "같은 사람 두 번째 빌드" 항목 병합 결정 뒤 ④ 신규 허락 **G**(roxTITAN, HC 9위 워리어 스트리머 폴링+VOD)·Graf_Irdis(러시아어) POE2 여부 1회 확인 ⑤ 추적기 변화마다 플래너·사이드카 갱신(`sb_track/`) → `make_hc_gemling_spec.py` → 빌드 재실행 ⑥ 채굴본 293건 액트별 시트 압축 ⑦ 여정 뷰 사용자 피드백. SSF 규칙은 SSF 소스가 생기면 `league/ssf` 로, 새 크리에이터 소스(`CREATOR_SOURCES`) 추가

**블로커**: 없음. 전체 테스트 실패 12 + 에러 16은 전부 POE1 쪽(`filters/Luminary_Bot_SSF_3.29_Progressive.filter` 미빌드)과 알려진 4월본 파생 DB 건이라 이 작업과 무관하다.

**포인터**:
- 젬링 전체 현황(실캐릭 좌표·필터 설계·밟은 지뢰·외부 검증 3회차) → `.claude/status/poe2_hc_gemling.md`
- 방송 채굴본 293건 판정 → `Docs/2026-09-06_SEONGBIN_FLAMEBLAST_GEMLING_0_5_5_LIVE_MINING.md`(읽는 문서) · `..._RAW.json`(원자료)
- Skadoosh 워브링어(버린 빌드) → `Docs/2026-09-05_SKADOOSH_...RESEARCH.md` (참고용으로만)
- 필터 디자인 기준선·Crimson 3축 문법·숨김 게이트 → `.claude/status/poe2_filter_design.md`
- GGPK 추출 운용·재추출 후 처리 목록 → `.claude/status/poe2_ggpk.md`
- 하코 소스 명부 → `.claude/status/poe2_hardcore_sources.md`
- HC 여정 DB 소싱 매트릭스(21명·HC 근거 등급·허락 목록 A~G·래더/팟캐스트 축 결과) → `.claude/status/hc_creator_sourcing.md` · 원자료 `data/hc_journey/sourcing/`
- POE2 가이드·필터·카드 파이프라인 → `.claude/status/poe2_guides.md`

**파이프라인 (순서 지킬 것)**:
1. `python scripts/track_poe2_character.py --account dtq03087-0345 --name 임성빈_화염파_젬링 --overview hc-forbidden-rites ...` — 실캐릭 폴링, 플래너 + `.tmp/seongbin/LIVE_ninja_items.json` 갱신
2. `python scripts/make_hc_gemling_spec.py` — 스펙 생성(룰 가림 가드 포함)
3. `python scripts/build_poe2_build_overlay.py --spec ... --stage {campaign,maps,endgame} --allow-drops` → `filters/` → 게임 폴더 복사
4. `python scripts/poe2_filter_coverage.py` — 그가 쓰는 것이 실제로 잡히나(0건이어야 함)
5. `python scripts/poe2_filter_sweep.py --spec ...` — 회귀 0 / 무음에 소리 추가 0
6. `python scripts/annotate_poe2_planner_notes.py` — 플래너 주석(멱등)
