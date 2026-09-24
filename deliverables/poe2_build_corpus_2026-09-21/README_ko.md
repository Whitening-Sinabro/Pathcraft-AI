# POE2 현재·0.5 계열 빌드 수집본 — 2026-09-21

신규 원문 **33개 가이드 / 25계열 / 24개 심층 전환 사례**를 수집·검수했다. 탱정 키타바는 별도 기존 우선 사례로 추가하여 catalog는 총34행이다. 기존 Seongbin·Skadoosh와 탱정 사례를 신규 목표에 가산하지 않았다. 상태는 전부 `collected_not_game_validated`다.

현재 사용은 [탱정 경로 00~07 안내](ACTIVE_ROUTE_ko.md)와 [HTML 탱정 경로](planner/transition.html)에서 시작한다. 탱정 원본 근거는 [키타바 방패벽 단계·최신 정정](priority_taengjeong_kitava_shield_wall.md)에 있다. **9/20 저자본 갱신과 아홉꼬리 저생명력 경로**는 과거 성찬식 전후 경로와 날짜를 나눴다. 카페 전체217개 목록을 확보했고 현재 본문93개, 목록의 댓글 수까지 일치한 관련 글93개를 확인했다. 정확한 완료 범위와 미확인은 [카페 coverage](cafe_coverage.json)에 있다.

| 파일 | 용도 |
|---|---|
| [플래너 시작](planner/index.html) | 현재·목표 세팅, 스킬 연결·장비·실제 패시브 트리 비교와 직접 편집 |
| [탱정 경로 게임 파일](taengjung_progression/native) / [참고 .build 안내](native_planner/README_ko.md) | 별이슬 액트(00~02)→맵 진입 탱정 1일차(03)→운명의 저항·황동 철갑(04)→아홉꼬리 묶음(05)→투구(06)→저자본 완성(07), 00~02 별이슬 액트 트리 + 03~07 탱정, 활성8개와 외부 백업 |
| [공통 근거 데이터](planner_data/README.md) / [관리자 검수](manager_planner_review.json) | HTML과 게임파일의 출처·패시브·무기세트·장비 대조 |
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

조회수·즐겨찾기·제작자 티어·poe.ninja 클래스 비중을 서로 다른 지표로 보존했다. 사이트의 현재0.5.5 배지는 본문 전체가 현 패치로 갱신됐다는 보장이 아니다. 정보가 없는 모드·날짜·전환 컷은 unknown/null로 남겼다. 수집 기록은 실전 성능이나 1.0.0 존속을 보장하지 않는다. 후속 사용자 지시로 아래 게임용 파일 설치와 HTML 플래너 보완을 진행했으며 제품 코드는 변경하지 않았다.

카페 자료는 초기 사용자 로그인 Chrome의 UIA 읽기와 이후 기존 Playwright MCP 프로필의 공개 DOM 읽기를 구분했다. 사용자 긴급 지시 후 UIA 자동 큐를 중지했다. 공개 MCP는 별도 로그아웃 프로필이며 같은 로그인 세션을 사용했다고 기록하지 않았다. 글 작성·댓글·가입·결제·쿠키/프로필 반출을 하지 않았다. 관련 공개 빌드 JSON/XML/CSV만 보존했고 룬트래커 실행파일은 다운로드·실행하지 않았다. 원본 `D:/Pathcraft-AI` 제품과 이전 감사·계획·탱정 조사폴더는 수정하지 않았다.

## 현재 빌드플래너 사용

활성 게임 파일은 탱정 9/20 방송 순서대로 00~02 별이슬 액트 트리와 03~07 탱정, 여기에 무자본(리그 스타터) 버전 03+를 더해 모두 9개이며, 이전 룬드 경로 5개와 그 전의23개는 게임 폴더 밖에 해시를 보존하여 백업했다. [탱정 경로 00~07 안내](ACTIVE_ROUTE_ko.md), [설치 기록](taengjung_install_receipt.json), [단계 검증](taengjung_progression/validation.json)이 현재 기준이다.

사용자 정정(2026-09-21)으로 Lundburgerr 맵 경로 후 전체 재분배하는 안은 폐기했다. 현재 경로는 탱정 9/20 방송 순서다: 액트는 별이슬골짜기 트리(00~02), 액트가 끝나면 탱정 1일차(03)로 전환한다. 03~06은 탱정 최신 29d39 트리의 연결된 부분집합으로 만든 Pathcraft 구성안(61/61/61/70점, 탱정 액트별 원본 트리가 아니다)이고, 07은 탱정 저자본 29d39 저장본 트리 그대로(118점)다. 03→07 일반 트리는 환불 없이 이어진다. 이전 Pathcraft 구성안18/26/37/47/56점과 룬드 자료(`lundburgerr_authored/`, `native_planner/active_route/`)는 역사 자료이고 과거 archive는 필수 진행 순서가 아니다.

HTML 단계 파일은 가이드이며 사용자가 편집한 세팅을 게임파일로 변환한 결과가 아니다. 현재·목표·초안·이력은 자동 덮어쓰지 않는다. 표시 범위1~100은 배분·획득 가능 레벨이 아니다. 게임 화면 확인과 실전 성능·하드코어 생존 검증을 구분한다.

카페 관련102글 중93개 본문·댓글을 확인했다. **160/158/149/135/131/129/121/120/112, 9글은 미완료**다. 승인된 확장 연결 복구1회는 초기화 후 browser_tabs가 1800초 시간 초과로 끝났다. 실제 사용자 Chrome의 탭·본문·댓글 읽기는 입증되지 않았으며 helper는 협조 종료했다. 브라우저 운영세션·요청 큐·테스트 프로필은 배포에서 제외한다. 이 한계를 플래너 정적 검증 완료와 구분한다.


파일 교체 후 패시브 또는 젬 가공 창을 닫았다가 다시 열어 갱신하세요. 열려 있던 창에는 이전 추천이 남을 수 있습니다. 게임 로그의 로드 성공은 파일 형식 확인이며 실전 성능·하드코어 생존 검증과는 별개입니다.
