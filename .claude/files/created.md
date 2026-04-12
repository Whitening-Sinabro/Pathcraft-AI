# 생성된 파일 추적

| 파일 | 목적 | 삭제 가능 |
|------|------|-----------|
| src-tauri/src/oodle.rs | Oodle DLL 동적 로더 (OodleLZ_Decompress FFI) | 아니오 |
| src-tauri/src/bundle.rs | POE Bundle 파일 리더 (청크 압축 해제) | 아니오 |
| src-tauri/src/bundle_index.rs | Bundle Index 파서 (파일 매핑 + 경로 복원) | 아니오 |
| src-tauri/src/bin/test_bundle.rs | 번들 파이프라인 실제 테스트 바이너리 | 예 |
| src-tauri/src/bin/extract_data.rs | POE 게임 데이터 추출 CLI (자동탐지 + JSON 변환) | 아니오 |
| python/game_data_provider.py | 추출된 게임 데이터 로더 + 크로스레퍼런스 해결 | 아니오 |
| python/filter_generator.py | 빌드 기반 아이템 필터 생성 (Sanavi 오버레이) | 아니오 |
| python/pathcraft_palette.py | Aurora Glow 팔레트 — 색/상수/헬퍼 (498줄) | 아니오 |
| python/pathcraft_sections.py | Facade — 4개 모듈 re-export (16줄) | 아니오 |
| python/sections_core.py | 코어 빌더 + 엄격도 시스템 (381줄) | 아니오 |
| python/sections_currency.py | 커런시 관련 섹션 (752줄) | 아니오 |
| python/sections_gear.py | 장비/기어 관련 섹션 (2,005줄) | 아니오 |
| python/sections_leveling.py | 레벨링 + 맵 + 기타 (1,066줄) | 아니오 |
| python/sanavi_tier_parser.py | Sanavi 필터에서 카테고리×티어 BaseType 리스트 추출 | 아니오 |
| python/filter_merge.py | POE 필터 오버레이 삽입/Sanavi 탐지 공유 유틸 | 아니오 |
| python/tests/test_pathcraft_palette.py | palette + sections 단위 테스트 (90 케이스) | 아니오 |
| data/sanavi_tier_data.json | Sanavi 실제 tier 데이터 (32 카테고리) 캐시 | 아니오 |
| data/hc_divcard_tiers.json | HC 경제 기반 디비카 티어 데이터 | 아니오 |
| _analysis/cobalt_filter_analysis.md | NeverSink Cobalt 상세 분석 문서 | 예 |
| _analysis/wreckers_ssf_analysis.md | Wreckers SSF 상세 분석 문서 | 예 |
| src/components/FilterPanel.tsx | 필터 생성 UI (엄격도 선택, 디비카/유니크 표시, 다운로드) | 아니오 |
