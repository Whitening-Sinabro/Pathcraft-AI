## 이관 판단 기록

### Python 모듈 (살림/버림/미판단)

| 모듈 | 판단 | 이유 |
|------|------|------|
| pob_parser.py | 살림 | 핵심. POB 링크 파싱 |
| poe_ninja_api.py | 살림 | 가격→파밍난이도 지표로 전환 |
| llm_provider_factory.py | 살림 | AI 코치 핵심 |
| skill_tag_system.py | 살림 | 스킬 분류/레벨링 |
| korean_stat_mapper.py | 살림 | 한국어 필수 |
| farming_strategy_system.py | 살림 | 파밍 전략, SSF 맞춤 조정 필요 |
| build_tagger.py | 살림 | SSF viable 태깅 |
| offline_mode_provider.py | 살림 | 37개 레벨링 템플릿 |
| filter_generator_service.py (Phase 8) | 살림 | SSF 필터, 정리 필요 |
| build_filter_generator.py (2,087줄) | 아카이브 | Phase 8로 대체 |
| filter_generator.py (1,810줄) | 아카이브 | Phase 8로 대체 |
| smart_filter_generator.py | 버림 | 이미 _legacy |
| poe_oauth.py | 살림 (Phase 2) | GGG 승인 보유 |
| poe_trade_api.py | 버림 | Trade 연동 포기 |
| poe_ladder_fetcher.py | 버림 | 래더 수집 포기 |
| discord_bot.py | 버림 | 별도 프로젝트 |
| poe_qa_collector.py + 크롤러들 | 보관 | 학습 데이터로 잠재 가치 |
| openai_finetuning.py | 보관 | 추후 Fine-tuning용 |

### 신규 모듈 (만들어야 함)

| 모듈 | 역할 |
|------|------|
| wiki_data_provider.py | PoE Wiki Cargo API + Atlas Data API 연동 |
| build_coach.py | AI 코치 오케스트레이터 |
| leveling_guide.py | 레벨링 로드맵 생성 (기존 통합) |

### C# 코드
- 전부 버림 (WPF → Tauri 대체)
- PathOptimizer.cs 로직만 Python으로 포팅 검토

### 데이터
| 파일 | 판단 |
|------|------|
| merged_translations.json | 살림 (canonical) |
| gems.json | 살림 (단일 소스로) |
| gem_levels.json | 보관 (백업) |
| farming_mechanics.json | 살림 |
| base_type_progression.json | 살림 (SSF 핵심) |
| quest_rewards.json | 살림 |
| 107개 빌드 인덱스 | 살림 |
| 15,000 Q&A | 보관 |
| 나머지 번역 4개 | 정리 (merged에 통합 확인 후) |
