**지금**: 0.5.5 대응 완료 — 카드 5장 갱신 게시(적대검증 반증 4건 반영), 점화 플래너 첨부, 마샬 웨폰 판정 확정(종소리 지팡이 = 캐스터, 40% 못 받음).

**다음**: ①9/5 패치 후 GGPK 재추출 — 다만 번들 리더가 현재 설치본을 못 읽는다(아래 블로커) ②키타바 PoB 의 얼음의 정화가 스왑 무기에 있는 건이 실제 손실인지 인게임 확인 ③Corrupting Wings PoB 확보(캐시에 없음, mobalytics 봇 403).

**블로커**: POE2 GGPK 번들 리더 실패 — `Path of Exile 2 - poe2_production/Content.ggpk`(6/25자)에서 `_.index.bin`(113MB) 추출까지는 되는데 헤더 파싱이 `chunk_count = -1416675296` 로 죽는다. 4월엔 `C:/Daum Games/Path of Exile2`(127MB 인덱스)로 정상 동작했으나 그 설치본은 삭제됨. `Bundles2/` 루즈 번들도 없어 우회 불가 → 리버싱 필요.

**포인터**:
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·무기 분류·밟은 지뢰) → `.claude/status/poe2_guides.md`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
