# Phase F legacy 파일 archive

2026-04-19 Phase F 감사 결과 ORPHAN 확정된 6 파일 보관.

## 배경

β-5b 재설계 (2026-04-13)에서 `pathcraft_sections` / `sections_*` 모듈이 삭제되면서
아래 파일들이 프로덕션 경로에서 분리됨. Phase F 감사 (2026-04-19)에서 각각 확인:

| 파일 | 감사 리포트 | ORPHAN 사유 |
|------|-------------|-------------|
| `mod_pool.json` | F7 (`_analysis/mechanic_data_audit_f7.md`) | 3.25 Wiki 스크래핑, 코드 사용처 0 |
| `sanavi_tier_data.json` | F4 (`_analysis/mechanic_data_audit_f4.md`) | 5530 items, DEPRECATED gen_test_filter_v4.py만 사용 |
| `sanavi_tier_parser.py` | F4 | `import sanavi_tier_parser` 0 히트 |
| `farming_mechanics.json` | F3a (`_analysis/mechanic_data_audit_f3a.md`) | 3.27 stale, 코드 사용처 0 |
| `farming_strategies.json` | F3a | 3.27 stale, 코드 사용처 0 |
| `farming_strategy_system.py` (1450 lines) | F3a | import 0 히트 |

## 복구 조건

아래 모두 충족 시 재활용 가능:
1. 현 리그(Mirage 3.28)에 맞춰 데이터 리프레시
2. `_meta.source` + `_meta.version` + `_meta.collected_at` 완비
3. β Continue 아키텍처 (또는 후속)에 통합 계획 문서
4. 자동 재추출 스크립트 (Wiki Cargo / GGPK / NeverSink 필터 파싱 등)

## 복구 없이 영구 삭제해도 될까?

제품 기능 대체 확인:
- **farming_strategy**: UI에 여전히 표시되지만 `build_coach.py` Claude LLM 프롬프트가 동적 생성 (파일 불필요)
- **sanavi tier**: β Continue가 Cobalt + Wreckers + NeverSink 3레퍼런스로 티어링 대체
- **mod_pool**: `id_mod_filtering.json` (NeverSink) + `defense/accessory/weapon_mod_tiers.json` (F0-fix-3 검증)이 실제 사용

대체 소스 확보 완료. 영구 삭제해도 기능 영향 없음 — 단 git history에 남으므로 당장은 archive 유지.
