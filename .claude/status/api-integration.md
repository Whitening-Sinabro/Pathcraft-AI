## GGG OAuth 2.1
- 승인일: 2025-06-07
- PKCE 기반 인증 + 토큰 자동 갱신
- 기존 구현: src/PathcraftAI.Core/ (C#) — 리빌드 시 재작성

## poe.ninja
- 가격 조회 + 빌드 통계
- 캐싱: 1시간 TTL
- Rate limit: 확인 필요

## POE Trade
- 검색 URL 생성
- Cloudflare 우회 이슈 있었음 (기존 Electron/WebView2로 해결)

## poedb.tw
- 퀘스트 보상, 젬 레벨, 벤더 레시피
- 크롤러 기존 구현 있음 (poedb_crawler.py)
