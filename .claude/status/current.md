**지금**: 하코 문서 2종 재작성용 소스 보강 중. 채널 열거로 크리에이터 27편 자막을 확보했고 명부를 열거 기반 실측본으로 갈아엎었다. 본문 집필 전이다.

**다음**: ①어느 빌드부터 쓸지 사용자 결정 대기 — 0.5.5 현행 패치 커버리지가 **바라시타 5명 / 화염파(Flameblast) 젬링 2명 / 방패벽 키타바 0명**으로 갈렸다(명부 "발견 2"). ②미수신 8건 보강(명부 마지막 표 — Blazeworks 방패 좌담·Oscrix 하코 3종·Big Ducks 핸들 미확정 등). ③9/5 패치 후 GGPK 재추출(아래 블로커).

**블로커**: POE2 GGPK 번들 리더 실패 — `Path of Exile 2 - poe2_production/Content.ggpk`에서 `_.index.bin`(113MB) 추출까지는 되는데 헤더 파싱이 `chunk_count = -1416675296` 로 죽는다. 4월엔 `C:/Daum Games/Path of Exile2`(127MB 인덱스)로 정상 동작했으나 그 설치본은 삭제됨. `Bundles2/` 루즈 번들도 없어 우회 불가 → 리버싱 필요.

**포인터**:
- 하코 소스 명부(조사 방법·자막 27편 대응표·"방패벽은 하나의 빌드가 아니다"·미수신 목록) → `.claude/status/poe2_hardcore_sources.md`
- 자막 읽기 → `PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3> [검색어…]`
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·주입 지뢰) → `.claude/status/poe2_guides.md`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
