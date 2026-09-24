# Atlas Viewer 수신 검토 — 2026-09-21

수신 책임자: Run `run_a35fcc129e02`, 후임 `term_563ecf5f-053e-4df4-a387-b4af588997a2`. 평가 대상은 현재 실제 `D:/Pathcraft-AI` 전체이며, 이번 문서는 그중 전달된 Atlas 레퍼런스의 수신 판정이다. [전달 문서](D:/Pathcraft-AI/Docs/2026-09-21_ATLAS_VIEWER_REFERENCE_FOR_CODEX.md)와 [송수신 계약](D:/contracts/atlas-viewer-to-pathcraft-app.md)을 전체 읽고, 기존 분야 보고서·실행 로그를 취합했다. 후임은 새 브라우저 검사·테스트·게임 추출을 실행하지 않았다. 제품 코드·설정·원본 레퍼런스는 수정하지 않았다.

**결론: 뷰어 UX와 구조 자료는 앱 설계 참고로 수락한다. 개인 캐릭터 추천·앱 통합·현재 게임 유효성의 완료로 수락하지 않으며, R3 완전한 원천 교체와 권리 근거가 미완료이므로 Atlas 기능의 상용화는 보류한다.**

제품 목표 교정: 핵심 제품은 **수집자료와 사용자 조건으로 빌드·성장 경로를 생성**하는 것이다. Atlas는 생성된 빌드의 성장·획득을 돕는 **보조 진행 플래너**다. PoB/캐릭터는 선택 입력이며 전체 제품의 필수 출발점으로 강제하지 않는다. 이 문서의 R1/R2/R3는 해당 보조 레퍼런스의 검토로 유지하며 빌드 생성 품질 검증을 대신하지 않는다. [생성 준비도](D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/build_generation_readiness.md).

## 1. 송신 주장과 수신 결과

| 항목 | 수신 판정 | 증거와 적용 범위 |
|---|---|---|
| S1 화면 카운터 | 송신 PASS 보존 | 수신 JSON 계수는 같은 수치를 보이지만 방송 화면/현재 게임 카운터 재대조는 하지 않았다. |
| S2 초반 경로 | 저장 그래프 정합성 확인 | 기존 개인용 작업자가 루트 포함 59개 도달, 비루트 58개, 목표 11개, prefix 끊김 0을 계산했다. 게임 할당 적법성·최소 위험 최적성 증명은 아니다. |
| S3 목록 530/중복 0 | 수신 구조 확인 | 메인 336+콘텐츠 194, 순서 목록의 유일 ID 530, 비루트 집합 완전 일치. 전체를 동시에 쓸 수 있는 포인트 예산이라는 뜻이 아니다. |
| S4 브라우저 | 아래 R1의 조건부 관측으로 보완 | 송신자의 Chrome PASS와 수신자의 Playwright MCP 관측을 별개로 기록한다. |
| S5 위험 분류 | 부분 유지 | 본 트리 5건 수정은 송신 기록. 서브트리 위험 및 58 이후 순서 적대검증은 미완료다. 연결성 계산으로 이를 PASS로 바꾸지 않는다. |
| R1 실제 HTML 조작 | 기존 실행 보고 수락, 인코딩 조건부 | 기존 기술 작업자는 두 HTML의 칩·행 선택·재생/정지·처음부터·green→blue 경계·reduced-motion을 확인했다고 보고했다. 원시 출력 재대조 한계와 아래 전송 인코딩 제한을 적용한다. |
| R2 537/255 | PASS | 기존 개인용 작업자의 직접 JSON 계수와 명령·입력 해시가 보존돼 있다. 노드 537, 그룹 255, 루트 7, 비루트 530. |
| R3 GGPK 대체 | PARTIAL / 상용 보류 | PSG 2개 및 EN/KO PassiveSkills 2개 추출과 선두 필드 대응까지만 확인했다. 그래프 의미·좌표·링크·선택형 옵션·적용 조건을 갖춘 독립 대체 데이터는 미완성이다. |

수신 결과 상세와 재현 명령은 [기술 보고서](D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/technical.md), [개인용 보고서](D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/personal_product.md)에 있다. 이 문서의 수락은 보고서·설계 참고 범위이며 상품 출시 승인과 다르다.

## 2. R1의 정확한 경계

기존 기술 작업자는 Orca embedded browser의 `runtime_unavailable` 뒤 양쪽 클라이언트 MCP 연결 규칙을 확인하고 실제 Playwright MCP로 실행했다. 브라우저 부재로 간주해 정적 코드 검사만 한 결과가 아니다. 반대로 로컬 HTML 조작 확인은 외부 계정 로그인·영상 재생·Tauri IPC 성공의 증거도 아니다.

이 실행 이력의 현존 출처는 [인계문](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-audit-20260921/deliverables/readiness_audit_2026-09-21/manager_handoff_medium.md:81)의 기존 status `msg_f45bc6ca4a29` 요약과 HQ 확인 보고다. 후속 기술 편집자가 기존 Dispatch의 원시 transcript를 요청했으나 `transcript_required / session_not_reported`, auto fallback은 0행·contentComplete=false였다. 따라서 세부 브라우저 명령·화면별 assertion·console 오류 수를 후임이 직접 대조했다는 뜻은 아니다. 새 실행으로 이 공백을 메우지 않았으며, R1을 무조건적인 수신 독립 PASS로 표기하지 않는다.

원시 localhost HTTP 응답은 UTF-8 charset/meta 누락으로 브라우저가 EUC-KR로 해석했다. 원본 HTML을 수정하지 않고 라우트의 응답 charset을 UTF-8로 지정한 상태에서 기능을 검사했다. 따라서 **전송 인코딩을 보정한 기능 관측**과 **원본 파일의 배포 준비도**를 분리한다. 최종 통합에서는 실제 배포 경로의 한글 표시와 인코딩을 확인해야 한다.

행 선택으로 커서·순번이 바뀌는 관측을 자동 카메라 이동이나 재생 중 클릭 후 영구 정지로 확대하지 않는다. 현 [행 클릭 핸들러](D:/Pathcraft-AI/deliverables/atlas_viewer_reference_2026-09-21/pages/hc_atlas_order.html:3052)는 stop을 명시적으로 호출하지 않는다. 후속 앱의 “행 클릭 시 정지”는 제안 수용 기준이다. reduced-motion도 효과 제거와 핵심 정보 보존의 범위이며 전체 접근성 인증이 아니다.

## 3. R2와 색·포인트 해석

| 범위 | 비루트 노드 수 |
|---|---:|
| 메인 | 336 |
| 의식 | 36 |
| 인커전 | 36 |
| 심연 | 35 |
| 균열 | 32 |
| 환영 | 31 |
| 탐험 | 24 |

초록 표시 집합 191개는 메인 58+콘텐츠 133이다. 메인 초록 58개 안에도 저장 분류상 위험 3개가 있다. **단계 색과 위험 라벨을 별도 필드로 둔다.** 초록은 생존 안전 인증이 아니며 빨강도 모든 노드가 동일 위험이라는 뜻이 아니다. 각 트리 prefix 연결은 확인됐지만 직전 노드에 바로 붙는 이동만 있는 것은 아니다. 노드 계수는 실제 획득 가능 포인트·해금·현재 패치 유효성을 입증하지 않는다.

기존 R2 입력 식별: `atlas_tree.json` SHA-256 `cb460643cbb4c29d9efd9533ca6893a49498cc4a1870858f6eb58181686efe48`. 나머지 입력 해시와 계수 명령은 개인용 보고서 D절에 보존했다. 후임은 계수를 중복 실행하지 않았다.

## 4. R3에서 실제 확인한 것

기존 기술 작업자는 GGPK index와 관련 번들의 해시를 확인하고 Oodle 경로로 아래 네 파일만 임시 작업 공간에 선택 추출했다. 후임은 해당 [보존 로그](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/ggpk-read.log:1)를 읽었다. 추가 추출은 하지 않았다.

| 내부 경로 | 추출 바이트 | SHA-256 |
|---|---:|---|
| metadata/atlasskillgraphs/atlasskillgraph.psg | 19,336 | c705685dfd3028cddbd535ca718931a8ece1eed369d16b79f867c37e9986e9d4 |
| metadata/atlasskillgraphs/endgamemaplayoutgraph.psg | 29,028 | f511ae9708d8278e1886c8af86e22020241449394ff82f8c53e5ac46989f4c7f |
| data/balance/passiveskills.datc64 | 5,497,515 | 49af4f7dfab787b57efa22e06e2673c268cbd90c4f40140aa085cb8fbb602bc2 |
| data/balance/korean/passiveskills.datc64 | 5,415,801 | f3996270a036ffc1965b5203fff1eb6f75c3908075d8c424b5cd1d240562329f |

전체 테이블 해석은 [최초 로그](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/atlas-tables.log:1)의 stride assertion에서 멈췄다. 실제 행 487바이트, 스키마 392바이트다. 이후 보존된 [prefix 로그](C:/Users/User/orca/workspaces/Pathcraft-AI/readiness-technical-20260921/.audit-readiness/atlas-tables-prefix.log:1)는 Id/GraphId/Name만 제한적으로 읽어 EN/KO 각각 537 ID 대응과 언어 ID 일치를 보인다. 영문명 530/537이 일치하고 7루트는 빈 이름이다. 이것은 부분 이름 대응의 근거이며 나머지 필드의 스키마 적합성을 증명하지 않는다.

아직 증명하지 못한 것은 PSG 의미 파싱, 올바른 노드·연결·좌표 복원, 효과·지역 레벨 조건, 선택형 옵션 ID/값/한영 이름, 별도 포인트 규칙, 동일 패치 데이터로 재생성한 전체 레퍼런스다. 파일을 추출했다는 사실만으로 ninja/Mobalytics 의존이 제거됐다고 할 수 없다.

**권리 검토는 기술 가능성과 독립이다.** 이미 수락된 [상용화 보고서 §12](D:/Pathcraft-AI/deliverables/readiness_audit_2026-09-21/run_a35fcc129e02/commercialization.md)의 2026-09-21 공식 문서 확인을 따른다. [GGG 개발자 정책](https://www.pathofexile.com/developer/docs), [공식 Data Exports](https://www.pathofexile.com/developer/docs/data), [poe.ninja API 정책](https://poe.ninja/docs/api), [Mobalytics 약관](https://mobalytics.gg/terms/)을 근거로 원천·취득·이용·재배포 범위를 분리한다. 후임이 새 법률 조사를 수행한 것은 아니다. API 정책을 정적 번들의 모든 권리 판정으로 확대하지 않으며, 개별 허가 미확인을 위반 또는 허용 확정으로 바꾸지 않는다. GGPK/Oodle 접근 성공도 상업적 사용 허가가 아니다.

## 5. 사용자 보정을 반영한 앱 계약

**메인 진행과 콘텐츠별 내부 배분 순서를 분리한다.** 사용자는 메인 초록 단계 중 서로 다른 콘텐츠를 만난다. 의식 1→2→3은 의식을 선택했을 때의 내부 순서이며 의식을 먼저 플레이해야 한다거나 그 다음에 균열·탐험을 해야 한다는 뜻이 아니다. 콘텐츠 사이의 의무 선후관계는 이번 레퍼런스에서 도출하지 않는다.

| 객체 | 필요한 정보 | 판정 규칙 |
|---|---|---|
| TreeSnapshot | game, sourcePatch, revision, hash, sourceRefs/rightsStatus, treeId/rootId, nodes/edges/geometry, nameEn/nameKo, effect/choice/condition | 그래프/명칭/조건/권리 검증 상태를 분리. 누락·불일치를 정상으로 보정하지 않음 |
| PointPool | pointPoolId, treeId 매핑, available/allocated, observedAt, evidence, known/unknown | 메인과 콘텐츠 예산을 합산하지 않음. 336/530을 보유 포인트로 쓰지 않음 |
| ContentState | contentId, encountered, unlocked, 각각의 근거·시각·known/unknown | 만남·해금·포인트 보유를 같은 boolean으로 합치지 않음 |
| AllocationPlan | current/target 역할, treeHash, orderedStepsByTree, treeOrdinal, stageId, riskLabel/evidence, prerequisites/appliesWhen, choice, reason | 순서는 선택한 콘텐츠 내부에서만 해석. 게임에서 확인된 선행 조건만 사용하고 콘텐츠 나열 순서를 조건으로 만들지 않음 |
| ViewState | selectedScope(main 또는 선택한 contentId), selectedStage, cursor, playbackWithinScope, reducedMotion | 범위 변경 시 정지. ‘처음부터’는 선택 범위 안에서만 재생. 재생 진도와 실제 게임 할당을 분리 |

현재 단계만 강조하고 이전 단계는 흰색·이후는 흐리게 보이는 UX, 숫자·커서 링·목록 선택·정지·reduced-motion은 유지한다. 다만 ‘전체 재생’을 모든 콘텐츠를 차례로 의무 수행하는 경험으로 옮기지 않는다. 선택 범위와 해당 pointPool을 항상 표시하며, 미확인 조건이 있으면 “미리보기”와 “지금 배분 가능”을 분리한다. 콘텐츠 미선택·미해금은 메인 진행을 막지 않는다.

관측 가능한 후속 수용 사례:

1. 메인 초록 20번째에서 의식을 만나지 않았어도 메인 진행을 계속한다.
2. 균열을 먼저 만나 선택한 사용자는 균열 내부 순서를 열 수 있고 의식 완료를 요구받지 않는다.
3. 의식을 선택했으나 해금/포인트가 unknown이면 실제 배분 가능이라고 표시하지 않는다. 조건부 미리보기는 별도로 허용한다.
4. 재생·행 선택·범위 변경·저장/재열기 후 selectedScope와 커서가 일치하며 실제 할당 상태를 덮어쓰지 않는다.

위 사례는 앱 계약의 제안이며 현재 게임의 획득 규칙 또는 구현·실행 PASS를 주장하지 않는다. PoB만으로 없는 아틀라스 상태는 사용자 입력이나 확인된 별도 입력으로 받아야 한다.

## 6. 남은 조건과 납품 경계

S5 부분, 311 대 336 포인트 불일치, 지역 레벨 70/75 적용 조건, 0.5.5 포인트 획득 출처는 미해결로 남긴다. 분류기의 미등록 효과 기본값이 안전인 점도 패치 변경 위험이다. 완전한 원천 교체와 권리 근거, 개인 캐릭터의 다음 행동/보류 판단, 실제 앱 저장·재열기를 확인하기 전에는 상용 적격성을 선언하지 않는다.

이번 납품은 수신 검토와 데이터·UX 계약의 보완이다. 수집자료 기반 빌드·성장 경로 생성이라는 제품 목표 안에서 파밍·아틀라스·제작 계획을 보조로 연결한다. 보고서 완결은 생성 제품 완결과 다르다. Atlas 브라우저·GGPK 검증은 반복하지 않았고 제품 구현은 수행하지 않았다.
