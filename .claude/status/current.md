## 지금
- β 아키텍처 전환 진행 중 (Wreckers식 Continue 체인)
- β-0~β-5a 완료. `--arch aurora|continue` + `--strictness 0~4` + 빌드 데이터 CLI 병존
- 전 레이어 활성: L0/L1/L2/L3/L5/L6/L7/L8/L9/L10 (L4 SPECIAL_BASE 폐기)
- 블록 수 strictness별 (빌드 없음): 0→45, 1→47, 2→68, 3→86, 4→92
- 빌드 투입 시 L7 BUILD_TARGET + L10 RE_SHOW 동적 생성 (Tabula s=3 → 90)

## β 인게임 시각 검증 주의 (β-1~β-4 interim)
- L1 UpsideDownHouse 아이콘이 모든 아이템에 캐스케이드 (의도된 동작, Wreckers 설계 원본)
- β-2에서 부패/T1 보더 레이어 추가, β-4 카테고리별 최종 아이콘 덮어쓰기까지 **시각적 완성 아님**
- β-1~β-3 인게임 테스트는 "기능 캐스케이드 확인" 목적, "UI 완성도 확인" 아님

## 다음
- β-5b: Aurora 제거 + 구 모듈 삭제 + POB 4개 인게임 검증 (필터 적재 + 시각 검증)
- β-4a: 누락 카테고리 (Quest Items, Unique Tiers, Gold, Essences)
- β-3a (선택): Wreckers 원본 필터 확보 시 장비 베이스 완전 parity

## 블로커
- 없음

## 참조
- [Continue 아키텍처 (β)](continue_architecture.md)
- [아키텍처](architecture.md)
- [필터 분석](filter_analysis.md)
- [Cobalt 분석](../../_analysis/cobalt_filter_analysis.md)
- [Wreckers SSF 분석](../../_analysis/wreckers_ssf_analysis.md)
