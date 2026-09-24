import json
from pathlib import Path
P=Path(__file__).resolve().parent
v=json.loads((P/'validation_report.json').read_text(encoding='utf-8'))
c=json.loads((P/'cafe_coverage.json').read_text(encoding='utf-8'))['counts']
readme=f'''# POE2 현재·0.5 계열 빌드 수집본 — 2026-09-21

신규 원문 **33개 가이드 / 25계열 / 24개 심층 전환 사례**를 수집·검수했다. 탱정 키타바는 별도 기존 우선 사례로 추가하여 catalog는 총34행이다. 기존 Seongbin·Skadoosh와 탱정 사례를 신규 목표에 가산하지 않았다. 상태는 전부 `collected_not_game_validated`다.

가장 먼저 [탱정 키타바 방패벽 단계·최신 정정](priority_taengjeong_kitava_shield_wall.md)을 읽는다. **9/20 저자본 갱신과 아홉꼬리 저생명력 경로**는 과거 성찬식 전후 경로와 날짜를 나눴다. 카페 전체217개 목록을 확보했고 현재 본문{c['body_text_read']}개, 목록의 댓글 수까지 일치한 관련 글{c['target_comments_complete']}개를 확인했다. 정확한 완료 범위와 미확인은 [카페 coverage](cafe_coverage.json)에 있다.

| 파일 | 용도 |
|---|---|
| [플래너 시작](planner/index.html) | 입력한 단계·핵심품에 따라 지금 할 일을 안내하는 로컬 HTML |
| [catalog.json](catalog.json) / [catalog.csv](catalog.csv) | 빌드·변형·패치 근거·인기 지표의 범위·단계·조건·출처 연결 |
| [sources.jsonl](sources.jsonl) | 원URL, 게시/수정/접근일, 접근 상태, 주장 위치 |
| [build_notes](build_notes) | 각 레코드의 한국어 요약과 전환 조건 |
| [coverage_and_gaps.md](coverage_and_gaps.md) | 조사 범위, 알려진 빈칸과 성능 검증 한계 |
| [validation_report.json](validation_report.json) | 데이터 형식·참조·중복·날짜·심층 검수 검사 |
| [review_ledger.json](review_ledger.json) | 책임자가 원문에서 재확인한24개 심층 조건 및 추가 보완 |
| [cafe_article_index.json](cafe_article_index.json) / [cafe_coverage.json](cafe_coverage.json) | 217개 제목 선별, 본문/댓글/이미지/첨부 구분 |
| [priority_pob_extracts.json](priority_pob_extracts.json) | 과거4개·최신29d39·별도 참조1개 XML의 실제 구성 |
| [atlas_context_review.md](atlas_context_review.md) | 메인 아틀라스와 콘텐츠 내부 순서 분리 |
| [supervision_log.md](supervision_log.md) / [delivery_manifest.json](delivery_manifest.json) | 실제 Orca 작업자·정정·납품 해시 추적 |

조회수·즐겨찾기·제작자 티어·poe.ninja 클래스 비중을 서로 다른 지표로 보존했다. 사이트의 현재0.5.5 배지는 본문 전체가 현 패치로 갱신됐다는 보장이 아니다. 정보가 없는 모드·날짜·전환 컷은 unknown/null로 남겼다. 추천 실행, 제품코드 반영, 게임 적용, 1.0.0 존속 판단은 이번 납품 범위가 아니다.

카페 자료는 초기 사용자 로그인 Chrome의 UIA 읽기와 이후 기존 Playwright MCP 프로필의 공개 DOM 읽기를 구분했다. 사용자 긴급 지시 후 UIA 자동 큐를 중지했다. 공개 MCP는 별도 로그아웃 프로필이며 같은 로그인 세션을 사용했다고 기록하지 않았다. 글 작성·댓글·가입·결제·쿠키/프로필 반출을 하지 않았다. 관련 공개 빌드 JSON/XML/CSV만 보존했고 룬트래커 실행파일은 다운로드·실행하지 않았다. 원본 `D:/Pathcraft-AI` 제품과 이전 감사·계획·탱정 조사폴더는 수정하지 않았다.
'''
(P/'README_ko.md').write_text(readme,encoding='utf-8')
gaps=f'''# 범위와 남은 빈칸

신규 상세33개 원문 URL,25계열,심층24개. 책임자가 심층24개 모두 원문에서 실제 전환 조건을 다시 확인했고 일부 빈 필드를 보완했다. 9개는 상세 단계이며 심층으로 부풀리지 않았다. 소스는 현재{v['counts']['sources']}행이며 발견 전용·차단 URL은 열람 건수에 포함하지 않는다. 가이드 URL 수와 보조자료/카페 URL 수를 혼합하지 않는다.

현재 사용 현황은 poe.ninja의 명시적인 리그별 인덱스 표본이다. Forbidden Rites124098 / Rise of the Abyss124353 캐릭터, HC3480/12462, SSF5164/26463, HCSSF3391/8506은 작업자2026-09-21 12:13:10Z 관측값이며 HQ가12:25:14Z 교차 확인했다. 클래스 비중은 특정 빌드 점유율이 아니다. 기본 리그를 SC/Trade로 읽은 부분은 해석으로 표시했다. 공식 FAQ의0.5.5 Forbidden Rites와 기존 Rise 동시 운영도 별도 출처에 연결했다.

가이드·노트의 빌드 단계는 열린 본문의 표본이다. 모든 인터랙티브 변형, 패시브 이미지, 장비 수치 및 원본 영상을 전수 재생한 자료가 아니다. 이미지로만 제공되어 추출하지 못한 장비는 빈칸/한계로 유지했다. 실게임 테스트, PoB 엔진 재계산, HC 무사망, 최소 스탯 보장,1.0.0 생존을 검증하지 않았다. 날짜/배지와 본문의 불일치 및 미래 패치 언급은 기록했다.

카페 목록217개, 키타바 일반78개+중복공지2개, 연구소16개, 공용Tip1개를 끝까지 확인했다. 관련 본문 예정{c['target_body_articles']}개 중 현재{c['target_body_read']}개를 읽었고 {c['target_comments_complete']}개는 목록 댓글 수와 일치한다. 핵심{c['core_total']}개 본문 중{c['core_body_read']}개를 읽었다. 미열람·로딩 실패·이미지 미검증·개인 캐릭터 링크 미추적은 글별coverage에 남긴다. unrelated 게시판의 제목 선별을 본문 열람으로 세지 않는다.

탱정의 첫날 액트 전체 VOD는 미확보다. 대신 제작자가 연결한 별이슬골짜기0.5 액트 스크립트와0.5.5 업데이트, 빌드 첨부, 특정 화면을 확인했다. 워브링어→타이탄과 키타바의 전직을 분리했다. `.build`의 [0,100]과 PoB 최종 레벨은 실제 진입 레벨이 아니다. 9/20의 아홉꼬리 저생명력 경로는 작성자 지시와 실제 옵션으로 연결한 추론이며 플라스크 예외와 실제 유지 여부는 게임 검증이 필요하다.

도구 보조 스크립트는 이 납품폴더 안에만 있다. `assemble_corpus.py`는 초기33개 통합용이며 최종 우선 사례를 덮어쓸 수 있으므로 임의로 다시 실행하지 않는다. `integrate_priority.py`는 우선사례와 source 연결, `update_cafe_coverage.py`는 범위 집계, `validate_corpus.py`는 자료 계약 검증용이다. `cafe_ui.py`/`cafe_read_queue.py`는 실제 사용자창의 관측 URL에 한정한 읽기용으로 특정 세션 핸들을 포함하며 일반 배포 도구가 아니다.
'''
(P/'coverage_and_gaps.md').write_text(gaps,encoding='utf-8')
(P/'atlas_context_review.md').write_text('''# Atlas 수신·해석 검토

사용자 보정은 **메인 진행**과 **의식 등 콘텐츠별 내부 진행 순서**를 분리하는 것이다. 이를 수용했다. 의식·원정·균열 등 콘텐츠 사이에 필수 선수 순서가 있다는 뜻으로 쓰지 않는다.

별이슬골짜기의0.5.5 업데이트05:39–06:49는 초기 메인 아틀라스에서 에센스, 희귀 몬스터, 경로석 수급을 우선하는 해당 작성자의 제안이다. 탱정 키타바의 의무 트리 또는 모든 빌드의 공통 최적해로 승인하지 않는다. “그다음”은 해당 메인 트리 내부 투자 순서이며 콘텐츠를 반드시 에센스→의식→다른 콘텐츠 순으로 해금해야 한다는 근거가 아니다.

카페글109의 룬트래커는 스태킹/소문/가격 기능을 설명하지만 콘텐츠 간 필수 진행 순서를 입증하지 않는다. 글 제목 날짜와 본문09/05 변경이 달라질 수 있어 수정일은 확정하지 않았다. 실행파일은 확인 대상에서 실행하지 않았다.

원문 연결: [별이슬0.5.5](https://www.youtube.com/watch?v=zaft1U-7klQ&t=339s), [카페109](https://cafe.naver.com/f-e/cafes/31644155/articles/109). 기존 수락된 실행계획이나 제품코드는 이번 검토로 수정하지 않았다.
''',encoding='utf-8')
print('delivery prose refreshed')
