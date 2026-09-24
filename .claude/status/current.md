**지금**: 주 진행 = **Ky 아크 토템 젬링 SC 새 캐릭**(2026-09-23~). 플래너 17 · 필터 `PathcraftAI_ArcTotem_1~3` 게임 설치(새 빌더로 재생성해도 바이트 일치). 전환은 2단계 — 70 에 6부위, 80 에 투구·장갑·신발. 70 때움 장비 실측 완료(2026-09-24, `deliverables/trade_probe/ky_lvl70_fill_*.json`): 요구 70↓ 로 플래너 06 동급(마나·Local ES·ES%/이속) 투구 928 · 장갑 335 · 신발 1,000건, 바탕 = Sorcerous Tiara · Opulent Gloves · Luxurious Slippers(모두 요구 70).

**다음**: ① SSF 화염파·대재난 스펙의 `custom_sound`(mp3, POE2 무음) → 내장 소리로 교체 후 재빌드 ② 사용자 전환 시점(70)에 쇼핑 링크 정리 — 무기·셉터·의복·목걸이·반지는 `req_filters.lvl.max` 70 ③ 임성빈/HC 여정 DB 쪽 대기 항목은 `.claude/status/poe2_hc_gemling.md` · `hc_creator_sourcing.md` (허락 E/F/G 대기, `annotate_poe2_planner_notes.py` 이름 맵 어긋남)

**블로커**: 없음. `AGENTS.md`·`CLAUDE.md` 의 MCP 연결 규칙 추가분은 외부(사용자/코덱스) 편집이라 미커밋으로 둠.

**포인터**:
- 젬링·아틀라스 재구성(9/21) → `.claude/status/poe2_hc_gemling.md`
- 필터 디자인·빌더 문법 → `.claude/status/poe2_filter_design.md`
- HC 여정 DB 소싱 → `.claude/status/hc_creator_sourcing.md` · 하코 명부 → `poe2_hardcore_sources.md`
- 패치노트 흡수 → `.claude/status/poe2_patchnotes.md`(다음 조회 `--since 4006357`)
- 가이드·필터·카드 파이프라인 → `.claude/status/poe2_guides.md` · GGPK → `poe2_ggpk.md`

**필터 재생성 규칙**: 빌더를 바꾸면 `data/filter_build_targets/poe2_*.json` 전 스펙을 다시 만들고 `filters/`(git 미추적)와 게임 설치본을 대조. 재현성 테스트(`test_regeneration_is_reproducible`)가 Fartfinder 로 이를 잡는다 — HC-Warbringer 는 `--allow-drops` 필요.
