**지금**: 하코 문서 2종을 크리에이터 원본 기반으로 재작성 준비 중. 소스 수집·명부 작성까지 끝났고 본문 집필 전이다.

**다음**: ①어느 빌드부터 쓸지 사용자 결정 대기(키타바 방패벽 / 화염파 / 바라시타 — "뭐가 재밌을지 모르겠다"는 상태) ②정한 빌드의 크리에이터를 **여러 명 대조**해 집필(같은 빌드도 내부가 갈린다) ③9/5 패치 후 GGPK 재추출(아래 블로커).

**블로커**: POE2 GGPK 번들 리더 실패 — `Path of Exile 2 - poe2_production/Content.ggpk`에서 `_.index.bin`(113MB) 추출까지는 되는데 헤더 파싱이 `chunk_count = -1416675296` 로 죽는다. 4월엔 `C:/Daum Games/Path of Exile2`(127MB 인덱스)로 정상 동작했으나 그 설치본은 삭제됨. `Bundles2/` 루즈 번들도 없어 우회 불가 → 리버싱 필요.

**포인터**:
- 하코 1차 소스 명부(크리에이터·스트리머·확보 자막·조사 방법 실패 기록) → `.claude/status/poe2_hardcore_sources.md`
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·주입 지뢰) → `.claude/status/poe2_guides.md`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
