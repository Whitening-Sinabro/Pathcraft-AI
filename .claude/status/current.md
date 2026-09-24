**지금**: 주 진행 = **Ky 아크 토템 젬링 SC 캐릭**(계정·캐릭터 이름은 로컬 기억 `user_poe2_account_characters.md`). 2026-09-24 **Lv59 에 전환 완료** — poe.ninja 기준 마나 2,944 · 저항 75/75/75/카오스 18 · 유효 체력 8.2k · Arc 9.0k. 요구 63 이하 바탕으로 샀다(투구 Jungle Tiara · 갑옷 Ceremonial Robe · 장갑 Gold Gloves · 신발 Dunerunner Sandals, 링크·수수료 `deliverables/trade_probe/ky_shop63_*.json`). 골드는 SC 리그 공유 — 리스펙 완료로 거의 소진. 지금은 **EasyBabi 탐험 파밍**으로 골드·커런시 모으는 중(가이드 `deliverables/expedition_farming_2026-09-24/index.html`).

**다음**: ① 마법봉 재제작 — 주문·번개·마나 접두 3줄 + 접미 1줄 바탕(`deliverables/trade_probe/ky_wand_rebuild_20260924.json`) → **우측** 결정화 징조 우클릭 활성화 → 완벽한 마술의 에센스 ② 80레벨에 투구·장갑·신발을 원래 바탕(Ancestral Tiara · Sirenscale · Sekhema)으로 교체 ③ SSF 화염파·대재난 스펙의 `custom_sound`(mp3, POE2 무음) → 내장 소리로 교체 후 재빌드 ④ 임성빈/HC 여정 DB 대기 항목은 `.claude/status/poe2_hc_gemling.md` · `hc_creator_sourcing.md`

**블로커**: 없음.

**포인터**:
- 종료 스냅샷(2026-09-25) 포함·제외 목록 → `~/.claude/projects/D--Pathcraft-AI/snapshot_2026-09-25/`(MANIFEST.md · include.txt · exclude.tsv). 제외분(영상·프레임·자막·코퍼스 렌더·벤더 라이브러리·카페 스크랩 등 5,443개)은 디스크에만 있고 git 에 없다
- 젬링·아틀라스 재구성(9/21) → `.claude/status/poe2_hc_gemling.md`
- 필터 디자인·빌더 문법 → `.claude/status/poe2_filter_design.md`
- HC 여정 DB 소싱 → `.claude/status/hc_creator_sourcing.md` · 하코 명부 → `poe2_hardcore_sources.md`
- 패치노트 흡수 → `.claude/status/poe2_patchnotes.md`(다음 조회 `--since 4006357`)
- 가이드·필터·카드 파이프라인 → `.claude/status/poe2_guides.md` · GGPK → `poe2_ggpk.md`

**필터 재생성 규칙**: 빌더를 바꾸면 `data/filter_build_targets/poe2_*.json` 전 스펙을 다시 만들고 `filters/`(git 미추적)와 게임 설치본을 대조. 재현성 테스트(`test_regeneration_is_reproducible`)가 Fartfinder 로 이를 잡는다 — HC-Warbringer 는 `--allow-drops` 필요.
