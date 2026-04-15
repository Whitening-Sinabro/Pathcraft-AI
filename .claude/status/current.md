## 지금
- 세션 커밋 완료 (master 29 commits pushed to origin)
- 필터 coverage 감사 완료 — BaseType 매칭 1777 → 1955 (에센스 7티어 + P0 + P1 + Heist Objective)
- Syndicate 탭 (튜토리얼 + 엔진 + Claude Vision)
- 패시브 트리 탭 추가됨 — **현재 iframe 차단 (POE X-Frame-Options: DENY)**
- 테스트 406 passing

## 다음 세션: 패시브 트리 렌더 방식 결정
- iframe 불가 확인됨 (`www.pathofexile.com 연결을 거부`)
- 유저 선택 대기 중 (UX 관점):
  - A. Tauri WebviewWindow — 30분, 별창으로 POE 공식 뷰어 띄움
  - D. 로컬 SVG 렌더 — 3~4시간, `data/skilltree-export/` 에셋으로 탭 내 자체 구현 (오프라인, 앱 통합)
- 현 구현: `PassiveTreeView.tsx` iframe + fallback "새 창" 버튼 (브라우저 열림)
- passive_tree_url 추출 로직은 `App.tsx` useMemo로 구현됨 (progression_stages[].passive_tree_url)

## 다음
- **인게임 검증 필수**: Phase 1-6 변경 + equipment_bases 599 확장 + Awakener's Orb T1 승격 동작 확인
- **Epic 6-Link 사운드 요구**: `6Link.mp3` 파일이 POE Documents 폴더에 있어야 함 (Sanavi 필터 설치 시 자동; 없으면 POE 기본 사운드 fallback)
- 향후 선택: Wreckers 원본 .filter 확보 시 equipment_bases 합집합 재검증 / strictness=4 실사용 피드백

## 블로커
- 없음 (sinabro MCP 글로벌 `.mcp.json` 등록 완료 — 다음 세션 재시작 시 `sv_observe` 툴 로드됨)

## 참조
- [Continue 아키텍처 (β)](continue_architecture.md)
- [아키텍처](architecture.md)
- [필터 분석](filter_analysis.md)
- [Cobalt 분석](../../_analysis/cobalt_filter_analysis.md)
- [Wreckers SSF 분석](../../_analysis/wreckers_ssf_analysis.md)
