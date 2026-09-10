**지금**: 임성빈 화염파 젬링 0.5.5 HC — 사용자가 직접 플레이 중(2026-09-07 기준 2막). 인게임 플래너 5개 + 필터 3단계 설치 완료, 외부 검증 3회차까지 반영 끝. 미해결 없음.
HC 여정 DB(`python/hc_journey/`) #1 규칙 자동 초안 완료 + F 자막 재추출 + 판독 신호원 + 후보 68건 판정(`rule_decisions.json`) + `league` 트리거(trade|ssf, 첫 전환 1회) 설계 → 규칙 24건·규칙 노트 40건. 규칙 텍스트 적대검증 3회(오독 2건 수정). 거래소 링크 생성기(`trade_links.py`, 사다리 T1/T2/T3 + 옵션 스탯 필터 + 요구 레벨 상한 + 즉시 구입, 국제/한국) → DB `trade_target/trade_link`. 크리에이터 4명(ds lily·Fubgun 추가, 손노동 0 으로 규칙 67건 상속), 링크 86건.

**다음**: ① 추적기가 잡는 변화마다 플래너·사이드카 갱신(15분 주기, scratchpad `sb_track/`) — 갱신되면 `make_hc_gemling_spec.py` → 빌드를 다시 돌려야 필터에 반영된다 ② 채굴본 293건을 사용자용 액트별 시트로 압축(브라우저 페이지 제안해 둠) ③ 커밋 안 함 — 워킹트리에 이번 작업분이 그대로 있다(HC 여정 DB 파일만 커밋됨) ④ 임성빈 live 매물 수(`trade_links_live_seongbin.json`)가 나오면 DB 재적재로 `trade_link.live_total` 채우기 → 로컬 id T1 이 실제 매물을 찾는지 확인 ⑤ 여정 DB 보류 해제 조건: 보조 젬 선택 트리거, Flask1 별칭(즉시 회복 발언). (유탄 '위에서 떨어뜨리는' 건은 GGPK 로 기각 완료) SSF 규칙은 SSF 소스가 생기면 `league/ssf` 로. 그다음 새 크리에이터 소스(`CREATOR_SOURCES`) 추가

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
