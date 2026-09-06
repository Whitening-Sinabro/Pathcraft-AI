**지금**: 임성빈 화염파 젬링 0.5.5 HC — 사용자가 직접 플레이 중(2026-09-07 기준 2막). 인게임 플래너 5개 + 필터 3단계 설치 완료, 외부 검증 3회차까지 반영 끝. 미해결 없음.

**다음**: ① 추적기가 잡는 변화마다 플래너·사이드카 갱신(15분 주기, scratchpad `sb_track/`) — 갱신되면 `make_hc_gemling_spec.py` → 빌드를 다시 돌려야 필터에 반영된다 ② 채굴본 293건을 사용자용 액트별 시트로 압축(브라우저 페이지 제안해 둠) ③ 커밋 안 함 — 워킹트리에 이번 작업분이 그대로 있다

**블로커**: 없음. 전체 테스트 실패 12 + 에러 16은 전부 POE1 쪽(`filters/Luminary_Bot_SSF_3.29_Progressive.filter` 미빌드)과 알려진 4월본 파생 DB 건이라 이 작업과 무관하다.

**포인터**:
- 젬링 전체 현황(실캐릭 좌표·필터 설계·밟은 지뢰·외부 검증 3회차) → `.claude/status/poe2_hc_gemling.md`
- 방송 채굴본 293건 판정 → `Docs/2026-09-06_SEONGBIN_FLAMEBLAST_GEMLING_0_5_5_LIVE_MINING.md`(읽는 문서) · `..._RAW.json`(원자료)
- Skadoosh 워브링어(버린 빌드) → `Docs/2026-09-05_SKADOOSH_...RESEARCH.md` (참고용으로만)
- 필터 디자인 기준선·Crimson 3축 문법·숨김 게이트 → `.claude/status/poe2_filter_design.md`
- GGPK 추출 운용·재추출 후 처리 목록 → `.claude/status/poe2_ggpk.md`
- 하코 소스 명부 → `.claude/status/poe2_hardcore_sources.md`
- POE2 가이드·필터·카드 파이프라인 → `.claude/status/poe2_guides.md`

**파이프라인 (순서 지킬 것)**:
1. `python scripts/track_poe2_character.py --account dtq03087-0345 --name 임성빈_화염파_젬링 --overview hc-forbidden-rites ...` — 실캐릭 폴링, 플래너 + `.tmp/seongbin/LIVE_ninja_items.json` 갱신
2. `python scripts/make_hc_gemling_spec.py` — 스펙 생성(룰 가림 가드 포함)
3. `python scripts/build_poe2_build_overlay.py --spec ... --stage {campaign,maps,endgame} --allow-drops` → `filters/` → 게임 폴더 복사
4. `python scripts/poe2_filter_coverage.py` — 그가 쓰는 것이 실제로 잡히나(0건이어야 함)
5. `python scripts/poe2_filter_sweep.py --spec ...` — 회귀 0 / 무음에 소리 추가 0
6. `python scripts/annotate_poe2_planner_notes.py` — 플래너 주석(멱등)
