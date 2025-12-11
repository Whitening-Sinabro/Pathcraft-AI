# PathcraftAI - Project State Document

> **Last Updated:** 2025-12-09
> **이 파일은 Claude가 매번 작업 시작 전에 참조해야 합니다**

---

## 1. 프로젝트 개요

- **이름:** PathcraftAI
- **설명:** POE1 빌드 검색 및 AI 분석 시스템
- **플랫폼:** Windows Desktop (WPF .NET 8 + Python 3.12)
- **대상:** POE 한국어 사용자
- **GGG 승인:** OAuth 2.1 공식 승인 (2025-06-07)

---

## 2. 완료된 기능 (Phase 1-6)

### Phase 1: POE OAuth 2.1 ✅
- PKCE 기반 인증
- 토큰 자동 갱신

### Phase 2: 사용자 빌드 분석 ✅
- 캐릭터 아이템 파싱
- poe.ninja 가격 조회
- 업그레이드 추천

### Phase 3: YouTube 빌드 검색 ✅
- 40+ 영어 / 11 한국어 스트리머
- POB 링크 자동 추출

### Phase 4: 아이템 가격 시스템 ✅
- poe.ninja 캐싱 (1시간 TTL)
- POE Trade URL 생성

### Phase 5: 고급 기능 ✅
- 한국어 번역 (5,847 아이템 + 21,389 스탯)
- POB 파싱 개선
- 북마크 시스템

### Phase 6: LLM 시스템 ✅
- OpenAI/Claude/Gemini 지원
- AI 빌드 가이드 생성

### Phase 7: 파밍 전략 시스템 ✅
- 리그 페이즈 가이드 (early/mid/late)
- poe.ninja 실시간 가격 연동
- 동적 ROI 기반 스카랍 조합 추천
- 15개 파밍 메카닉 상세 데이터

### Phase 7.2: Q&A 데이터 수집 ✅
- 15,000 Q&A 쌍 수집 시스템
- Reddit/Wiki/Forum/DC Inside/YouTube 크롤러
- 템플릿 기반 고품질 Q&A 생성기 (5,000개)
- OpenAI JSONL 형식 자동 변환

### Phase 8: 필터 시스템 클린 아키텍처 🚧 (IN PROGRESS)
**시작일:** 2025-11-28

**Phase 8.1: Domain Layer** ✅ (COMPLETED - 2025-11-28)
- Domain Models 구현 (Build, FilterRule, ItemPriority)
- Domain Interfaces 정의 (IBuildParser, IPriceProvider)
- Domain Services 구현:
  - ItemPriorityCalculator - 아이템 우선순위 계산
  - ColorSchemeResolver - 색상 스키마 (SINGLE SOURCE OF TRUTH)
  - FilterRuleBuilder - 필터 규칙 생성
- **Divine Orb 색상이 1곳에서만 정의됨** (ColorSchemeResolver.TIER_COLORS)

**Phase 8.2: Infrastructure Layer** ✅ (COMPLETED - 2025-11-28)
- POBParser 구현 (IBuildParser 인터페이스 구현체)
  - POB XML 파일, pastebin, pobb.in URL 파싱
  - Domain Model 변환 (Build, BuildItem)
- NinjaPriceProvider 구현 (IPriceProvider 인터페이스 구현체)
  - poe.ninja 캐시 데이터 로드 (1,368 유니크, 446 점술 카드)
  - 가격 조회, 티어 결정, 고가 아이템 필터링
- FilterFileWriter 구현
  - FilterRule → .filter 파일 작성
  - 우선순위 정렬, 섹션 구분, 헤더 생성
- **End-to-End 통합 테스트 통과** (213 priorities → 16 rules → 4.8KB filter)

**Phase 8.3: Application Layer + SSF Support** ✅ (COMPLETED - 2025-11-29)
- **SSF 필터 분석 및 기준점 설정**
  - SSF 필터 패턴 분석 완료 (SSF_FILTER_ANALYSIS.md)
  - NeverSink 8.18.1a 필터 분석 (Flask progression: Small@15, Medium@30, Greater@48)
  - "모든 것에 기준점" 철학 문서화
- **base_type_progression.json** (5,400+ 라인)
  - Flasks (Life/Mana/Utility) with Trade/SSF/HC_SSF thresholds
  - Weapons (1H Swords, 2H Swords, Bows, Wands, Staves)
  - Armour (Body, Helmets, Gloves, Boots, Shields)
  - Jewellery (Amulets, Rings, Belts)
  - SSF 안전 마진: +5 levels, HC SSF +10 levels
- **ProgressiveStrictnessService**
  - SSF/Trade/HC_SSF 게임 모드 지원
  - AreaLevel 기반 점진적 숨김 로직
  - 특수 케이스 처리 (Influenced, Quality, 6-Link/Socket)
  - "의심스러우면 표시" 원칙 구현
- **BuildAnalysisService**
  - 빌드 테마 감지 (chaos_dot, physical_melee, elemental_caster, minion_summoner, bow_attack)
  - 데미지 타입 추출 (Physical, Fire, Cold, Lightning, Chaos)
  - 필요 스탯 추론 (Strength, Dexterity, Intelligence)
  - 키 유니크 식별 및 추천 베이스 타입 제안
- **FilterGeneratorService** (메인 오케스트레이션)
  - 전체 레이어 협력 관리 (Domain → Infrastructure → Application)
  - POB 파싱 → 빌드 분석 → 우선순위 계산 → 필터 생성 플로우
  - 점진적 숨김 규칙 통합
  - FilterGenerationRequest/Result DTOs
- **테스트 결과**: ProgressiveStrictnessService, BuildAnalysisService 검증 완료

**Phase 8.4: Migration (기존 코드베이스 통합)** ✅ (COMPLETED - 2025-11-29)
- **filter_generator_cli.py** (새 CLI 엔트리포인트)
  - FilterGeneratorService 기반 필터 생성
  - 레거시 CLI 인자 호환성 (--output, --league, --name, --summary)
  - 새 인자: --mode {trade,ssf,hc_ssf}, --area-level, --progressive, --strictness
  - --summary 플래그: 빌드 요약만 출력
  - --name 플래그: 커스텀 파일명 지정
- **C# WPF 통합** (MainWindow.xaml.cs)
  - Line 101: `build_filter_generator.py` → `filter_generator_cli.py` 교체
  - Line 1923: 기본 인자 `--mode ssf --phase EarlyMap --area-level 68`
  - Line 2002: 동일한 인자 적용 (필터 생성 2개 위치)
- **Styling 객체 생성 버그 수정** (filter_generator_service.py)
  - Line 222-227: Gems rule Styling 수정
  - Line 238-243: Divination Cards rule Styling 수정
  - Line 254-259: Maps rule Styling 수정
  - resolve_for_tier() dict 키 매핑: text→text_color, border→border_color, background→background_color
- **마이그레이션 대상 파일 (향후 제거 예정)**
  - build_filter_generator.py (2,087 lines)
  - filter_generator.py (1,810 lines)
  - smart_filter_generator.py (439 lines)
  - **총 4,336 라인의 레거시 코드**

**Phase 8.5: Cleanup & Testing** ✅ (COMPLETED - 2025-11-29)
- **테스트 결과 모두 통과**
  - ProgressiveStrictnessService: Flask hiding, Quality override, Influenced items ✅
  - BuildAnalysisService: chaos_dot, physical_melee, minion_summoner 테마 감지 ✅
  - FilterGeneratorService: 211 priorities → 18 rules → 5.3KB filter ✅
  - C# WPF 빌드: 경고 0, 오류 0 ✅
- **레거시 코드 정리** (`_legacy/` 폴더로 이동)
  - build_filter_generator.py (92KB)
  - filter_generator.py (75KB)
  - smart_filter_generator.py (17KB)

**Phase 8.6: GemDataLoader Service** ✅ (COMPLETED - 2025-11-29)
- **GemDataLoader** (`domain/services/gem_data_loader.py`)
  - gems.json에서 552개 젬 로드 (338 액티브, 214 서포트)
  - 태그 기반 데미지 타입 추출 (fire, cold, lightning, chaos, physical)
  - 태그 조합 기반 빌드 테마 추론 (chaos_dot, fire_dot, minion_summoner 등)
  - 특수 DoT 스킬 처리 (Righteous Fire, Scorching Ray 등)
  - 싱글톤 패턴으로 데이터 캐싱
- **BuildAnalysisService 개선**
  - SKILL_DAMAGE_MAP (17개 하드코딩) → GemDataLoader (338개 동적) 전환
  - `_detect_damage_types()`: 태그 기반 + 서포트 젬 분석
  - `_determine_build_theme()`: 태그 조합 + DoT 감지 + 폴백 로직
  - `_detect_playstyle()`: 태그 기반 mine/trap/totem/minion 감지
- **테스트 결과**
  - RF Juggernaut → fire_dot ✅
  - ED/C Trickster → chaos_dot ✅
  - Lightning Strike → physical_melee ✅ (projectile과 구분)
  - SRS Necro → minion_summoner ✅ (DoT보다 minion 우선)
  - Tornado Shot → bow_attack ✅

**Phase 8 완료!** Clean Architecture 필터 시스템 전체 구현 완료

### Phase 9: LLM 레벨링 가이드 시스템 ✅ (COMPLETED - 2025-11-30)
**목표**: POB Notes 기반 LLM 레벨링 가이드 생성 (Claude/GPT/Gemini)

**구현 파일 (Python)**:
- **llm_provider_factory.py** - Multi-LLM 프로바이더 팩토리
  - ClaudeProvider (claude-sonnet-4-20250514)
  - OpenAIProvider (gpt-4o-mini)
  - GeminiProvider (gemini-1.5-flash)
  - LLMResponse dataclass (content, tokens, elapsed_seconds)
- **build_context_builder.py** - POB → LLM 컨텍스트 변환
  - BuildContext dataclass (스킬, 장비, 스탯, 저항, 키스톤)
  - 스킬 자동 분류 (AURA_SKILLS, TRIGGER_SUPPORTS, MOVEMENT_SKILLS)
- **prompt_builder.py** - 레벨링 가이드 프롬프트 생성
  - LEVELING_SYSTEM_PROMPT (JSON 스키마 정의)
  - BUILD_ANALYSIS_SYSTEM_PROMPT
  - parse_leveling_response() JSON 파서
- **cache_manager.py** - SQLite 캐싱 (7일 TTL)
  - compute_hash() - 빌드 해시 생성
  - get_any_provider() - 프로바이더 무관 캐시 조회
  - get_expired() - 만료 캐시 폴백
- **llm_usage_tracker.py** - 사용량 추적 (수정)
  - 티어: free(0회), premium(40회/월), expert(100회/월)
  - check_limit(), get_remaining_usage()
- **leveling_guide_llm.py** - 통합 CLI 스크립트
  - LevelingGuideGenerator 클래스
  - generate_from_url(), generate_from_xml()
  - --provider, --user, --json 옵션

**구현 (C# WPF)**:
- **MainWindow.xaml.cs** (4280-4500 라인)
  - _useLLMLevelingGuide = true (기본 활성화)
  - _llmProvider = "gemini" (기본 프로바이더)
  - RunLLMLevelingGuide() - Python 스크립트 호출 (60초 타임아웃)
  - DisplayLLMLevelingGuide() - 결과 UI 표시
  - 폴백: LLM 실패 시 skill_tag_system.py 사용

**아키텍처**:
```
C# WPF UI
    │
    ▼
leveling_guide_llm.py (CLI)
    │
    ├── LLMProviderFactory (Claude/GPT/Gemini)
    ├── BuildContextBuilder (POB → Context)
    ├── PromptBuilder (프롬프트 생성)
    ├── CacheManager (7일 TTL)
    └── UsageTracker (월별 제한)
```

**환경 변수 (필요)**:
- ANTHROPIC_API_KEY (Claude)
- OPENAI_API_KEY (GPT)
- GOOGLE_API_KEY 또는 GEMINI_API_KEY (Gemini)

---

## 3. 현재 핵심 이슈 (Critical)

### ✅ 모든 핵심 이슈 해결 완료 (Phase 1)

**Phase 1 완료 (2025-11-25):**
- ✅ 데이터 정확도 검증 및 수정 (682개 오류 수정)
- ✅ LLM 사용량 추적 시스템 구현
- ✅ RAG System v2 구현 (Multi-model support)
- ✅ Gemini API 통합 (라이브러리 설치 완료, API key 필요)

**상세 보고서**: [`Docs/Phase1_Completion_Report.md`](Docs/Phase1_Completion_Report.md)

---

## 3.1 해결된 이슈들

### 3.1.1 데이터 정확도 문제 ✅ 해결됨
**문제**: gem_levels.json에서 682개 데이터 오류 발견
- Cleave: 1 → 20 (19 레벨 차이!)
- Glacial Hammer: 1 → 28 (27 레벨 차이!)
- Armageddon Brand: 28 → 12 (16 레벨 차이!)

**해결** (2025-11-25):
- `validate_gem_data.py` 생성 - POB 데이터와 교차 검증
- 682개 오류 자동 수정 (381 HIGH, 15 MEDIUM, 286 LOW severity)
- gem_levels.json 업데이트 (549 → 763 gems, 100% accuracy)

### 3.1.2 LLM 비용 폭주 위험 ✅ 해결됨
**문제**: "Expert Unlimited" 티어 = 파산 위험
- 100 users × 1,000 requests × $0.003 = $300/month cost

**해결** (2025-11-25):
- `llm_usage_tracker.py` 구현 - SQLite 기반 사용량 추적
- 티어별 제한: Free (Gemini, 무제한) / Supporter (GPT, 100/월)
- 자동 fallback: 한도 초과 시 Gemini로 자동 전환
- Cost monitoring: 월별 사용량, 비용 추적

### 3.1.3 skill_tag_system.py 하드코딩 ✅ 해결됨 (이전)
**해결 완료 (2025-11-22):**
- gems.json에서 338개 액티브 스킬 동적 로드
- 태그 기반 자동 분류

### 3.1.4 레벨링 가이드 부정확 ✅ 해결됨 (이전)
**해결 완료 (2025-11-23):**
- poedb.tw 크롤러로 퀘스트 보상, 젬 레벨 데이터 수집
- required_level 기반 필터링 추가

### 3.1.5 필터 생성 오류 ✅ 해결됨 (이전)
**해결 완료 (2025-11-23):**
- HasInfluence, Class 문법 수정
- NeverSink 형식에 맞게 조정

---

## 4. 데이터 소스 정책

### ✅ 사용 가능
1. **POB 데이터** - 젬/스킬 정보 (최우선)
2. **poe.ninja API** - 가격 정보 (이미 사용 중)
3. **POE 공식 API** - OAuth, 캐릭터 (이미 사용 중)
4. **poedb.tw** - 한국 커뮤니티 DB
5. **GGPK 추출** - 게임 데이터 직접 추출

### ❌ 사용 금지
1. **RePoE** - 업데이트 중단됨 (절대 사용 금지)
2. **PyPoE** - 3년 이상 미관리
3. **POE2 데이터** - POE1만 지원

---

## 5. 데이터 파일 현황

### 사용 중인 파일 (`src/PathcraftAI.Parser/data/`)
```
merged_translations.json      # 한국어 번역 (주요)
awakened_translations.json    # Awakened POE Trade
poe_trade_korean.json        # Trade API 한국어
korean_dat_data.json         # GGPK 추출 데이터
update_cache.json            # 버전 캐시
farming_strategies.json      # 파밍 전략 데이터 (수익, 스카랍 조합)
farming_mechanics.json       # 15개 파밍 메카닉 상세 정보
```

### poedb.tw 크롤링 데이터
```
quest_rewards.json           # 퀘스트 보상 (128개 퀘스트, 클래스별)
gem_levels.json              # 젬 required_level (549개 젬)
vendor_recipes.json          # 벤더 레시피 (201개)
```

### 빌드 전환 패턴 (NEW)
```
build_transition_patterns.json  # Reddit 크롤링 65패턴 (레벨링 → 최종 스킬)
```

### 가이드 템플릿 (`src/PathcraftAI.Parser/data/guide_templates/`)
```
common_template.json              # 공통 레벨링 템플릿
archetype_spell.json              # 스펠 캐스터 아키타입
archetype_attack.json             # 공격 빌드 아키타입
archetype_minion.json             # 소환 빌드 아키타입
archetype_dot.json                # DOT 빌드 아키타입
builds/spell_brand_penance_inquisitor.json  # ZeeBoub Penance Brand 가이드
```

### 게임 데이터 캐시 (`game_data/`)
- base_types.json (24.8MB) - 22,460 베이스 아이템
- poe.ninja 캐시 파일들
- **base_type_progression.json** (NEW - Phase 8.3) - 점진적 필터 숨김 데이터
  - Flasks (Life/Mana/Utility) AreaLevel 임계값
  - Weapons/Armour/Jewellery 베이스 타입 티어링
  - SSF/Trade/HC_SSF 모드별 안전 마진

### POB 데이터 (NEW - `game_data/`)
```
mods.json              # 13,289개 아이템 모드 (prefix/suffix, 가중치, 태그)
uniques.json           # 1,236개 유니크 아이템 (모드, 레벨 요구, 베이스)
item_bases.json        # 1,061개 베이스 아이템
gems.json              # 552개 스킬젬 (태그, 스탯 요구사항)
essence.json           # 104개 에센스
pantheons.json         # 12개 판테온
cluster_jewels.json    # 클러스터 주얼 설정
```

### POB 저장소 (`pob_repo/`)
- POB GitHub 클론 (git pull로 업데이트)
- `python game_data_fetcher.py --clone` 으로 설치
- `python game_data_fetcher.py --parse-all` 로 JSON 생성

### Phase 1 시스템 파일 (NEW - `src/PathcraftAI.Parser/`)
```
llm_usage_tracker.py        # LLM 사용량 추적 시스템 (SQLite 기반)
rag_system_v2.py             # Multi-model RAG (OpenAI GPT + Gemini)
validate_gem_data.py         # 데이터 검증 및 자동 수정 도구
simple_rag_test.py           # 컴포넌트 테스트 스크립트
data/usage.db                # 사용량 추적 DB
data/unified_database.json   # 통합 데이터베이스 (1,634 entries)
data/vector_db/              # ChromaDB 벡터 데이터베이스
```

---

## 6. 기술 스택

### Frontend
- WPF (.NET 8 / C#)
- WebView2 (POE Trade 연동)

### Backend
- Python 3.12
- SQLite (북마크)

### 외부 API
- YouTube Data API v3
- poe.ninja API
- POE Official API

---

## 7. 다음 작업 우선순위

### 높음 (이번 주)
1. ~~quest_rewards.json 데이터 구조 수정~~ ✅ 완료
2. ~~레벨링 가이드에 퀘스트 보상 데이터 연동~~ ✅ 완료
3. ~~UI에 필터 생성 기능 통합~~ ✅ 완료 (My Build 탭에서 분석 후 표시)
4. ~~Leveling 3.27 필터 셉터 숨김~~ ✅ 완료 (DoT 빌드용)
5. **Phase 8.4 - 클린 아키텍처 Migration** 🔄 진행 예정
   - 기존 필터 생성 코드를 새 아키텍처로 마이그레이션
   - WPF UI에서 FilterGeneratorService 호출
   - 기존 BuildFilterGenerator, CustomLevelingFilter 제거

### 중간
6. 필터 유효성 검사 및 테스트
7. poe.ninja 가치 규칙 베이스 타입 매핑 개선

### 낮음
7. ~~Electron 모듈 (Stage 3)~~ ✅ 기본 구현 완료
8. 오버레이 UI

---

## 7.1 POE Trade 3단계 (Electron 모듈) ✅

**구현 완료 (2025-11-23):**

**파일 구조:**
```
src/PathcraftAI.Electron/
├── package.json           # 프로젝트 설정, 의존성
├── README.md              # 사용 가이드
└── src/
    ├── main.js            # Electron 메인 프로세스
    └── preload.js         # 보안 브릿지

src/PathcraftAI.UI/
└── ElectronService.cs     # C# IPC 클라이언트
```

**주요 기능:**
- Lazy Loading: 필요시에만 Electron 프로세스 시작
- 메모리 모니터링: 800MB 임계치 초과 시 자동 정리/종료
- 자동 종료: 5분 미사용 시 자동 종료
- 3단계 캐시 시스템: Hot (1분) / Warm (5분) / Cold (30분)
- JSON-RPC IPC: TCP port 47851

**IPC 메서드:**
- `ping`, `show`, `hide`, `navigate`, `search`
- `getMemory`, `getCache`, `clearCache`, `setCache`, `getCacheItem`
- `setLeague`, `shutdown`

**사용법:**
```csharp
var electron = new ElectronService();
await electron.StartAsync();
await electron.SearchAsync("Keepers", itemName: "Headhunter");
```

**설정 (CONFIG):**
- IPC_PORT: 47851
- MEMORY_THRESHOLD_MB: 800
- IDLE_TIMEOUT_MS: 5분
- CACHE_CLEANUP_INTERVAL: 1분

---

## 8. 주요 파일 위치

```
MainWindow.xaml(.cs)         # UI 메인
skill_tag_system.py          # 스킬 태그 (동적 로드)
filter_generator.py          # 필터 생성
build_filter_generator.py    # POB 기반 3단계 필터 (--color-preset 지원)
filter_visual_rules.py       # 필터 색상 규칙 (HSV 변환, 프리셋 적용, get_preview_items)
filter_visual_config.json    # 필터 색상/사운드 설정 (color_presets, build_themes)
pob_base_extractor.py        # POB 베이스 타입 추출 (extract_base_type 함수)
pob_data_extractor.py        # POB 통합 데이터 추출 (리그 모드, 유니크, Graft)
build_chat.py                # AI 빌드 대화 시스템 (테마 변경, 빌드 조언)
filter_validator.py          # 필터 문법 검증 (POE 규칙, NeverSink 키워드)
GameDataExtractor.cs         # GGPK 추출
Dat64Parser.cs               # DAT64 파싱
poe_ninja_api.py             # 가격 캐싱 (리그 자동 감지)
league_service.py            # POE 리그 자동 감지 (공식 API 사용)
farming_strategy_system.py   # 파밍 전략 (poe.ninja 연동)
poedb_crawler.py             # poedb.tw 크롤러 (퀘스트, 젬, 레시피)
game_data_fetcher.py         # POB 데이터 수집 (--clone, --parse-all)
item_recommendation_engine.py # 동적 아이템 추천 (빌드 분석 → 모드 매칭 → 가격 최적화)
build_pattern_crawler.py     # 빌드 전환 패턴 크롤러 (Reddit, GitHub)
poe_qa_collector.py          # Fine-tuning Q&A 수집 메인 (15,000 Q&A)
openai_finetuning.py         # OpenAI GPT-3.5 Fine-tuning 파이프라인
llm_usage_tracker.py         # LLM 사용량 추적 시스템 (Phase 1)
rag_system_v2.py             # Multi-model RAG (GPT + Gemini) (Phase 1)
validate_gem_data.py         # 데이터 검증 및 수정 도구 (Phase 1)
```

---

## 9. 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2025-12-11 | **패시브 트리 저장/불러오기 + 최적 경로 계산 구현** - (1) PassiveTreeUrlCodec.cs: POB URL 포맷 v6 호환 인코더/디코더 (Base64URL, 클래스/어센던시/노드/클러스터/마스터리 지원), (2) PathOptimizer.cs: Dijkstra 알고리즘 기반 최적 경로 계산 (Steiner Tree 근사, 그리디 알고리즘으로 다중 목표 노드 경로 계산, 연결성 검증), (3) PassiveTreeViewer.xaml.cs: ExportToUrl/ImportFromUrl/CalculateOptimalPath/AllocateOptimalPath API 추가, (4) **WebView vs 자체구현 분석 결과**: WebView는 저장/불러오기는 가능하나 최적 경로 계산 불가 (공식 사이트 JavaScript API 미제공), **자체구현 방식 채택** |
| 2025-12-09 | **테스트 버전 + 인스톨러 + 도네이션 통합 완료** - (1) ai_build_analyzer.py: LLM 사용량 제한 체크 통합 (test_version_config.py 연동, LLM_LIMIT_EXCEEDED 에러 코드, 무료 사용자 3회/일 제한), (2) MainWindow.xaml.cs: LLM 제한 초과 시 Ko-fi 도네이션 안내 표시, (3) PathcraftAI.iss 검증 완료 (Inno Setup 스크립트, 한/영 양국어, Python 자동 감지/설치), (4) AutoUpdater.NET 패키지 추가 + AutoUpdateService.cs 검증 (GitHub update.xml 기반 업데이트), (5) kofi_donation_handler.py 검증 완료 (도네이션 등록/검증 시스템, 티어 업그레이드), (6) TierWindow.xaml/cs 검증 완료 (구독 관리 UI, Ko-fi/BMC/GitHub Sponsors 버튼), **플랜 100% 완료 (테스트 버전 기능 + 인스톨러 + 도네이션)** |
| 2025-12-09 | **Phase C: 데이터 동기화 시스템 완료** - (1) cache_sync.py: GitHub 기반 빌드 데이터 동기화 (GZIP 압축 JSON, 민감 정보 해시화, 병합 전략 newer/skip/all, GitHub Release 다운로드), (2) .github/workflows/sync-builds.yml: 자동 동기화 워크플로우 (하루 2회 cron, 수동 실행 지원, Release 자동 배포), (3) test_cache_sync.py: 16개 테스트 통과 (해시화, 정제, 내보내기, 가져오기, 병합 전략, 라운드트립), (4) google_build_scraper.py 삭제 (플랜에 없는 작업 정리), **Phase C 데이터 동기화 완료 (플랜 순서: Phase A→B→C 완료)** |
| 2025-12-09 | **Phase B: 스트리머 빌드 트래커 완료** - (1) data/streamer_accounts.json: 24개 스트리머 계정 목록 (영어 18개 + 한국어 6개, tier/priority/pob_sources/specialties 포함, rate_limit 설정), (2) streamer_build_tracker.py: 스트리머 빌드 정기 수집 시스템 (StreamerAccount 모델, POB 링크 추출, rate limiting, 티어/우선순위 필터링, CSV/JSON 내보내기), (3) build_snapshot_service.py: 스냅샷 비교/히스토리 서비스 (SnapshotDiff 모델, 젬/장비/키스톤/스탯 비교, 변경 요약 생성, 유사 빌드 검색, 스킬 분포 통계), (4) test_streamer_tracker.py: 16개 테스트 통과 (StreamerBuildTracker 6개 + BuildSnapshotService 9개 + Integration 1개), **Phase B POB 데이터 수집 강화 완료 (models/build_snapshot.py, cache_manager.py build_snapshots 테이블, test_build_snapshot.py 15개 테스트)** |
| 2025-12-09 | **Phase A.3: 레벨링 템플릿 확장 (12→37)** - (1) offline_mode_provider.py: 20개 신규 레벨링 템플릿 추가 (spectral_helix, raise_spectre, skeleton_mages, blade_vortex, lacerate, earthquake, boneshatter, ice_nova, flameblast, detonate_dead, blazing_salvo, eye_of_winter, ball_lightning, storm_brand, divine_ire, ice_spear, herald_of_agony, exsanguinate, reap, soulrend), (2) ARCHETYPE_TO_TEMPLATE 매핑 확장 (12→40개, archetype_standards.json 35개 아키타입 커버), (3) test_leveling_templates.py: 24개 테스트 작성 (템플릿 개수/필드 검증, 한/영 팁 검증, 매핑 유효성, 가이드 생성, 신규 템플릿 검증), **테스트 24/24 통과 (100%)** |
| 2025-12-09 | **Phase 3단계: WPF UI 프리미엄 분석 통합** - (1) MainWindow.xaml: AI 분석 섹션에 프리미엄 분석 유형 콤보박스 (Full/Upgrade/Defense/Offense/Leveling/Quick) + 티어 배지 (FREE/PREMIUM/EXPERT 색상 구분) + 커스텀 질문 입력 패널 + Premium 분석 버튼 추가, (2) MainWindow.xaml.cs: PremiumAnalysis_Click/DisplayPremiumAnalysis/UpdateTierBadge 메서드 추가 (프리미엄 분석 호출, 결과 표시, 티어 UI 업데이트), (3) PythonBridgeService.cs: AnalyzeBuildPremiumAsync/GetTierInfoAsync/GetTierComparisonAsync/CheckDailyLimitAsync 메서드 추가 (Python analysis_tier_manager.py 연동), (4) analysis_tier_manager.py: CLI 인터페이스 확장 (--tier-info, --tier-comparison, --check-limit, --premium, --build-file), (5) test_premium_analysis_e2e.py: 29개 E2E 테스트 작성 (PremiumPromptBuilder 12개 + AnalysisTierManager 12개 + Integration 5개), **빌드 성공 (0 에러), 29/29 테스트 통과 (100%)** |
| 2025-12-09 | **Phase 2단계: 유료 분석 강화** - (1) premium_prompt_builder.py: 무료 분석 결과 + 아키타입 표준을 LLM에 전달하는 고급 프롬프트 빌더 (full/upgrade/defense/offense/leveling 분석 유형, 토큰 예상 기능), (2) ai_build_analyzer.py 확장: analyze_build_premium() 함수 추가 (자동 무료 분석 → 프리미엄 프롬프트 → LLM 심층 분석), --provider premium --analysis-type 옵션, (3) analysis_tier_manager.py: FREE/PREMIUM 티어 관리자 (기능별 분기, 일일 사용량 추적 50회/일, 티어 비교 UI 데이터), **빌드 성공 (0 에러), 테스트 통과** |
| 2025-12-09 | **테스트 버전 배포 준비** - (1) test_version_config.py: 테스트 버전 관리 시스템 (FREE/EARLY_SUPPORTER/FOUNDER 티어, LLM 3회/일 제한, 30일 테스트 기간, Ko-fi 연동), (2) MainWindow.xaml: Beta 배너 UI (노란색 배너, 버전/남은일수/LLM횟수 표시, Ko-fi 버튼), (3) MainWindow.xaml.cs: UpdateBetaBanner() 메서드 (Python 상태 조회, 동적 UI 업데이트), (4) installer/PathcraftAI.iss: Inno Setup 6 스크립트 (영어/한국어 양국어, Python 감지, 자동 의존성 설치, Beta 경고), (5) installer/build-installer.ps1: 빌드 자동화 스크립트 |
| 2025-12-09 | **코드 정리: 래더 수집 코드 삭제** - (1) poe_ladder_fetcher.py, ladder_cache_builder.py, ladder_item_filter.py 삭제 (70% 비공개 프로필로 인한 낮은 효용성), (2) poe_api_utils.py 생성 (API 유틸리티 함수 분리: get_character_items, get_character_passive_skills, parse_build_data, get_ladder), (3) build_search_manager.py, popular_builds_precacher.py, poe_ninja_build_scraper.py, streamer_builds.py import 업데이트 |
| 2025-12-08 | **Phase 9: 수익화 준비 + Discord 봇** - (1) TierWindow.xaml/cs: 구독 티어 관리 UI (Free/Premium/Expert 카드, 기능 비교, 라이선스 키 입력), (2) LicenseKeyDialog: 라이선스 키 입력 모달, (3) MainWindow에 "Subscription" 버튼 추가, (4) discord_bot.py: Discord 슬래시 명령 봇 (/pob, /price, /build, /meta, /help), (5) test_discord_bot.py 19개 테스트 통과, (6) Ko-fi/Buy Me a Coffee/GitHub Sponsors 도네이션 링크 연동, **빌드 성공, 총 테스트 146개+** |
| 2025-12-08 | **Phase 5.2: 에러 다국어 + 가격 알림 시스템** - (1) LocalizationService.cs: 싱글톤 다국어 서비스 (한국어/영어 25종 에러 메시지, Title/Message/Solution 구조), (2) SettingsWindow.xaml 언어 선택 ComboBox 추가, (3) App.xaml.cs 전역 예외 핸들러 로컬라이즈 메시지 표시, (4) price_alert_service.py: 관심 아이템 가격 변동 알림 시스템 (변동률/상한선/하한선 알림, 백그라운드 모니터링, 히스토리 저장), (5) test_price_alert_service.py 22개 테스트 통과, **총 테스트 109개 통과** |
| 2025-12-08 | **WPF UI 통합 완료** - (1) SetupWizardWindow.xaml/cs: 첫 실행 시 Python 경로 자동 감지 + LLM API 키 설정 UI, 4단계 마법사 (Python→AI→의존성→완료), 환경 변수 API 키 자동 감지, (2) PythonBridgeService.cs: Python 모듈 호출 브릿지 (setup_wizard, ai_session_manager, trade_link_generator, offline_mode_provider), (3) AISessionService.cs: 세션 기반 AI 사용량 추적, 남은 시간/세션 표시, (4) TradeLinkService.cs: POE Trade 검색 URL 생성, 저항 부족 아이템 검색, (5) OfflineModeService.cs: 네트워크 연결 감지, 오프라인 분석 폴백, **빌드 성공 (4 warnings)** |
| 2025-12-08 | **사용자 경험 개선 4대 모듈** - (1) trade_link_generator.py: pathofexile.com/trade 검색 URL 자동 생성, 아키타입별 스탯 필터, 32개 테스트 통과, (2) ai_session_manager.py: 세션 기반 AI 사용량 관리 (Free 2회/일, Premium 5회/일, Expert 무제한), 세션 충전 시스템, 30개 테스트 통과, (3) setup_wizard.py: Python 경로 자동 감지, LLM API 키 검증 (OpenAI/Claude/Gemini/Grok), 의존성 확인, 22개 테스트 통과, (4) offline_mode_provider.py: LLM 없이 로컬 빌드 분석, 아키타입별 레벨링 템플릿, 캐시 시스템, 20개 테스트 통과, **총 138개 신규 테스트 통과** |
| 2025-12-08 | **AI 프롬프트 + 추천 로직 + 통합 수집기 + 로컬 분석 엔진** - (1) BuildContext에 방어 스탯/아키타입/SSF/HC 호환성 필드 추가, (2) PromptBuilder에 6개 아키타입별 분석 팁/업그레이드 우선순위 추가, (3) upgrade_path.py에 예산 티어(50c~20000c) + poe.ninja 실시간 가격 연동, (4) unified_build_collector.py 생성 (Reddit+YouTube+poe.ninja 통합, 중복 제거, 인덱스 생성), (5) local_build_analyzer.py 생성 (LLM 없이 저항/생존/방어 분석, 0.1초 응답), (6) 101개 테스트 통과, 107개 빌드 인덱스 생성 |
| 2025-12-08 | **빌드 데이터 100개 수집 완료 + SSF/HC 태그 시스템** - (1) pob_link_collector.py에 append 모드 추가, (2) 107개 빌드 수집 (20개 어센던시 커버), (3) build_tagger.py 구현 (SSF/HC/HCSSF 호환성 자동 태깅), (4) poe.ninja 가격 연동 예산 티어 분류 (starter/budget/mid/high/mirror), (5) 테스트 추가 (test_build_tagger.py, test_build_context_builder.py - 38개 테스트 통과), (6) SSF viable 98%, HC viable 72%, HCSSF viable 71% |
| 2025-12-08 | **POB 파싱 강화 + 레거시 코드 제거** - (1) 키스톤 추출 기능 추가 (54개 키스톤 매핑, tree.lua 기반), (2) keystone_mapping.json 생성 (data/), (3) BuildContext에 keystones 필드 연동, (4) _legacy/ 폴더 삭제 (184KB, 4,336줄 레거시 코드 제거), (5) poe.ninja 가격 조회 정상 작동 확인 (2,751 유니크 아이템) |
| 2025-12-08 | **Reddit 빌드 수집 초기** - pob_link_collector.py로 13개 빌드 수집 |
| 2025-11-29 | **빌드 분석 개선 Phase 1-3 완료** - (1) recommended_bases.json 외부화 (12개 빌드 테마별 베이스 타입, 하드코딩 제거), (2) UI 에러 처리 개선 (failedSections 추적, 부분 성공 알림, 주황색 경고 토스트), (3) AI 모드 UX 개선 (ComboBox 툴팁, API 키 상태 실시간 표시) |
| 2025-11-29 | **UI 개선: My Build 탭 기본 화면으로 변경** - PRD 목표와 UI 정렬 (POB 분석 = 핵심 기능), MainWindow.xaml TabControl SelectedIndex="1" 추가, 기존 Empty State UI 재활용 |
| 2025-11-29 | **Phase 8.6: GemDataLoader 서비스 추가** - BuildAnalysisService가 gems.json 기반으로 338개 스킬 자동 분석 (기존 17개 하드코딩 SKILL_DAMAGE_MAP 대체), 태그 기반 데미지 타입/빌드 테마 추론, RF/SRS 등 특수 케이스 처리, 테스트 통과 (RF→fire_dot, SRS→minion_summoner, LS→physical_melee) |
| 2025-11-29 | **Phase 8.4: Migration 완료** - filter_generator_cli.py (새 CLI, FilterGeneratorService 기반, --mode/--area-level/--progressive/--summary/--name 인자), C# WPF 통합 (MainWindow.xaml.cs Line 101/1923/2002, build_filter_generator.py → filter_generator_cli.py 교체), Styling 객체 버그 수정 (resolve_for_tier() dict 키 매핑), 레거시 코드 4,336 라인 마이그레이션 대상 식별 |
| 2025-11-29 | **Phase 8.3: Application Layer + SSF Support 완료** - SSF 필터 분석 문서화 (SSF_FILTER_ANALYSIS.md), base_type_progression.json (5,400+ 라인, NeverSink 8.18.1a 기반), ProgressiveStrictnessService (SSF/Trade/HC_SSF 모드, AreaLevel 기반 점진적 숨김), BuildAnalysisService (chaos_dot, physical_melee, minion_summoner 등 테마 감지), FilterGeneratorService (메인 오케스트레이션, POB → 빌드 분석 → 우선순위 → 필터 생성), FilterGenerationRequest/Result DTOs, 테스트 통과 |
| 2025-11-28 | **Phase 8.2: Infrastructure Layer 완료** - POBParser (POB XML/URL 파싱), NinjaPriceProvider (poe.ninja 캐시, 1,368 유니크), FilterFileWriter (필터 파일 작성), End-to-End 통합 테스트 통과 |
| 2025-11-28 | **Phase 8.1: Domain Layer 완료** - 클린 아키텍처 필터 시스템 Domain Layer 구현, Build/FilterRule/ItemPriority 모델, IBuildParser/IPriceProvider 인터페이스, ItemPriorityCalculator/ColorSchemeResolver/FilterRuleBuilder 서비스, **Divine Orb 색상 단일 소스 (ColorSchemeResolver.TIER_COLORS)** |
| 2025-11-26 | **데이터 관리 시스템** - `data_manager.py` 추가, POB GitHub 버전 체크 (하루 3회), poe.ninja 실시간 가격 캐싱 (TTL별), 빌드 메타 조회 |
| 2025-11-26 | **필터 색상 JSON 외부화** - `filter_visual_config.json` 확장 (currency tiers, rarity, jewels, maps 등 15+ 카테고리), `filter_visual_rules.py`에 `get_color()`, `get_filter_lines()` 메서드 추가 |
| 2025-11-26 | **AI 빌드 대화 시스템** - `build_chat.py` 추가, 테마 변경/빌드 조언/가격 질문/필터 도움말 인텐트 처리, PRD Premium 크레딧 20→40회 수정 |
| 2025-11-26 | **POB 데이터 추출 시스템** - `pob_data_extractor.py` 추가, 리그 모드 961개 (Graft/Tincture/Necropolis/Foulborn), 유니크 1,242개, Graft 베이스 16개 + 347 모드, pob_base_extractor.py에 `extract_base_type()` 함수 추가 (MAGIC 아이템 베이스 추출) |
| 2025-11-26 | **필터 미리보기 API** - `filter_visual_rules.py`에 `get_preview_items()` 함수 추가, 테마별 색상 적용, CLI 지원 (`--preview --theme chaos_dot`) |
| 2025-11-26 | **사용자 데이터 백업 시스템** - `BackupService.cs` 추가, AES 암호화, 세션 종료 시 자동 백업, 최근 5개 유지, 북마크/캐시/설정 백업 |
| 2025-11-26 | **리그 자동 감지 시스템** - `league_service.py` 추가, POE 공식 Trade API 사용, 캐싱 지원, poe_ninja_api.py, poe_trade_api.py, poe_ladder_fetcher.py 업데이트 |
| 2025-11-26 | **필터 유효성 검사 시스템** - `filter_validator.py` 추가, POE 필터 문법 검증, NeverSink 메타 키워드 지원, 790개 블록 검증 0 오류 달성 |
| 2025-11-26 | **필터 색상 프리셋 시스템** - `--color-preset` CLI 옵션 추가 (default, eye-friendly, high-contrast, colorblind-safe), HSV 기반 색상 변환, RGB 채도/명도 조절 |
| 2025-11-25 | **Phase 1 완료** - 데이터 정확도 검증 (682 오류 수정), LLM 사용량 추적 시스템, RAG v2 (Multi-model), Gemini 통합 |
| 2025-11-25 | Phase 7.2 완료 - Fine-tuning Q&A 데이터 수집 시스템 (15,000 Q&A, 6개 소스, JSONL 자동 변환) |
| 2025-11-24 | Leveling 3.27 필터 셉터 숨김 - Death Aura (Chaos DoT) 빌드용, 레벨링 캐스터 셉터 규칙 Hide |
| 2025-11-24 | build_filter_generator.py 셉터 숨김 로직 추가 - DoT 빌드 타입 감지 시 셉터 Class 규칙 자동 숨김 |
| 2025-11-23 | quest_rewards.json 재구성 - POE Wiki 검증 데이터, 클래스별 정확한 퀘스트 보상 (13개 퀘스트) |
| 2025-11-23 | POE Trade 3단계 Electron 모듈 - Lazy Loading, 메모리 모니터링, 3단계 캐시, JSON-RPC IPC |
| 2025-11-23 | 빌드 전환 패턴 시스템 - Reddit 크롤링 65패턴, 폴백 패턴, 아키타입 분류, 협업 필터링 |
| 2025-11-23 | 동적 아이템 추천 엔진 - POB 빌드 분석 → mods.json 매칭 → poe.ninja 가격 → 예산 최적화 |
| 2025-11-23 | POB 전체 데이터 수집 시스템 - git clone, 모드 13,289개, 유니크 1,236개, 베이스 1,061개 |
| 2025-11-23 | NeverSink 필터 통합 시스템 - 파서, POB 오버레이, poe.ninja 가치 규칙, 7단계 엄격도 |
| 2025-11-23 | 레벨링 가이드 개선 - 태그 기반 젬 진행, 스킬 이름 매칭 강화, 기본 폴백 추가 |
| 2025-11-23 | 필터 생성 HasInfluence 문법 수정, KoreanTranslator skills_kr/items_kr 지원 추가 |
| 2025-11-23 | poedb.tw 크롤러 완성 - 퀘스트 보상 128개, 젬 레벨 549개, 벤더 레시피 201개 |
| 2025-11-23 | 파밍 전략 시스템 완성 - poe.ninja 연동, 현실적 수익 데이터, 15개 메카닉 상세 정보 |
| 2025-11-22 | 4개 아키타입 템플릿 완성 (spell, attack, minion, dot) + 테스트 스크립트 |
| 2025-11-22 | 가이드 템플릿 시스템 추가 - 공통/아키타입 분리, ZeeBoub Penance Brand 가이드 저장 |
| 2025-11-22 | skill_tag_system.py 리팩토링 - POB gems.json에서 338개 스킬 동적 로드 |
| 2025-11-22 | PROJECT_STATE.md, CLAUDE_INSTRUCTIONS.md, CLAUDE.md 생성 |
| 2025-11-22 | 불필요한 파일 삭제 (약 25개) |
| 2025-11-22 | poe.ninja 캐싱, POB 아이템 모드 파싱 |
| 2025-11-21 | 한국어 번역 시스템 (5,847 아이템) |
| 2025-11-21 | 북마크, 설정, 트레이드 윈도우 |
| 2025-11-20 | 사용자 빌드 분석, YouTube 썸네일 |

---

## 10. 작업 시 주의사항

1. **POE1만 지원** - POE2 데이터 사용 금지
2. **RePoE 금지** - 절대 참조하지 말 것
3. **하드코딩 금지** - 데이터는 JSON 파일로 분리
4. **한국어 지원 필수** - 모든 UI/데이터

---

*이 파일은 Claude가 작업을 완료할 때마다 업데이트해야 합니다*
