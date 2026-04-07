## 제품 방향
- **빌드 코치** — 분석기가 아님. "역학 폭발 할 거야" → 레벨 1~엔드게임 전체 로드맵 제공
- HCSSF 기본 전제
- AI = 오케스트레이터 (방향 결정), 시스템 = 실행/검증

## 기술 스택
- 프론트엔드: Tauri + React + TypeScript
- 백엔드: Python sidecar
- AI: Claude (우선)
- 데이터: poe.ninja, PoE Wiki Cargo API, PoE Atlas Data API

## MVP Phases
- Phase 0: Tauri + Python sidecar 연결
- Phase 1: 빌드 코치 핵심 (레벨링, 장비 획득, 파밍, 필터)
- Phase 2: OAuth → 프로필 추적 → 전략 자동 조정
- Phase 3: 크래프팅 가이드, 보스 전략 등 확장

## 확정 결정
- WPF → Tauri 리빌드
- Python 유지 (sidecar)
- 빌드 "생성"이 아닌 "코치" 방향
- 인게임 오버레이 포기
- Electron 포기
- 래더 수집 포기
- POE Trade 직접 연동 포기

## 동작 중인 파이프라인
```
POB 링크 → pob_parser.py → JSON
  → 유니크 추출 → wiki_data_provider.py (Wiki Cargo API)
  → 아키타입 감지 → archetype_*.json 로드
  → 퀘스트 보상 로드
  → build_coach.py → Claude Sonnet → 코칭 JSON
  → Tauri UI 표시
```

## 미확정
- 화면 구성 (탭/원페이지/대시보드)
- 패시브 트리 시각화 방식
- 빌드 검색 소스 (poe.ninja만 vs YouTube 포함)
