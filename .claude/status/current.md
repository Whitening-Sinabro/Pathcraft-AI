**지금**: **하드코어 젬링(화염파+기름 유탄)으로 리그 시작 확정.** 소스 배치는 임성빈=기준 / ds lily=52~93+생존 / fubgun=대조용(레벨링 참고서 아님). 하코 필터 3단계 + 플래너 18개 게임 폴더 설치 완료, 회귀 0. 소프트코어 세트는 레포에만 두고 설치 안 함.

**다음**: ①9/5 05:00 KST 리그 시작 후 GGPK 재추출 → 파생 DB 2종 한 묶음 갱신. ②키타바 하코 문서가 아직 16KB 차이분 문서 — 점화 편처럼 독립 가이드로 재작성. ③하코 문서 2종 구글 닥 공유 설정(현재 제작 계정만 열림).

**알려진 빨간불 1건** (블로커 아님): `test_valid_gems_poe2_categories` — 9/4 GGPK 재추출로 파생 `valid_gems_poe2.json`(4월본)이 낡았다. 재생성은 9/5 0.5.5 재추출 직후 한 번에(`base_items_poe2.json` 의 Runeforged 535종 누락도 같이). 처리 목록 → `.claude/status/poe2_ggpk.md`

**포인터**:
- **하코 젬링 소스 배치·구간별 추천·트리 실측·병합본 재현법** → `.claude/status/poe2_hc_gemling.md`
- GGPK 추출 운용(커맨드·0.5 vs 0.5.5 격차·추출 실패 시 진단 순서·재추출 후 처리 목록) → `.claude/status/poe2_ggpk.md`
- 하코 소스 명부(조사 방법·자막 49편 대응표·0.5.5 버그수정 대조표·핸들 정정표) → `.claude/status/poe2_hardcore_sources.md`
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·주입 지뢰) → `.claude/status/poe2_guides.md`
- 자막 읽기 → `PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3> [검색어…]`
- 산출물 디스코드 전송 → `python scripts/send_to_discord.py --spec <스펙> --planner <접두사> --channel <id>`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
