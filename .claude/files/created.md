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
