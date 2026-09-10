# HC 여정 DB #1 — 규칙 자동 초안 (다음 세션 실행 지시)

사용자가 "다음 세션에서 1번 하자"고 지정했다. 이 문서는 그 실행 지시다. 요약이나 계획만 쓰고 멈추지 말고 실제 스크립트·테스트·커밋까지 진행한다.

작업 폴더 D:/Pathcraft-AI. master 최신 = `5bb406a`. 실질 변경이므로 자체 테스트까지 하고, 판돈이 커지면(배포·조용한 실패) 독립 적대검증을 건다(개인 로컬 도구면 자체 테스트로 충분).

## 먼저 읽기

1. 메모리 `project_hc_journey_db`(제품 축·아키텍처 정본), `project_poe2_hardcore_sources`(명부·자막 함정), `feedback_no_invented_labels`·`feedback_english_source`.
2. `python/hc_journey/README.md`, `schema.sql`, `build_db.py` — 특히 `CURATION_RULES`와 규칙 매처(keystone·skill_added·item_slot_change·ascendancy 트리거).
3. `deliverables/seongbin_from_day1_2026-09-09/transcripts/*.json` — 타임스탬프 자막(segments: start·duration·text). A=zKJQyBm4VnI B=GtC5-b4QXec C=C_tkSubXWDk D=39kHWKUhwhU E=xnREtaV3m1A.

## 배경 (왜 이 작업인가)

여정 DB는 자동 diff(WHAT/WHEN)는 공짜로 나오고, 차별화 20%(비용·조건·함정·왜)는 `curation_rule`로 담는다. 규칙은 한 번 쓰면 모든 빌드에 자동 상속된다(Skadoosh 손0·규칙8로 증명). **그런데 규칙을 손으로 쓰는 것 자체가 병목이다.** 이 작업은 그 규칙 작성을 반자동화한다 — 전환점 근처 자막에서 규칙 후보를 뽑고, 사람은 승인만.

## 이번에 만들 것

`python/hc_journey/rule_autodraft.py` (+ `python/tests/test_rule_autodraft.py`):

1. **입력**: 자막(transcripts) + 각 빌드의 전환점(자동 diff가 이미 아는 "어느 스킬/키스톤/장비/어센던시가 언제 바뀌나"). 전환점의 대략 시각을 알면 그 근처 자막 창을 본다. (임성빈은 판독으로 (영상,초)가 이미 많음 — precision_findings.py 활용 가능.)
2. **후보 추출**: 전환점 근처 자막에서 신호를 뽑아 `(trigger_kind, trigger_key, note_type, text, evidence)` 후보 생성.
   - note_type 신호: cost(골드·엑잘티드·신성한 오브·수수료·숫자), condition(요구 레벨·요구 지능·"~해야"), pitfall("죽었다"·"안 먹힌다"·"바꿔야"·"잘못"), why(키스톤명·메커니즘 설명), survival(저항·부활·플라스크).
   - trigger 매핑: 키스톤명 언급→keystone, 스킬명 도입→skill_added, 무기 세트/슬롯→item_slot_change, 전직명→ascendancy.
3. **출력**: 승인 대기 후보 목록(예 `data/hc_journey/rule_candidates.json`). 사람이 골라 `CURATION_RULES`에 반영(자동 반영 금지 — 승인 게이트).
4. **정직성**: 자막은 자동 생성이라 고유명사가 깨진다(명부 doc의 왜곡 표 참고). **이름은 자막에서 확정하지 말고 PoB/GGPK/전환 diff에서 얻는다.** 자막은 *수치·주장·정황*의 근거로만. 지어낸 라벨 금지.

## DoD

- 초안기가 임성빈 자막에서 규칙 후보를 실제로 N(≥5)개 뽑는다.
- 후보가 `(trigger_kind, trigger_key, note_type, text, evidence)` 스키마로 나오고, evidence에 (영상,초)가 붙는다.
- 승인 게이트: 자동으로 CURATION_RULES를 바꾸지 않는다(후보 파일만 생성).
- test 통과. 기존 `test_hc_journey_db.py` 4건도 여전히 green.
- 커밋·푸시(master). 커밋 메시지 끝에 Co-Authored-By + Claude-Session.

## 경계

- POE2 하드코어(→SSF) 니치 유지. 다른 게임·범위로 새지 말 것.
- `data/hc_journey/creators/` 픽스처·`build_db.py` 기존 규칙·테스트를 깨지 말 것.
- `.db`는 산출물이라 git 제외 유지.
- 외부 전송·게시·프로세스 종료 없음.

## 시작 상태 (인계)

- 여정 DB: 2 크리에이터·2 빌드·규칙 11·노트 24(손 8·규칙 16). `python -X utf8 python/hc_journey/build_db.py --build --query`로 재현.
- 자막 5편 커밋됨. 임성빈 판독 358건(precision_findings.py, (영상,초)+관찰).
- 이 세션 커밋: 656dc44(조사+엔드게임 플래너)→e3f4a59(스키마)→8869173(다중)→abf1db0(규칙 엔진)→5bb406a(규칙 확장+버그).
