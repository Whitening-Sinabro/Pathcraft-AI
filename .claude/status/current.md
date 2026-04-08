## 지금
- 스키마 타입 매핑 수정 (enumrow→4B, row/rid→8B)
- 번들 캐시 추가 (같은 번들 반복 해제 방지)
- 문자열 오프셋 버그 수정 (variable_data_start가 마커 위치 기준)
- extract_data CLI 완성 (자동탐지 + .datc64 + JSON 변환, 7/7 성공)

## 다음
- 추출 데이터 활용 (Build Coach에서 게임 데이터 참조)
- 추가 테이블 추출 필요 시 TARGETS 목록 확장

## 블로커
- 없음

## 참조
- [아키텍처](architecture.md)
- [백로그](backlog.md)
- [이관 판단](migration.md)
- [API 연동](api-integration.md)
