## Phase 0: Tauri + Python sidecar ✅
- [x] Tauri 프로젝트 초기화
- [x] Python sidecar 연결 (Tauri Command ↔ Python)
- [x] 기존 Python 코드 정리 (19개 살림, 나머지 _archive)
- [x] data/ 폴더 복구

## Phase 1: 빌드 코치 핵심
- [x] POB 파싱 CLI (pob_parser.py URL 인자 추가)
- [x] AI 코치 모듈 (build_coach.py → Claude Sonnet)
- [x] 아키타입 자동 감지 (dot/attack/spell/minion)
- [x] 아키타입별 레벨링/오라/저주 데이터 로드
- [x] 퀘스트 젬 보상 데이터 연동
- [x] Wiki Cargo API 연동 (wiki_data_provider.py)
  - [x] 유니크 드롭 제한/chanceable 조회
  - [x] 디비니 카드 + 드롭 맵 조회
  - [x] 리그 접두어 정규화 (Foulborn 등)
- [x] Tauri UI (빌드 분석 + 코칭 결과 카드)
- [x] print → logger 교체 + UTF-8 인코딩 수정
- [x] 프롬프트 보강 (오라/유틸리티/전령 구간별, 보이드스톤, 장비 타이밍, 10구간)
- [x] UI에 leveling_skills 섹션 표시
- [x] 빌드 평가 5카테고리 별점 (PoE Vault 패턴)
- [x] 장비 진행 타임라인 (슬롯별 카드 흐름)
- [x] 맵 모드 경고 + regex 필터
- [x] 구간별 스냅샷 탭 (Mobalytics 패턴)
- [x] 파밍 전략 (타겟 맵 추천)
- [x] 필터 생성 (SSF 모드 — 디비카/유니크/chanceable/엄격도 Hide/UI)

## Phase 2: OAuth + 프로필 추적
- [ ] GGG OAuth 2.1 연동 (기존 승인 활용)
- [ ] 프로필 상태 읽기
- [ ] 변화 감지 → 전략 자동 조정

## Phase 3: 확장
- [ ] 크래프팅 가이드
- [ ] 보스별 전략
- [ ] Trade 리그 모드 (가격 표시 전환)
- [ ] 수익화 (티어/도네이션)

## 기존 코드 정리
- [ ] 필터 3세대 → Phase 8만 남기고 아카이브
- [ ] 레거시 파일 ~15개 정리
- [ ] 번역 데이터 5개 → merged_translations.json 기준 정리
- [ ] 젬 데이터 이원화 해소 (gems.json 단일 소스)

## Phase F 감사 Fix (2026-04-19 F2+F7 감사 결과)
- [ ] **F7-fix-1 (🔴)** — `data/mod_pool.json` 삭제 (ORPHAN 확정, 3.25 stale). 권고 삭제; 대안 2h로 Wiki Cargo 자동 재생성
- [ ] **F7-fix-2 (🔴)** — `data/id_mod_filtering.json` `_meta` 보강 (source/version/collected_at) + NeverSink 재추출 스크립트 (1h)
- [ ] **F7-fix-3 (🟡)** — `data/t1_craft_bases.json` `_meta` 보강 (version/collected_at/ref_url) (15min)
- [ ] **F7-fix-4 (🟡)** — `sections_continue.py` `HIGH_FOSSILS` / `OILS_*` 출처 주석 보강 (10min)
- [ ] **F2-fix-1 (🟡)** — `_EXCEPTIONAL` / `_UNIQUE_FRAGMENTS` 출처 주석 추가 (30min)
- [ ] **F2-fix-2 (🟡)** — `layer_endgame_content` / `layer_stacked_currency` 스모크 테스트 추가 (15min)
