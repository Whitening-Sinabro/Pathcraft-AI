# Pathcraft-AI 상용화 읽기 전용 실사

평가일: **2026-09-21**, 조사 시작 **16:54:48 +07:00 (Asia/Bangkok)**. 본문 근거 확인은 같은 날 17시대에 수행했다. 평가 대상은 **실제 `D:/Pathcraft-AI` 작업 디렉터리 전체**이며, 이 보고서가 있는 새 worktree는 보고서 작성 공간으로만 사용했다. 원본 `AGENTS.md`, `CLAUDE.md`를 읽었고, 발견한 보관 하위트리의 `CLAUDE.md`도 확인했다. POE1 필터 수정은 하지 않았다.

**판정: 지금 상태 그대로 일반 고객에게 유료 판매하는 것은 보류해야 한다.** 결제·구독 권한과 크레딧은 판매 문구를 뒷받침하지 못하고, 고객 PC 배포·비밀정보 처리·외부 자료 이용 권한에도 독립적인 차단 요인이 있다. 제한된 개인 연구에는 활용 가치가 있고, 아래 선행 조건을 충족한 범위의 무상 비공개 검증은 다음 단계로 권고한다. 이는 제품 준비도 판단이며, 특정 이용 행위가 법적으로 허용되거나 위법하다는 판정은 아니다.

**후임 책임자 목표 보완:** 판매하려는 핵심은 수집자료와 사용자 조건으로 빌드·성장 경로를 만드는 제품이며 PoB 분석/비교는 보조다. 기존 구성을 조건부로 조합·변형하는 생성도 포함한다. 따라서 권리·과금·배포 문제 외에 **생성한 전체 구성이 작동하는지 검증하고 개인별 수정·저장까지 이어지는 핵심 제품 증거**가 먼저 필요하다. 이 추가 판정은 [생성 준비도 정적 평가](build_generation_readiness.md)에 근거하며 기존 상용화 조사·공식 출처를 재조사한 것은 아니다. 이하 원 상용화 담당의 정책·가격 확인일/미확인 범위는 그대로 유지한다.

## 1. 범위와 증거 수준

- **사실**: 직접 읽은 현재 파일·설정·메타데이터 또는 실제 회수한 공식 문서가 뒷받침한다.
- **추론**: 확인한 구현에서 도출한 위험·준비도 판단이다. 실제 실행 결과로 가장하지 않는다.
- **미확인**: 실행·계정·계약 또는 표본 외 자료가 필요하다. 미확인은 허용이나 위반을 의미하지 않는다.

원본 HEAD는 조사 중 `dd7a09a0b2237307b3ae44ad2ca6ee8be091a586`였다. `git status --porcelain`은 156행을 반환했으며 이는 파일 수가 아니다. `.claude/status/poe2_hc_gemling.md`, `scripts/probe_trade_listings.py` 등의 수정과 `build_planner`, `deliverables`의 다수 미추적 항목이 실제로 존재했다. 이 HEAD만으로 평가 내용을 재현할 수 없으며, 진행 중인 다른 작업의 변경이 들어올 수 있는 살아 있는 원본을 읽었다.

검토는 원본 경로 목록, 현재 Tauri→Python 호출 연결, 키·OAuth·저장 코드, 데이터 수집기, `.claude` 상태 문서, 미추적 플래너·방송 분석 산출물 표본, 기존 설치물 메타데이터, 공식 공급자 문서를 포함했다. 모든 바이너리·영상 프레임·전사문을 전수 판독하거나 모든 의존성 라이선스를 감사한 것은 아니다. 테스트·빌드·앱·설치 파일 실행, 유료 API 호출, 로그인·계정 변경, 게임 필터 변경, 원본 코드 수정은 **전혀 수행하지 않았다**. 비밀 값은 출력하거나 보고서에 복사하지 않았다.

## 2. 판매 차단 요인과 통과 기준

| 우선순위 | 현재 사실과 판정 | 유료화 전 통과 증거 |
|---|---|---|
| **P0-0 생성 제품의 핵심 가치** | 자료 문맥을 활용한 코칭·기존 profile 추천·PoB 변환 경로는 있으나 사용자 조건에 따른 완성 구성의 생성·통합검증·수정/저장 완결은 미확인. [build_coach.py:1332](D:/Pathcraft-AI/python/build_coach.py:1332), [입력 스탯 해석](D:/Pathcraft-AI/python/build_instance.py:445), [생성 준비도](build_generation_readiness.md). | 지원 범위 내 예산/보유품/선호 차이가 실제 빌드 구성·성장 경로에 반영되고, 불가능·미확인 조건은 보류되며, 각 단계의 지원호환·포인트·자원·획득·패치·성능 검증 범위와 출처를 추적. 수정→재검증→저장·재열기 연속 증거. PoB 입력을 필수 전제로 하지 않음. |
| **P0-1 데이터 접근·상용 권한** | POE2 추적기는 poe.ninja 내부 캐릭터 API를 호출한다. 현재 공식 문서는 해당 계열을 제3자용으로 제공하지 않는다. GGG 게임 자산·GGPK·방송·외부 가이드의 상업적 이용 범위를 덮는 계약도 이번 검토에서 확인되지 않았다. | 출시 기능별 데이터 원천·수집 경로·권리자·허용 목적·재배포/번역/AI 입력/학습 범위·철회 절차를 적은 권리 대장과 근거 문서. 허용되지 않는 접근은 별도 허가를 받거나 허용된 경로로 교체하고, 미해결 자료는 배포 목록에서 제외. §5 참조. |
| **P0-2 판매 약속·결제 권한** | README의 유료 티어·월 크레딧·Fine-tuned 모델·OAuth 승인·환불·우선지원은 실제 상용 운영 증거와 다르다. 크레딧 함수는 명시적으로 Mock이며 차감도 저장하지 않는다. | 판매 기능·제한·지원 약속과 실제 출시 경로의 일치. 구독형이면 검증된 결제 이벤트→권한 부여→갱신/해지/환불/권한 회수, 중복·위조 이벤트 방지와 원자적 사용량 차감 증거. §3 참조. |
| **P0-3 비밀정보·개인정보** | 로컬 `.env` 키 사용, OAuth 토큰·검증자 로그 출력, 평문 토큰 저장 코드가 있다. 빌드·노트·이미지는 공급자 API에 전달되고 로컬에도 남는다. | 소유자 키가 배포물에 없다는 검사, BYOK 또는 서버 키 구조 확정, 안전한 저장·회수, OAuth 보완, 전송 고지·선택, 로컬/서버 삭제와 로그 마스킹 검증. §4 참조. |
| **P0-4 고객 설치·출시 재현성** | 기존 설치물은 있으나 현재 코드와의 대응은 미확인이고, 수정 시각은 7월이며 서명이 없다. 현재 실행 코드는 시스템 Python과 프로젝트 폴더를 찾고, Tauri 설정에는 Python/data 번들 선언이 없다. | 실제 출시 커밋+미추적 자산 명세+잠금된 런타임/의존성으로 만든 패키지. 개발 도구 없는 새 Windows 사용자/PC에서 설치·핵심 흐름·제거·업데이트·복구 성공 기록 및 무결성/배포 신뢰 정책. §6 참조. |
| **P0-5 비용·오류 통제** | 실제 앱은 기본 GPT-5 nano이며 출력 상한·캐시·교정 재시도는 있다. 계정별/전체 금액 상한과 서버 원장은 확인되지 않았고, 재시도 전 호출의 사용량이 최종 로그에서 빠질 수 있다. | 모든 시도 비용 합산, 모델/요청 크기/동시성/횟수 제한, 금액 한도 초과 시 차단, 실패·취소·재시도·환불 정산 정책과 검증. 공급자 계정별 실제 요율·한도 확인. §7 참조. |
| **P1-1 유지관리·품질·지원** | 패치 가드·정규화·일부 429 대처는 있다. 출시 버전별 품질·고객 복구·지원 운영은 미확인이다. 내부 상태의 ‘블로커 없음’도 전체 테스트 실패/오류를 함께 기록한다. | 지원할 게임/패치/빌드 범위, 갱신 책임, 오래된 추천 차단, 골든 케이스·외부 장애 검증, 지원 창구와 응답 약속·취약점/정정 절차. §8 참조. |
| **P1-2 유료 차별성** | 한국어 HC/SSF 전환 조건·근거 연결은 유망하지만 연구 파이프라인과 판매 앱 경험이 완결된 증거는 없다. 기존 제품도 빌드 추적·플래너·필터 조정을 제공한다. | 권한이 확보된 동일 빌드/과제로 기존 도구와 비교한 사용자 검증. 판단 정확도·출처 추적 가능성·사용자 독립 수행·추가 가치의 관찰 기록. §9 참조. |

P0 항목은 서로 독립적이다. 결제 기능만 붙이거나 모델을 바꿔도 나머지 차단 요인이 해소되지 않는다. 우선순위는 해결 기간이나 완성률의 추정이 아니다.

## 3. README 판매 문구와 실제 구현

**사실:** 현재 데스크톱의 주요 화면은 빌드 리서치, PoB 검증, Syndicate, 패시브 트리다. Rust에 등록된 명령은 파싱·소스 해석·코칭·필터·게임 데이터 추출 등이며 결제·구독·OAuth 명령은 없다. `src`, `src-tauri/src`, `python`, `Docs`의 관련 문자열 검색에서도 현재 앱에 연결된 결제 제공자 webhook/권한 서버를 확인하지 못했다. 별도 외부 운영 시스템의 존재까지 부정하는 것은 아니다. 근거: [Sidebar.tsx:20](D:/Pathcraft-AI/src/components/shell/Sidebar.tsx:20), [lib.rs:1152](D:/Pathcraft-AI/src-tauri/src/lib.rs:1152).

| README 주장 | 확인한 구현·증거 | 판단 |
|---|---|---|
| Premium $2/월, Expert $5/월, 월 20회/무제한 | [README.md:35](D:/Pathcraft-AI/README.md:35). [build_guide_generator.py:349](D:/Pathcraft-AI/python/build_guide_generator.py:349)는 환경변수/기본 15를 반환하며 DB가 Mock임을 명시. [같은 파일:373](D:/Pathcraft-AI/python/build_guide_generator.py:373)은 새 잔액을 계산·출력할 뿐 저장하지 않는다. | **사실:** CLI 분기는 있으나 신뢰 가능한 사용량 원장이 아니다. 사용자가 `tier`와 `user_id`를 입력하는 것으로 구독 자격이 증명되지 않는다. |
| Expert 전용 Fine-tuned POE 모델, 10,000+ Q&A, 최상급 최적화 | [README.md:58](D:/Pathcraft-AI/README.md:58), [build_guide_generator.py:152](D:/Pathcraft-AI/python/build_guide_generator.py:152)에 모델명 문자열은 있다. 현재 앱의 기본값은 [useBuildAnalyzer.ts:43](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:43)과 [build_coach.py:35](D:/Pathcraft-AI/python/build_coach.py:35)의 `gpt-5-nano`. | **미확인:** 실제 학습 작업/모델 접근권, 데이터 권리, 평가 결과. 문자열은 모델 실재·성능 증거가 아니다. 현재 앱이 Expert 모델을 쓴다고 광고할 수 없다. |
| Patreon/Ko-fi 결제, 7일 환불, Email/Discord 우선지원 | [README.md:43](D:/Pathcraft-AI/README.md:43), [README.md:108](D:/Pathcraft-AI/README.md:108). | **미확인:** 운영 계정·결제 통합·고객 권한 연동·환불 실행·지원 인력. 판매자가 수동 운영할 수는 있으나 그 절차와 이행 증거가 필요하다. |
| GGG 공식 OAuth 승인(2025-06-07) | [README.md:220](D:/Pathcraft-AI/README.md:220), [.claude/status/api-integration.md:1](D:/Pathcraft-AI/.claude/status/api-integration.md:1)는 동일 주장을 반복하고 기존 C# 구현은 재작성 대상으로 적는다. | **미확인:** 승인 원본·현재 client 유형/범위·리디렉션·유효성. OAuth 등록은 상품 전반의 공식 보증이나 상업적 IP 허가와 동일하지 않다. |

**권고:** 출시 시에는 판매 계약의 기능·쿼터·지원 범위를 하나로 확정하고 문구를 실제 구현에 맞춰야 한다. 이번 실사는 README를 수정하지 않았다. ‘무료 사용자 키’ 방식도 제품 자체의 권리·개인정보·설치 문제를 없애지 않는다.

## 4. 인증, 키와 개인정보

### 4.1 실제 키 취급

**사실:** `D:/Pathcraft-AI/.env:1`의 `OPENAI_API_KEY`, `:2`의 `YOUTUBE_API_KEY`에 비어 있지 않은 값이 존재한다. 값·접두사·유효성은 보고하지 않으며 실제 인증도 시도하지 않았다. `.env`와 `poe_token.json`은 [`.gitignore:13`](D:/Pathcraft-AI/.gitignore:13), [`.gitignore:18`](D:/Pathcraft-AI/.gitignore:18)에 제외되어 있다. 이는 Git 추적 방지이며 암호화나 설치물 제외를 증명하지 않는다.

[build_coach.py:15](D:/Pathcraft-AI/python/build_coach.py:15)는 프로젝트 루트 `.env`를 `override=True`로 읽고, [같은 파일:50](D:/Pathcraft-AI/python/build_coach.py:50)에서 SDK 클라이언트를 생성한다. **추론:** 이미 설정한 사용자 환경보다 복사된 프로젝트 키가 우선할 수 있다. 현재 앱에 별도 안전 저장소/키 관리 흐름이 있다는 증거는 확인하지 못했다. 사업자 공용 키를 설치물에 넣는 방식은 승인 조건을 통과시키면 안 된다.

### 4.2 OAuth 경로의 구체적 문제

- **사실:** PKCE 생성은 [poe_oauth.py:37](D:/Pathcraft-AI/python/poe_oauth.py:37)에 있지만, authorization `state`는 고정 문자열이다([:138](D:/Pathcraft-AI/python/poe_oauth.py:138)). callback은 code를 저장하고 state를 비교하지 않는다([:63](D:/Pathcraft-AI/python/poe_oauth.py:63)). 서버는 루프백 전용 주소가 아닌 빈 host로 bind한다([:112](D:/Pathcraft-AI/python/poe_oauth.py:112)). 이는 코드상 관찰이며 공격 성공을 재현하지 않았다.
- **사실:** 토큰 교환의 요청 `data`와 성공 응답 전체를 stderr에 출력한다([:192](D:/Pathcraft-AI/python/poe_oauth.py:192)). 인증 코드·PKCE 검증자·토큰 등이 로그로 나갈 수 있는 경로다. 실제 비밀 로그 파일을 열어 확인하거나 복사하지 않았다.
- **사실:** [save_token:436](D:/Pathcraft-AI/python/poe_oauth.py:436)은 스크립트 디렉터리의 `poe_token.json`에 JSON을 평문 저장한다. 조사 시 `D:/Pathcraft-AI/python/poe_token.json`과 루트의 동명 파일은 없었다. 다른 위치의 과거 토큰 존재나 과거 노출 여부는 미확인이다.
- **추론:** 이 경로는 현재 Tauri 등록 명령에 없으므로 현행 UI가 해당 취약 경로를 실행한다고 단정할 수 없다. 그러나 README가 판매 기능으로 안내하므로, 출시에서 제외하거나 복구·보안 검증 후 연결해야 한다.

통과 조건은 요청별 난수 state의 검증·단일 사용, loopback callback, 토큰/검증자 로그 제거, 저장소 접근 보호와 키 회수, 취소·시간초과·만료·갱신 실패 처리다. 실제 client 등록과 판매 모델이 맞는지도 별도로 입증해야 한다.

### 4.3 전송·잔존 데이터

| 데이터 | 현재 코드 경로 | 필요한 통제 |
|---|---|---|
| PoB 빌드 및 사용자의 구두 입력 노트 | [useBuildAnalyzer.ts:309](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:309), [:391](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:391) → [build_coach.py:1736](D:/Pathcraft-AI/python/build_coach.py:1736) 또는 Anthropic 호출 | 전송 전 수신자·목적·포함 정보·비용을 고지하고, 계정명·비공개 노트 등 불필요 정보 제거 및 선택권 제공. |
| Syndicate 스크린샷 | [VisionControls.tsx:48](D:/Pathcraft-AI/src/components/syndicate/VisionControls.tsx:48)에 Claude Vision tooltip은 있으나, [syndicate_vision.py:182](D:/Pathcraft-AI/python/syndicate_vision.py:182)는 이미지 base64를 외부 전송한다. [:29](D:/Pathcraft-AI/python/syndicate_vision.py:29)의 모델은 `claude-opus-4-6`. | 채팅·계정명 등이 포함될 가능성을 다루는 미리보기/잘라내기/전송 고지. 단순 tooltip을 완성된 개인정보 흐름으로 볼 수 없다. |
| 분석 이력/결과 캐시 | [useBuildHistory.ts:5](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:5), [:58](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:58): raw build/coach를 localStorage에 최대 20건. 별도 coach cache는 [useBuildAnalyzer.ts:283](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:283), [:321](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:321). | 이력 삭제가 별도 캐시·로그까지 제거하는지 검증. 현재 remove는 이력 배열만 변경([useBuildHistory.ts:100](D:/Pathcraft-AI/src/hooks/useBuildHistory.ts:100)); 캐시 TTL/삭제 연동은 이 경로에 없다. |
| 디버그 결과 | [build_coach.py:2018](D:/Pathcraft-AI/python/build_coach.py:2018)은 `_debug/coach_last_{game}.json`에 결과를 쓴다. | 출시 기본 비활성화 또는 명시적 진단 동의·보존 기간·삭제와 지원 업로드 마스킹. |

**공식 공급자 확인(모두 2026-09-21):** OpenAI API 데이터는 기본적으로 학습에 사용하지 않지만 abuse monitoring 보존이 있으며, Responses는 기본 application state 보존이 있다. 현재 호출에는 `store=False`가 없다. 계정의 별도 보존 특약은 미확인이다. [OpenAI 데이터 통제](https://developers.openai.com/api/docs/guides/your-data). Anthropic API의 표준 삭제 기간과 예외는 별도이며 무보존이라고 설명하면 안 된다. [Anthropic 보존 정책](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data).

구형 선택 경로에는 Gemini와 xAI도 남아 있다([llm_provider_factory.py:196](D:/Pathcraft-AI/python/llm_provider_factory.py:196), [:261](D:/Pathcraft-AI/python/llm_provider_factory.py:261)). 현재 데스크톱 기본 연결과 구분해야 한다. Gemini 무료 서비스는 지역 예외를 포함한 데이터 사용·인적 검토 조건이 있으므로 README의 ‘공짜’가 동일한 개인정보 조건을 뜻하지 않는다. xAI도 기본 보존과 별도 ZDR 상태가 구분된다. [Gemini 약관](https://ai.google.dev/gemini-api/terms), [xAI API 보안](https://docs.x.ai/developers/faq/security), 확인 2026-09-21. 해당 모델의 실제 계정 접근·현재 지원 여부·지역 적격성은 호출하지 않아 미확인이다.

**필요 결정:** 판매자 소재지, 대상 고객 국가·연령, 개인정보 처리 주체, BYOK/사업자 API 모델을 먼저 정해야 한다. 그 조건 없이 한국·EU 등 특정 법의 적용·준수를 확정하지 않는다. 완성된 개인정보 고지, 데이터 보존/삭제 범위, 공급자 계약과 국외 처리 검토는 출시 승인에 필요한 미확인 항목이다.

## 5. 게임 데이터·외부 가이드·방송·라이선스

### 5.1 현재 정책과 충돌 가능성이 직접 드러난 수집 경로

**사실:** [track_poe2_character.py:74](D:/Pathcraft-AI/scripts/track_poe2_character.py:74)는 `poe.ninja/poe2/api/builds/latest/character`에 `Mozilla/5.0` User-Agent로 요청한다. [기본 간격:278](D:/Pathcraft-AI/scripts/track_poe2_character.py:278)은 180초이고, [.claude/status/current.md:20](D:/Pathcraft-AI/.claude/status/current.md:20)은 이를 실제 파이프라인에 둔다. 반면 [poe_ninja_build_scraper.py:14](D:/Pathcraft-AI/python/poe_ninja_build_scraper.py:14)는 같은 정책을 이유로 구형 빌드 수집을 비활성화했다.

**공식 사실:** 현재 poe.ninja API 문서는 economy endpoint를 공개 표면으로 설명하고, builds/profiles/character/PoB/authentication 계열은 제3자 사용용이 아니라고 명시한다. 경제 API에도 캐시·식별 User-Agent·요청량·백엔드 프록시 지침과 안정성 무보장 설명이 있다. [poe.ninja API Reference](https://poe.ninja/docs/api), 확인 **2026-09-21**.

**판정:** 느린 폴링·공개 캐릭터·개별 조회라는 이유만으로 이 정책 문제는 해결되지 않는다. 별도 예외 계약은 미확인이다. 현재 API 기반 실캐릭 여정을 유료 서비스의 안정된 입력으로 약속해서는 안 된다. 사용자 직접 export/입력, 권리자가 제공하는 허용 자료, 사용 범위가 확인된 공식 API로 대체 가능성을 검증해야 한다. 이미 보유한 스냅샷도 출처·보관·재배포 권한은 따로 확인한다.

### 5.2 원천별 판단

| 원천과 실제 프로젝트 근거 | 공식 확인과 불확실성 | 출시 조건 |
|---|---|---|
| **GGG 게임 자료·GGPK·트리·OAuth**. [lib.rs:298](D:/Pathcraft-AI/src-tauri/src/lib.rs:298)는 게임 번들에서 데이터를 추출한다. [oodle.rs:34](D:/Pathcraft-AI/src-tauri/src/oodle.rs:34)는 DLL을 동적 로드하며 [:135](D:/Pathcraft-AI/src-tauri/src/oodle.rs:135)는 Unreal 설치 경로 후보도 탐색한다. | GGG는 독립 실행 앱과 게임/게임 파일 상호작용을 구분하고 상업적 IP 이용을 제한한다. 공개 문서에 공식 데이터 export도 있다. 게임이 지원하는 사용자 필터/플래너 import와 게임 번들 추출·DLL 이용을 같은 행위로 취급하면 안 된다. [개발자 정책](https://www.pathofexile.com/developer/docs), [이용약관](https://www.pathofexile.com/legal/terms-of-use-and-privacy-policy), [Data Exports](https://www.pathofexile.com/developer/docs/data), 확인 2026-09-21. | 판매 기능별 사용 범위를 GGG 정책·필요 허가와 대조. 데이터와 그림/문구/로고를 분리. Oodle 실행/재배포 권한도 별도 확인; DLL을 찾는 코드가 권한 증명은 아니다. |
| **Mobalytics 제작자 가이드·export**. [.claude/status/poe2_hc_gemling.md:15](D:/Pathcraft-AI/.claude/status/poe2_hc_gemling.md:15), [hc_creator_sourcing.md:65](D:/Pathcraft-AI/.claude/status/hc_creator_sourcing.md:65). | 현재 약관에는 허용되지 않은 상업적 사용·제3자 이익을 위한 이용 제한이 있다. 공개 export 버튼만으로 유료 재가공·재배포 권한을 추정할 수 없다. [Mobalytics Terms](https://mobalytics.gg/terms/), 확인 2026-09-21. | 플랫폼 조건과 제작자 저작물의 권리를 각각 확인. 원본 링크·사실 추출·번역 가이드·이미지·플래너 재배포별로 범위를 명시. |
| **Twitch VOD·오디오·전사·프레임**. [초반생존_방송상세분석.md:94](D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/초반생존_방송상세분석.md:94), [focus_transcribe.py:15](D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/focus_transcribe.py:15). 후자는 로컬 faster-whisper를 사용한다. | 최신 공개 약관 본문을 HTTP로 회수해 상업적 이용·데이터 수집·다운로드 제한을 확인했다(페이지 표시 수정일 08/12/2026). 검색 도구가 내비게이션만 반환해 추가 공개 HTTP 확인을 했다. [Twitch Terms](https://legal.twitch.com/en/legal/terms-of-service/), 확인 2026-09-21. | 방송자 허가와 플랫폼의 접근·다운로드 조건을 별개로 검증. 재판매/번역/화면·음성 이용/학습을 포괄하는지 확인. 보유 영상이 있다는 사실은 판매 권리 증거가 아니다. |
| **YouTube 메타데이터·자막**. [youtube_build_collector.py:129](D:/Pathcraft-AI/python/youtube_build_collector.py:129), [hc_creator_sourcing.md:67](D:/Pathcraft-AI/.claude/status/hc_creator_sourcing.md:67), 미추적 `deliverables/seongbin_streams_2026-09-13/*.json3`. | API 개발자 정책은 영상·음성 복제 저장에 사전 승인 조건을 두고, 데이터 저장·갱신·표시·개인정보 요건을 둔다. 자막 수집에 사용한 별도 도구의 접근은 API 메타데이터 허가와 같다고 볼 수 없다. [YouTube Developer Policies](https://developers.google.com/youtube/terms/developer-policies), 확인 2026-09-21. | 메타데이터 API, 자막, 영상·오디오, 제작자 저작물을 나눠 허용 근거 확인. 무제한 검색·고정 무료 쿼터 광고는 계정별 실제 쿼터 확인 전 보류. |
| **PoEDB·PoE Wiki·Maxroll·pobb.in·Pastebin**. [wiki_data_provider.py:17](D:/Pathcraft-AI/python/wiki_data_provider.py:17), [build_source_resolver.py:20](D:/Pathcraft-AI/python/build_source_resolver.py:20), [:102](D:/Pathcraft-AI/python/build_source_resolver.py:102). | PoEDB 현재 공개 페이지는 wiki content에 CC BY-NC-SA 3.0(예외 가능)을 표시한다. 이것을 게임 데이터 전체나 사용자가 올린 PoB 전체의 동일 라이선스로 확대하지 않는다. [PoEDB 고지](https://poedb.tw/us/DataHistory?cn=TreasureHunterMissions), 확인 2026-09-21. PoE Wiki는 공개 요청에서 보호 페이지가 반환되어 원문 조건을 확정하지 못했고, Maxroll은 웹 도구 robots 제한으로 약관 본문을 검증하지 못했다. | 출처별 허용 범위 확인. 위키 문장의 NC 조건과 사실/수치/게임 자산을 구분하고, 별도 허가·대체·배포 제외를 결정. pobb.in/Pastebin의 링크 접근이 링크 속 제작물의 판매권을 주지는 않는다. |
| **Reddit**. [pob_link_collector.py:20](D:/Pathcraft-AI/python/pob_link_collector.py:20), [build_search_manager.py:105](D:/Pathcraft-AI/python/build_search_manager.py:105). | 현재 Data API Terms는 상업적 사용에 별도 계약을 요구하며 사용자 콘텐츠 학습 등에도 권리 조건을 둔다. 현재 UI 연결 여부와 별개로 남아 있는 CLI/데이터 경로의 문제다. [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms), 확인 2026-09-21. | 해당 수집·저장 데이터가 출시물에 들어가는지 명시하고 승인 범위를 확인하거나 제외. |
| **NeverSink 필터, PoB 코드, dat-schema**. [neversink_poe2_soft.filter:2](D:/Pathcraft-AI/data/filter_sources/neversink_poe2_soft.filter:2), [schema.rs:3](D:/Pathcraft-AI/src-tauri/src/schema.rs:3). | NeverSink POE1/POE2와 dat-schema 공식 LICENSE는 MIT이며 고지 보존 조건이 있다. PoB LICENSE는 주 코드 MIT 외 구성요소 라이선스도 수록한다. [NeverSink POE1](https://raw.githubusercontent.com/NeverSinkDev/NeverSink-Filter/master/LICENSE), [POE2](https://raw.githubusercontent.com/NeverSinkDev/NeverSink-Filter-for-PoE2/main/LICENSE), [dat-schema](https://raw.githubusercontent.com/poe-tool-dev/dat-schema/master/LICENSE), [PoB](https://raw.githubusercontent.com/PathOfBuildingCommunity/PathOfBuilding/dev/LICENSE.md), 확인 2026-09-21. | 채택한 정확한 버전·코드·필터·의존성을 대조해 고지를 동봉. MIT 코드 허용이 GGG 자산이나 제작자 가이드 권리까지 포괄하지 않는다. |

**놓치기 쉬운 구분:** [hc_creator_sourcing.md:81](D:/Pathcraft-AI/.claude/status/hc_creator_sourcing.md:81)의 ‘허락 결과’는 사용자의 작업 승인이다. 이것을 크리에이터나 플랫폼의 상업 라이선스 승인으로 계산하면 안 된다. 실제 미추적 [Warbringer Lv24 live 0905 - Skadoosh.build:2](<D:/Pathcraft-AI/build_planner/Warbringer Lv24 live 0905 - Skadoosh.build:2>)는 저자와 ninja 출처를 표시하지만 권한 부여 문서는 아니다.

**자체 코드/번들 라이선스도 미완결:** [README.md:368](D:/Pathcraft-AI/README.md:368)은 MIT, [package.json:17](D:/Pathcraft-AI/package.json:17)은 ISC, [Cargo.toml:6](D:/Pathcraft-AI/src-tauri/Cargo.toml:6)은 빈 license다. 루트 `LICENSE`, `LICENSE.md`, `LICENSE.txt`는 확인 시 없었다. 이것만으로 코드 판매가 불가능하다는 법적 결론은 내리지 않지만, 배포 약관·저작권자·제3자 고지를 정리하지 않고 전체 원본 폴더를 상품으로 배포하는 것은 승인할 수 없다. `deliverables`의 vendored 문서 라이브러리까지 포함할지는 별도 배포 명세로 정해야 한다.

## 6. 설치·배포와 게임 데이터 의존성

**사실:** [package.json:7](D:/Pathcraft-AI/package.json:7)은 TypeScript/Vite 빌드와 Python 번역 생성 prebuild를 연결한다. [extract_passive_tree_translations.py:7](D:/Pathcraft-AI/python/extract_passive_tree_translations.py:7)은 트리 export와 번역 JSON을 입력으로 요구한다. 루트와 `python/`에 `requirements.txt`, 루트에 `pyproject.toml`은 없었다. README 설치 지시의 루트 requirements 파일은 현재 경로와 맞지 않는다([README.md:117](D:/Pathcraft-AI/README.md:117)). 다른 보관 경로에 requirements가 있다는 사실은 현행 앱의 잠금된 의존성 명세를 대체하지 않는다.

[lib.rs:51](D:/Pathcraft-AI/src-tauri/src/lib.rs:51)은 PATH의 `python`을 실행하며, [:58](D:/Pathcraft-AI/src-tauri/src/lib.rs:58)은 환경변수→실행 파일 조상→현재 디렉터리 조상에서 프로젝트를 찾는다. [:560](D:/Pathcraft-AI/src-tauri/src/lib.rs:560)은 그 루트의 data를 읽는다. [tauri.conf.json:46](D:/Pathcraft-AI/src-tauri/tauri.conf.json:46)의 bundle에는 아이콘·targets 설정만 있으며 Python 런타임/스크립트/data의 `resources`나 `externalBin` 선언이 없다. **추론:** 현재 설정만으로 독립적인 신규 고객 설치를 보장할 수 없다. 별도 패키징 절차가 있는지, 과거 설치물에 무엇이 들어갔는지는 설치를 실행하지 않아 확정하지 않았다.

기존 바이너리에 대한 **읽기 전용 관찰**:

| 실제 절대 경로 | 크기·수정 시각(로컬 +07:00) | Authenticode 결과 |
|---|---|---|
| `D:/Pathcraft-AI/src-tauri/target/release/bundle/nsis/PathcraftAI_0.1.0_x64-setup.exe` | 43,822,819 bytes; 2026-07-17 18:49:06 | `NotSigned` |
| `D:/Pathcraft-AI/src-tauri/target/release/bundle/msi/PathcraftAI_0.1.0_x64_en-US.msi` | 44,965,888 bytes; 2026-07-17 18:48:39 | `NotSigned` |

바이너리에는 줄번호가 없으므로 `Get-Item` 및 `Get-AuthenticodeSignature` 메타데이터 관찰로 명시한다. 서명이 없다는 사실을 악성코드나 실행 불가능 판정으로 확대하지 않는다. 빌드 성공 기록·소스 대응·패키지 내용·설치 성공 증거도 아니다.

현재 데이터 추출은 게임 설치·번들·Oodle에 의존하고 출력도 프로젝트 data에 쓴다([lib.rs:303](D:/Pathcraft-AI/src-tauri/src/lib.rs:303), [:311](D:/Pathcraft-AI/src-tauri/src/lib.rs:311)). 고객 설치 경로의 쓰기 권한, 게임 미설치, Steam/독립 클라이언트, 패치 후 schema drift를 구분한 지원 계약이 필요하다. 공개 data export를 이용할 수 있는 항목과 허가가 필요한 추출을 먼저 분리해야 한다.

**실행 검증 담당에게 넘길 통과 조건:** 개발 checkout·전역 Python·원본 `.env`가 없는 환경에서 설치 후 자신의 입력으로 핵심 기능 수행; 한글/공백 경로·일반 권한 사용자·네트워크 단절·필수 데이터 누락에 대한 안내; 데이터 보존/제거 선택; 이전 버전 데이터 마이그레이션; 업데이트 실패 및 롤백; 출시 manifest/hash와 설치물 대응. 이 보고서에서는 수행하지 않았다.

## 7. API 비용 통제와 과금 모델

현재 구현에서 유효한 기반은 있다. 모델 allowlist([lib.rs:192](D:/Pathcraft-AI/src-tauri/src/lib.rs:192)), 프런트 캐시([useBuildAnalyzer.ts:283](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:283)), 출력 상한 16,384/32,000([build_coach.py:1670](D:/Pathcraft-AI/python/build_coach.py:1670)), 잘못된 젬에 대한 한 차례 교정 재호출([:1873](D:/Pathcraft-AI/python/build_coach.py:1873))이 보인다. 이는 비용 폭증 방지의 일부이며 구독 원장·총 지출 차단은 아니다.

**계측 결함의 근거:** 첫 응답은 [:1775](D:/Pathcraft-AI/python/build_coach.py:1775), 재시도는 [:1897](D:/Pathcraft-AI/python/build_coach.py:1897)에서 같은 `response` 변수에 저장된다. 완료 시 [:1989](D:/Pathcraft-AI/python/build_coach.py:1989)는 남아 있는 response의 usage만 정규화한다. **추론:** 교정 재호출이 발생하면 최종 로그만으로 첫 호출 비용을 합산할 수 없다. SDK 자체 재시도·실패 후 공급자 청구·취소 후 처리 여부도 별도 측정해야 한다.

현재 공식 **표준 토큰 단가**는 다음과 같다. 확인일 **2026-09-21**, USD/백만 토큰이며 세금·계약 할인·도구/이미지·캐시 생성 등 모든 비용을 뜻하지 않는다.

| 실제 코드에 등장하는 모델 | 입력 | 캐시 입력 | 출력 | 공식 근거 |
|---|---:|---:|---:|---|
| `gpt-5-nano` (현재 앱 기본) | 0.05 | 0.005 | 0.40 | [OpenAI 모델 문서](https://developers.openai.com/api/docs/models/gpt-5-nano) |
| Claude Haiku 4.5 | 1 | 0.10 | 5 | [Anthropic 가격](https://platform.claude.com/docs/en/about-claude/pricing) |
| Claude Sonnet 4.6 | 3 | 0.30 | 15 | 같은 공식 가격 문서 |
| Claude Opus 4.6 / 4.7 (4.6은 Vision 경로) | 5 | 0.50 | 25 | 같은 공식 가격 문서 |

`요청 원가 = 모든 시도의 비캐시 입력×입력 단가 + 캐시/캐시 생성 비용 + 출력×출력 단가 + 기타 해당 요금`으로 원장을 작성해야 한다. 원가는 실제 토큰·실패·재시도·캐시 적중에 따라 달라진다. README의 `$0.03`, `$0.0045`, ‘무제한’, Gemini 고정 무료 횟수를 현재 실측 원가나 수익성으로 인정하지 않는다([README.md:51](D:/Pathcraft-AI/README.md:51)). 이번 조사에서 API를 실행하거나 수익·기간을 추정하지 않았다.

**필요 결정:** BYOK 개인 도구로 판매할지, 사업자가 호출료를 부담할지 먼저 확정한다. 후자는 클라이언트가 조작할 수 없는 인증·권한·원자적 차감·동시성 제어·계정/전사 지출 상한·비용 알림·차단 장치가 필요하다. BYOK는 사용자에게 공급자 청구가 별도라는 설명과 키 입력/삭제·모델 선택·최대 사용량 통제가 필요하다. 어느 쪽도 현재 README의 무제한 약속을 자동으로 정당화하지 않는다.

## 8. 업데이트·품질·오류 대응·지원

**사실:** 일부 보호는 실제로 있다. Rust는 작업을 blocking pool로 옮기고 오류를 반환하며([lib.rs:113](D:/Pathcraft-AI/src-tauri/src/lib.rs:113)), 모델 allowlist와 단일 coach 취소 경로를 둔다. [build_coach.py:1783](D:/Pathcraft-AI/python/build_coach.py:1783)은 JSON 복구, [:1873](D:/Pathcraft-AI/python/build_coach.py:1873)은 젬 정규화 재시도를 수행한다. [probe_trade_listings.py:109](D:/Pathcraft-AI/scripts/probe_trade_listings.py:109)는 429에서 Retry-After를 읽는다. 따라서 오류 처리나 검증이 전혀 없다는 평가는 틀리다.

다만 출력 존재·스키마 복구·아이템명 정규화는 빌드의 실제 생존성이나 패치 적합성 보증과 다르다. [.claude/status/poe2_hc_gemling.md:372](D:/Pathcraft-AI/.claude/status/poe2_hc_gemling.md:372)는 과거 검토에서 출처 혼합·조건부 설명의 단정 문제가 발견됐다고 기록한다. [.claude/status/current.md:6](D:/Pathcraft-AI/.claude/status/current.md:6)은 전체 테스트 실패 12/오류 16을 기재한다. **이 숫자는 내부 기록을 읽은 사실이며 이번 원본에 대한 재실행 결과가 아니다.** 현재 구현 담당의 실행 결과가 우선한다.

패치 기준도 출시 계약으로 고정되지 않았다. Rust의 가드는 [lib.rs:567](D:/Pathcraft-AI/src-tauri/src/lib.rs:567)의 `3.29.0`이고, CLI help는 [build_coach.py:2008](D:/Pathcraft-AI/python/build_coach.py:2008)에서 더 오래된 게임 버전을 설명한다. 데이터·코드·캐시의 버전을 함께 표시하고 패치 변경 시 무효화해야 한다. 캐시 키는 입력/게임/모델/앱 schema 버전 중심으로 구성되며 별도의 자료 개정 hash가 명확히 포함된 근거는 보이지 않는다([useBuildAnalyzer.ts:283](D:/Pathcraft-AI/src/hooks/useBuildAnalyzer.ts:283)).

현재 Tauri 의존성·초기화에는 updater가 없고([Cargo.toml:21](D:/Pathcraft-AI/src-tauri/Cargo.toml:21), [lib.rs:1148](D:/Pathcraft-AI/src-tauri/src/lib.rs:1148)), 자동 업데이트 endpoint·서명·롤백 설정을 확인하지 못했다. 자동 업데이트 자체가 필수라는 뜻은 아니다. 수동 배포라도 버전 식별, 최신/지원 종료 안내, 무결성 확인, 백업·복구와 보안 패치 전달 방법은 있어야 한다.

출시 승인용 지원 항목은 오류/모델 중단/원천 API 차단/패치 drift의 분류, 비밀이 제거된 진단 수집, 지원 연락처, 정정·삭제 요청, 유료 기능 장애 시 보상·환불, 지원 범위·시간과 실제 담당자다. GitHub Issues 안내([README.md:374](D:/Pathcraft-AI/README.md:374))만으로 README의 유료 우선지원을 검증한 것으로 볼 수 없다.

## 9. 기존 제품 대비 차별성

현재 공식 제품 화면/문서를 직접 확인했다. 비교는 기능 존재 수준이며, 경쟁 제품의 전체 품질·가격·시장 점유율·Pathcraft의 성능 우위를 측정한 결과가 아니다. 확인일은 모두 **2026-09-21**이다.

| 비교 대상 | 공식적으로 확인한 겹침 | Pathcraft가 증명해야 할 가치 |
|---|---|---|
| [Path of Building Community](https://pathofbuilding.community/) | POE1/POE2 다운로드, 트리·젬·장비 계획과 변경 효과 비교 | PoB 수치/설정의 해석을 초보자가 정확히 행동으로 옮기게 하는 한국어 단계별 전환 안내. 현재 파서는 XML PlayerStat 등을 읽는다([pob_parser.py:450](D:/Pathcraft-AI/python/pob_parser.py:450)); 독립적인 계산 엔진 우위는 미확인. |
| [FilterBlade](https://www.filterblade.xyz/) | POE1/POE2 필터 편집, build auto-adjust, strictness, export/sync, 시뮬레이션, 자동 갱신 기능 안내 | 단순 필터 생성·색상·자동 조정만으로 고유 가치를 주장하기 어렵다. 실제 SSF/HC 전환 필수품 보존, 불확실한 타깃 검색, 패치별 안전성의 비교 증거 필요. |
| [Mobalytics POE2](https://mobalytics.gg/poe-2/builds) | 제작자/검증/커뮤니티 빌드, planner, build tracker, starter/endgame·HCSSF 분류 | 이미 같은 제작자 가이드와 추적 기능이 있다. 출처 있는 ‘지금 전환해도 되는 조건·비용·위험·대체품’의 정확도와 작업 절감이 추가 가치인지 확인해야 한다. |

**실제 자산의 긍정적 근거:** [python/hc_journey/README.md:3](D:/Pathcraft-AI/python/hc_journey/README.md:3), [:29](D:/Pathcraft-AI/python/hc_journey/README.md:29)는 스냅샷→변경→전환 노트 구조를 설명한다. [초반생존_방송상세분석.md:94](D:/Pathcraft-AI/deliverables/skadoosh_early_survival_2026-09-08/초반생존_방송상세분석.md:94)는 시점·근거·해석을 연결하고 조건부/미확인을 구분한다. 미추적 플래너도 실제 존재한다. 이 연구 품질과 한국어 HC/SSF 문맥은 **차별화 후보**다.

**한계:** hc_journey는 별도 Python/산출물 경로이며 현재 프런트와 등록 명령에서 직접 연결된 흐름을 확인하지 못했다. 해당 README의 ‘자동 100%’는 범용 정확도 증거가 아니다. 생성 제품의 차별성은 사용자 제약에 맞춰 실제 구성이 달라지고 그 조합·성장 경로가 검증되는 데서 입증해야 한다. 좋은 맞춤 연구나 단계 설명은 재료지만 그것만으로 생성 가치와 유료 앱이 완성되지는 않는다. 권한이 확보된 데이터로 이어갈 수 있는지도 별도 조건이다.

## 10. 단계별로 가능한 범위

### A. 로컬 개인용: 제한된 연구 활용

**권고 범위:** 본인이 보유·사용할 권한이 있는 입력, 직접 작성한 노트, 자신의 빌드 export를 이용한 읽기·정리·비교. 외부 전송 없는 흐름은 네트워크·키 의존을 별도로 확인한 뒤 사용하고, AI 호출 시에는 본인 키·비민감 입력·선택한 비용 상한·공급자 조건을 전제로 한다. 생성 안내는 검증 보조로 사용하며 HC 안전을 보장하는 판단 근거로 삼지 않는다.

‘개인용’이라는 이유로 ninja 내부 API 폴링, 방송 다운로드, GGPK/DLL 이용, 타인 가이드의 권리 문제가 자동으로 면제되는 것은 아니다. 위 정책상 미해결 기능은 중지 또는 허용된 경로 확인이 필요하다. 이 보고서는 기존 파일을 삭제하거나 수집기를 변경·실행하지 않았다. 자체 입력 위주의 로컬 사용 권고도 모든 행위에 대한 포괄적 법적 허가가 아니다.

### B. 소규모 비공개 사용자 검증: 조건부 진행

**현재 전체 원본이나 기존 설치물을 그대로 배포하는 것은 권고하지 않는다.** 다음 조건을 충족한 명시적 범위부터 무상 검증한다.

1. 지원 게임·패치·기능·검증할 질문을 고정한다. 권리 확인된 자료와 사용자 자신의 export만 포함하고 소유자 `.env`, 토큰, 내부 `.claude`, 원본 방송/전사, 개인 산출물을 배포에서 제외한다.
2. 구현 담당이 새 PC 설치·핵심 흐름·실패 안내를 실행 검증한다. 릴리스 후보와 데이터 manifest를 고정해 결과를 재현 가능하게 한다.
3. OAuth는 보완·검증 전 사용하지 않거나 출시 후보에서 명확히 비활성화한다. 키는 사용자별로 분리하며 외부 전송·비용·보존과 삭제 방법을 안내한다.
4. 유료 티어·Fine-tuned·공식 승인·무제한·생존 보장 문구를 사용하지 않는다. 지원 창구와 오류 신고·자료 철회 절차를 준비한다.
5. 평가 과제는 ‘사용자 조건에 맞는 완성 구성과 성장 경로가 생성되는가’, ‘조건을 바꾸면 실제 구성이 적절히 달라지는가’, ‘각 단계의 조합·자원·포인트·확보·전환 조건을 검증하고 미확인을 보류하는가’, ‘출처가 선택을 지지하는가’, ‘수정·재검증·재열기가 이어지는가’로 정한다. 외부 장애와 비용 차단도 포함하며, 단순 가이드 이해도만으로 생성 품질을 합격시키지 않는다.

테스터 수나 기간을 임의로 제시하지 않는다. 비공개 테스트도 공급자 약관·개인정보·콘텐츠 이용 조건을 무시할 근거가 아니며, 신규 자료를 자동 수집하는 실험은 별도 범위로 승인·검토한다.

### C. 유료화 승인 패키지

검토 책임자는 아래 증거가 준비된 뒤 정식 판매 여부를 판단해야 한다.

- **상품 명세:** 누구에게 무엇을 파는지, 앱·연구 산출물·서비스의 포함 범위, 게임/패치/플랫폼, BYOK/사업자 API, 가격·사용량·지원·환불 약속.
- **생성 품질 패키지:** 지원 빌드 계열·허용 변형·성장 구간별로 조건 입력→구성 생성→통합검증→수정·저장 증거. 공격/생존 성능의 검증 방법·가정, 조건 불충족/정보 누락의 보류, 출처·패치·revision 추적. 기존 선택 테스트·Atlas 수신 결과와 별도다.
- **권리 패키지:** §5의 모든 실제 출시 원천에 대한 상업 이용·수집·저장·번역·재배포 근거 또는 제외/대체 기록. OAuth 등록 증명과 지식재산 사용 허가는 분리.
- **출시/보안 패키지:** 현재 원본과 대응하는 재현 가능한 설치물, 비밀정보 없는 배포 명세, 새 PC 실행 결과, OAuth·키·개인정보 보완 및 삭제 검증, 업데이트·복구 경로.
- **과금/비용 패키지:** 선택한 판매 모델의 결제·권한·해지·환불 검증, 모든 API 시도의 사용량 원장, 지출 상한과 실패 정책.
- **품질/운영 패키지:** 지원 범위별 실측 검증, 출처·불확실성 표시, 잘못된 추천의 차단/정정, 패치 갱신 책임과 지원 이행 기록, 경쟁 대안과의 사용자 검증.

필요한 사용자 결정은 **출시 상품 범위, API 비용 부담 방식, 지원할 게임/패치, 이용 권한을 확보할 원천, 대상 시장·연령, 운영 책임자와 지원 약속**이다. 어느 항목도 이 보고서에서 임의로 확정하거나 프로젝트를 다른 상품으로 전환하지 않았다.

## 11. 납품 및 남은 검증

납품물은 이 `commercialization.md` 하나다. 원본 정적 분석과 공개 공식 문서 확인, 기존 설치물 파일/서명 메타데이터 검사를 완료했다. 조율에는 [orchestration 스킬](C:/Users/User/.agents/skills/orchestration/SKILL.md), OpenAI 조사에는 [OpenAI Docs 스킬](C:/Users/User/.codex/skills/.system/openai-docs/SKILL.md)을 적용했다.

남은 검증은 실제 설치/실행/테스트, 공급자 계정의 실제 접근·요율·보존 설정, OAuth 승인 원본, 결제/지원 운영 증거, 제작자·플랫폼·게임 자산의 개별 권한과 배포 라이선스 전수 대조다. 공개 페이지 회수 한계는 위에 각각 기록했으며 MCP 또는 인증 브라우저가 없다고 판단한 적은 없다. 책임자의 결과 수집·판단·정식 settlement/release를 대신하지 않는다.

## 12. 추가 실사: Atlas Viewer의 데이터 권리와 안정성

**추가 평가 시각: 2026-09-21 17시대 +07:00. 판정은 Atlas 기능의 상용화 보류다.** [전달 문서:1](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:1)와 [수신 계약:1](D:/contracts/atlas-viewer-to-pathcraft-app.md:1)을 전체 읽고, 원본 `deliverables/atlas_viewer_reference_2026-09-21`의 HTML·데이터·생성 스크립트를 정적으로 확인했다. 계약의 ‘상용 사용 불가 가정’은 보수적인 수신·검증 조건이며, 위법 또는 영구적인 상업 이용 금지가 확정되었다는 법률 판정으로 취급하지 않는다. [계약:5](D:/contracts/atlas-viewer-to-pathcraft-app.md:5), [:31](D:/contracts/atlas-viewer-to-pathcraft-app.md:31).

담당 범위는 R3의 **권리·유지보수 검토**다. 로컬 HTML 실행(R1), 전체 데이터 수 검증(R2), 실제 GGPK 직접 추출(R3 기술 검증)은 실행 담당의 별도 결과가 필요하다. 계약의 S1~S4 PASS는 **발신자가 기록한 검사 결과**이며 이번 작업자가 재현한 결과가 아니다. 이 장은 해당 결과를 덮어쓰거나 수신 계약을 정식 승인하지 않는다. [계약:19](D:/contracts/atlas-viewer-to-pathcraft-app.md:19), [:29](D:/contracts/atlas-viewer-to-pathcraft-app.md:29).

### 12.1 실제 출처와 증거의 경계

| 구성 요소 | 현재 사실·근거 | 권리·유지보수 판단 |
|---|---|---|
| 트리 그래프·노드·좌표 | 전달 문서는 poe.ninja 해시 이름 프런트엔드 번들 `assets.poe.ninja/_astro/a.Dfx976kX.mjs`에서 얻었다고 명시한다. 로컬 [atlas_tree.json:1](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/atlas_tree.json:1)과 파생 좌표 [screen_xy.json:1](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/screen_xy.json:1)이 있다. 상세 출처는 [전달 문서:56](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:56). | **미확인:** 번들 전체 또는 추출 필드의 상업적 재사용·재배포 근거. **추론:** 해시 파일명, 번들 내부 변수·구조는 업데이트에 따라 바뀔 수 있으므로 제품 데이터 공급 계약으로 삼기 어렵다. 좌표를 다시 계산해 저장했다는 사실만으로 원천의 권리 확인이 끝나지는 않는다. |
| 크리에이터의 할당 트리 | 문서는 Mobalytics `window.__PRELOADED_STATE__` 수집이라고 한다. [dslily.json:1](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/sources/dslily.json:1), [allie.json:1](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/data/sources/allie.json:1)에 제작자 표지와 할당 ID가 있다. [전달 문서:24](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:24), [:57](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:57). | 페이지 상태는 공식적인 버전 지정 데이터 계약으로 확인되지 않았다. 제작자 원본 이용 권한과 플랫폼을 통한 취득·이용 조건은 별도로 확인해야 한다. HC 수집 노트의 사용자 작업 승인은 제작자의 상업 이용 허락이 아니다(§5). |
| 선택형 옵션 이름·한국어 문자열 | 전달 문서가 `selectionName`의 Mobalytics 의존과 한국어 문자열 미비를 명시한다. [전달 문서:58](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:58), [:60](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:60). 이번 `data/sources` 문자열 검색에서는 `selectionName` 필드를 찾지 못했다. | **미확인:** 현재 산출물의 옵션 ID↔실제 선택↔표시명 전체 대응과 GGPK 대체 가능성. 문서의 출처 진술만으로 필드가 완전하게 전달되었다고 볼 수 없다. 그래프만 추출되고 옵션·조건·번역이 누락되면 R3의 완전한 대체로 인정하기 어렵다. |
| 방송 프레임·재구성 페이지 | [seongbin_atlas.html:1241](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/seongbin_atlas.html:1241)에 YouTube 영상·시각 링크가, [:1269](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/seongbin_atlas.html:1269)에 로컬 프레임 참조가 있다. [전달 문서:18](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:18), [:59](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:59). | 출처 표시가 재배포 허가를 대신하지 않는다. 영상 프레임, 해설 표현, 게임 그래픽, 추출한 할당 사실은 동일한 자료가 아니므로 각각 사용 범위를 정해야 한다. 숫자 ID라는 이유로 무조건 자유 이용 또는 침해라고 단정하지 않는다. 수동 판독도 새 패치마다 필요한 유지 비용과 오독 위험을 남긴다. |
| 분류·순서·SVG/HTML | [classify.py:3](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/classify.py:3)은 `ninja/atlas_tree.json`을 읽는다. [full_order.py:11](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_order.py:11), [hcguide/build.py:6](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/hcguide/build.py:6)은 스크래치 경로를 사용한다. | 독자적으로 작성한 UX·경로 코드와 포함 데이터의 권리·출처를 분리해야 한다. HTML이 정적 파일로 존재하는 것과 현재 폴더에서 원천부터 재생성 가능한 것은 별도 조건이다. 현재 경로 의존은 [전달 문서:25](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:25)도 인정한다. |

### 12.2 현재 공식 정책이 뒷받침하는 범위

아래 URL은 **2026-09-21에 실제 공개 본문을 확인**했다. 특정 계정의 계약이나 별도 허가는 확인하지 않았다.

- **poe.ninja:** [공식 API 문서](https://poe.ninja/docs/api)는 경제 API만 제3자 지원 범위로 두고, builds/profiles 등 내부 API의 제3자 이용을 제공하지 않는다고 명시한다. 이는 §5의 캐릭터 추적기 판정 근거다. **이 API 문장만으로 정적 프런트엔드 번들에서 얻은 Atlas 필드의 저작권·상업 이용 조건 전체가 확정되었다고 확대 해석하지 않는다.** Atlas 번들의 별도 사용 근거와 안정적인 공급 경로는 여전히 미확인이다.
- **Mobalytics:** [공식 이용약관 §4·§8](https://mobalytics.gg/terms/)은 개인 비상업적 이용, 상업 목적 이용 제한, 수집 도구 및 보호 조치 우회 제한을 규정한다. 페이지가 브라우저에서 보인다는 사실은 제품용 수집·재배포 권한의 증거가 아니다. 제작자가 직접 제공한 원본을 이용하는 경로는 플랫폼 상태 수집과 구분할 수 있지만, 게임 자산 등 다른 권리까지 자동으로 해결하지는 않는다.
- **GGG:** [공식 개발자 정책](https://www.pathofexile.com/developer/docs)과 [이용약관](https://www.pathofexile.com/legal/terms-of-use-and-privacy-policy)의 게임 IP·상업 이용 및 게임 파일 관련 조건을 검토해야 한다. **GGPK 추출 성공은 기술적 접근 가능성의 증거이며, 상업적 이용·재배포 허가의 증거가 아니다.** 로컬 추출 방식·사용 라이브러리·배포 자산의 구체적 범위에 대한 허용 근거가 필요하다.
- **공식 export의 실제 범위:** [GGG Data Exports](https://www.pathofexile.com/developer/docs/data)는 POE2 아래에는 Passive Skill Tree를, POE1 아래에는 Passive Skill Tree와 Atlas Passive Tree를 안내한다. 따라서 POE1 Atlas 저장소를 이번 **POE2 Atlas의 공식 대체 데이터**라고 제시할 수 없다. 이 문서에서 필요한 POE2 Atlas export를 확인하지 못했다는 판단이며, 모든 미공개·향후 경로의 부재를 단정하지 않는다.
- **방송:** [YouTube API 개발자 정책](https://developers.google.com/youtube/terms/developer-policies)의 영상·음성 내려받기 및 저장 제한은 해당 API 사용 조건이다. 이 문서 하나로 모든 비API 프레임 취득의 적법성을 판정하지 않는다. 사용한 취득 방식, 영상 제작자의 허락, 게임 화면·기타 포함 요소, 상업 배포 범위를 별도로 확인해야 하며 이번 작업에서는 새 영상을 수집하지 않았다.

해시 번들 자동 수집기를 제품화하거나 Cloudflare 등 보호 조치를 우회하는 방안은 대안으로 제시하지 않는다. 이는 [수신 계약:35](D:/contracts/atlas-viewer-to-pathcraft-app.md:35), [:36](D:/contracts/atlas-viewer-to-pathcraft-app.md:36)의 명시적 범위 제한이기도 하다.

### 12.3 대체 경로: 해결되는 부분과 남는 조건

| 대체 경로 | 기술적 가능성·해결 범위 | 권한·통과 조건 |
|---|---|---|
| **사용자 자신의 노드 할당·순서 입력** | 제작자 할당 트리 수집을 줄이는 유력한 입력 경로다. 현재 뷰어를 이 입력에 연결하는 구현과 검증은 별도다. | 사용자 입력만으로 지도 그래프·게임 문자열·아이콘의 출처 문제까지 해결되지 않는다. 자기 데이터와 타인 자료의 복사 입력을 구분하고 입력·저장·공유 범위를 정한다. |
| **허락받은 제작자 원본을 직접 제공받기** | 제작자가 제공한 노드 ID·단계·옵션 선택·직접 작성 설명을 계약된 포맷으로 받으면 Mobalytics 페이지 상태 수집 의존을 줄일 수 있다. | 실제 권리자가 상업 이용·편집·번역·표시·갱신·철회 범위를 허락한 기록이 필요하다. 플랫폼에서 다시 긁어온 파일을 단순히 ‘원본’으로 부르지 않는다. 게임 자산 허용 범위는 따로 남는다. |
| **공식적으로 제공·허용된 데이터 export** | 지원 게임과 Atlas 버전이 일치하는 공식 공급 경로가 있다면 우선 검토할 후보다. 현재 확인한 공식 페이지만으로 POE2 Atlas 제공은 입증되지 않았다. | 저장소별 라이선스·상업 사용 조건과 포함 자산을 실제 확인해야 한다. POE1 데이터 또는 캐릭터 Passive 트리를 POE2 Atlas 대체로 오인하지 않는다. |
| **허용 근거를 확보한 사용자 로컬 GGPK 추출** | 구현 담당이 Atlas PSG·PassiveSkills·문자열·옵션을 실제 읽고 재현 가능한 결과를 내야 한다. 전달 당시 직접 추출은 미시도·미확인이었다([전달 문서:56](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:56)). | 먼저 구체적 로컬 추출 행위의 허용 범위, 이후 상업 앱에서의 사용·파생 데이터 배포 권한을 구분해 확인한다. 고객 로컬 생성 방식도 자동 면제는 아니다. §5의 Oodle/DLL 사용·재배포 조건도 남는다. |
| **독자 합성 그래프·허락받은 작은 예제** | 단계 칩·순번·재생·접근성의 비공개 UX 검증을 진행할 수 있다. | 실제 PoB/캐릭터 기반 Atlas 가이드라는 원래 제품 목적의 완료 증거는 아니다. 실제 데이터 대체에 실패했다는 사실을 가리기 위한 출시 우회로로 사용하지 않는다. |

추천 순서는 **UX 검증을 보존하면서, 게임 그래프의 허용된 원천을 확정하고 사용자/허락받은 제작자의 할당을 별도로 결합하는 것**이다. 어느 대안도 이번 실사에서 구현·권한 확보를 완료한 상태는 아니다.

### 12.4 패치 변경과 HC 안내의 위험

**확인한 코드:** [classify.py:7](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/classify.py:7)은 stat ID를 이어 정규식으로 판정하며, [:13](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/classify.py:13)의 기본 반환값은 `안전`이다. 서브트리도 [full_order.py:41](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/scripts/full_order.py:41)에서 기본값이 `안전`이다. **추론:** 새 위험 효과·미등록 ID·빈 효과 목록이 안전으로 보일 가능성이 있으므로, 상용 HC 추천에서는 미분류를 ‘검토 필요’로 남기고 확정 안내를 멈추는 정책이 필요하다.

전달 문서의 58포인트 경로는 1,500가지 순서 탐색 결과이고 수학적 최소 증명이 없으며, 지역 레벨 70/75 조건 누락과 총 311/336 불일치를 미확인으로 적고 있다. 계약 S5도 서브트리와 초반 58 이후의 검증을 남긴다. [전달 문서:47](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:47), [:48](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:48), [:50](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md:50), [계약:23](D:/contracts/atlas-viewer-to-pathcraft-app.md:23), [:37](D:/contracts/atlas-viewer-to-pathcraft-app.md:37). 이를 최적·가장 안전·현 패치 완전 검증으로 광고할 근거는 없다. 총 노드 수, 실제 할당 가능한 노드, 시작점, 획득 가능한 포인트, 본 트리·서브트리별 예산을 분리해 확인해야 한다.

**권고 데이터 계약:** 원천별 권리 기록과 게임/패치/추출기/스키마 버전, 데이터 해시, 노드 ID·연결·좌표·루트·서브트리·할당 가능 여부, 조건과 효과 ID, 선택 옵션 ID·선택값·한국어/영문 표시명, 별도 포인트 예산을 트리 자료에 둔다. 할당 자료에는 작성자/사용자·허락 근거·대상 트리 버전·단계별 순서·옵션 선택·추천 이유와 불확실성을 둔다. 뷰어는 누락 노드·연결 단절·중복·유효하지 않은 선택·버전 불일치·예산 초과·미분류를 검출하고, 확인하지 못한 값을 임의로 안전/정상으로 보정하지 않아야 한다. 이는 향후 구현·검증 기준의 제안이지 현재 구현 완료 사실이 아니다.

### 12.5 Atlas 판매 승인에 필요한 별도 통과 조건

**사용자 보정 반영 — 메인 진행과 콘텐츠 내부 순서:** 메인 초록 단계 중 어떤 콘텐츠를 만나는지는 달라진다. 의식·균열·탐험 등을 하나의 필수 전역 순서로 묶거나 ‘의식부터 해야 한다’는 상품 설명을 해서는 안 된다. 현재 HTML은 서브트리 포인트가 별도라고 안내하면서도 [hc_atlas_order.html:113](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:113)에 ‘전체 순서’, [:114](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:114)에 ‘처음부터 전부’, [:131](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:131)에 ‘하코 아틀라스 전체 찍는 순서’라는 표현을 쓴다. **추론:** 범위를 구분하지 않은 안내는 콘텐츠 선택까지 의무 진행으로 오해하게 할 수 있다. 실제 재생에서 의식이 먼저 나오는지, 고객이 화면을 어떻게 이해하는지는 이 작업자가 실행 검증하지 않았다.

데이터 계약과 판매 설명에서 **메인 공통 진행**, **사용자가 선택한 콘텐츠별 내부 할당 순서**, **각 콘텐츠의 만남·해금·보유 포인트 조건**을 분리해야 한다. 콘텐츠 사이의 필수 선후관계를 만들어서는 안 되며, 전체 재생은 메인 기본 범위와 명시적으로 선택한 콘텐츠 범위를 구분해야 한다. 이것은 향후 통과 조건이다. 이번 작업에서는 UI나 제품 코드를 변경하지 않았다.

1. **R3 기술 증거:** 실행 담당의 실제 로컬 추출 명령·대상 게임 버전·성공/실패 로그·산출물 경로, 그래프와 선택 옵션·조건·표시 문자열 대응, 결과 비교 및 미해결 필드 목록. ninja 번들·Mobalytics 상태에 숨은 의존이 남지 않는지 확인한다. 파일 하나 생성되거나 노드 수만 일치하는 결과는 완전한 출처 교체의 증거가 아니다.
2. **R3 권리 증거:** 게임 원천·제작자 입력·플랫폼 취득·영상 요소·런타임 라이선스마다 예정된 상업 이용에 적용되는 허락 또는 명시 조건. 로컬 연구, 고객 기기에서의 생성, 개발자가 묶어 배포하는 방식의 차이를 기록한다.
3. **출시 품질 증거:** 수신 R1/R2와 S5의 남은 부분, 패치별 분류·연결·할당 가능성, 지역 조건과 포인트 예산을 실제 검증한다. 화면에 재생되는 순서가 캐릭터의 실제 진행 조건과 맞는지 별도로 검토한다. 선택형 노드와 한국어 누락을 숨기지 않는다.
4. **운영 결정:** 지원 패치·업데이트 책임·자료 철회/정정·이전 데이터 차단·재검증 실패 시 기능 중단 정책을 정한다. 계약이나 공급 경로의 지속성이 없으면 현재 수동 레퍼런스를 고객 서비스의 갱신 약속으로 바꾸지 않는다.

**출처 교체가 실패하거나 미검증이면 Atlas 상용화는 보류한다.** 기술 추출이 성공해도 권리 증거가 미확인이면 동일하게 보류한다. 반대로 허락만 있어도 실행·데이터 품질이 미검증이면 출시 승인이 아니다. 현재 이 작업자가 확인한 것은 원본 정적 자료와 공개 정책이며, R3 기술 성공 또는 상업 이용 허가를 확인한 결과는 아니다. 최종 수신·settlement/release는 조율자/검토 책임자의 검증 결과 취합 후 판단 사항이다.
