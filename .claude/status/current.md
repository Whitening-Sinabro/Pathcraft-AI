## 지금
- GGPK 파서 실제 테스트 완료 — 52,927 파일 인덱싱, 번들 구조 확인
- Oodle 디컴프레서(ooz) 바인딩 필요 (번들 안에 .dat64 있음)

## 다음
- ooz FFI 바인딩 (Oodle Leviathan 압축 해제)
- _.index.bin 파싱 (파일 경로 → 번들 위치 매핑)
- .dat64 추출 + 스키마 기반 JSON 변환
- 추출 UI (POE 경로 자동탐지 + 추출 버튼)

## 참조
- [아키텍처](architecture.md)
- [백로그](backlog.md)
- [이관 판단](migration.md)
- [API 연동](api-integration.md)
