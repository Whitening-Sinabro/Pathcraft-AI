## 지금
- 게임 데이터 → Build Coach 연동 완료
- game_data_provider.py: 젬 정보 + 퀘스트 가용 여부를 빌드 기준으로 필터링
- build_coach.py: 게임 데이터 컨텍스트 주입 (폴백: 기존 quest_rewards.json)

## 다음
- 파밍 전략 (타겟 맵 추천 — Maps.json 활용)
- 추가 테이블 추출 필요 시 TARGETS 목록 확장

## 블로커
- 없음

## 참조
- [아키텍처](architecture.md)
- [백로그](backlog.md)
- [이관 판단](migration.md)
- [API 연동](api-integration.md)
