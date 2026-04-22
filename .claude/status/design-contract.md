# Design Contract

> UI 작업 시작 전 필수 작성. 모든 필드 값이 채워지기 전까지 UI 파일 Write BLOCK.

## Primary Action:
POE 빌드를 분석해 레벨링 / 장비 / 코칭 가이드를 즉시 받는다 (POB 링크 입력 또는 POE2 구두 빌드 설명)

## Reference URL:
https://mobalytics.gg/poe-2/tier-list

## Accent Color:
#0A84FF

## Font Family:
Pretendard

## Layout Structure (SOP §3):
- Hero: 진입 화면 = TopBar (게임 토글 · 패치 업데이트) + POB 입력창 또는 VerbalBuildInput 폼
- Feature sections: 3 (BuildSummary / LevelingGuide / ChecklistSections — Z-pattern 좌우 교차)
- Showcase sections: 백엔드 주도 앱이라 marketing showcase 없음 (단일 다크 배경)

## Notes:
다크 모드 단일 테마 (POE Rarity 팔레트 + Linear 레이아웃). 한국어 지원 필수. 이번 감사 스코프는 POE2 코치 파이프라인 백엔드 중심 — UI 시각 변경 없음 (defensive guard + VerbalBuildInput 신규 컴포넌트는 기존 ui-card/ui-button 토큰 재사용).
