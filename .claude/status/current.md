**지금**: 하코 문서 2종 재작성용 소스 보강 **완료**. 자막 49편 + 0.5.5 패치노트 판정까지 끝났다. 본문 집필 전이다.

**다음**: ①어느 빌드부터 쓸지 사용자 결정 대기 — 0.5.5 커버리지가 **바라시타 5명 / 화염파(Flameblast) 젬링 2명 / 방패벽 키타바 0명**으로 갈렸다(명부 "발견 2"). 방패벽은 패치가 죽인 게 아니라 크리에이터가 옮겨간 것으로 확인됨. ②집필 시작하면 자막 인용마다 명부 "발견 3" 표로 0.5.5 버그 수정 대조 필수(무기 세트 스냅샷 계열은 무효). ③9/5 패치 후 GGPK 재추출(아래 블로커).

**블로커**: POE2 GGPK — **해결. 리버싱 불필요. 게임을 켜서 패치를 끝내면 된다.**

원인을 두 번 잘못 적었다. 최종 판정(2026-09-04):

- **우리 리더는 멀쩡하다.** GGPK FILE 레코드에 든 32바이트가 내용의 SHA256 인데,
  `gateway_list.txt` · `Tiny.V5.bundle.bin` · `_.index.high.bin` 모두 **저장 해시와 실제
  해시가 일치**한다. 반면 **`_.index.bin` 의 저장 해시는 전부 0** 이다 — GGPK 스스로가
  그 레코드를 미완성으로 표시하고 있다.
- **원인은 중단된 패치다.** `logs/Client.txt`:
  `2026/06/25 [BUNDLE] Bundle index: Bundles2/_.index.bin` 로 **6월엔 3회 정상 로드**했고,
  `2026/08/30 00:00:00 Queue file to download: Bundles2/_.index.bin` 로 인덱스를 포함해
  **72,878개 파일을 다운로드 큐에 넣은 뒤**,
  `00:07:22 [WARN] Recv failure: Connection was reset` 로 끊겼다. 그 상태로 멈춰 있다.
- **해시 0 = 헤더 파싱 실패**가 예외 없이 일치한다. Bundles2 루트는 **실물 8 / 자리표시자 30**.
  자리표시자만 골라 "포맷이 바뀌었다"고 판단했던 것이다.
- **`compressor=8` 도 유효하다.** 앞선 스캔이 `9/12/13` 만 유효로 잡아 `_.index.high.bin`
  (정상 74B 번들)까지 "번들 아님"으로 오판했다.
- Bundles2 하위에 `Streaming/` · `Folders/`(16진수 253~265개) · `Content/`(경로 뼈대 +
  디렉터리별 `ggdh` 해시)가 생긴 것은 **사실**이지만 스트리밍 설치 레이아웃이지 장벽이 아니다.
  `Content/` 안에는 `*.vworld.bundle.bin` 같은 실제 번들도 있다.

**다음 수: 게임 클라이언트를 켜서 패치를 끝까지 받는다.** 어차피 9/5 리그 시작 전에 받아야 한다.
그 뒤 `extract_data.exe --game poe2 "<설치경로>" --json` 을 다시 돌리면 된다 —
자동 탐지는 폴더명이 `Path of Exile 2 - poe2_production` 으로 바뀌어 실패하므로 **경로를 직접 준다**.
받은 뒤 `_.index.bin` 의 저장 해시가 0 이 아닌지부터 확인하면 성공 여부를 바로 안다.

**PackCheck.exe 는 결손을 못 고친다 (2026-09-04 실측).** 설치 폴더의 GGG 자체 도구인데
로그를 보니 **서버 접속·다운로드가 0건**이고, 하는 일은 청크 검사 -> **콘텐츠 해시 재동기화**
-> free chain -> compaction 뿐이다. 즉 낡은 바이트 위에 해시만 맞춰 놓는다.
**부작용: 돌리고 나면 "저장 해시가 0 = 패치 미완료" 단서가 사라진다.** 그게 이 블로커를
깬 근거였으므로, 이후에는 그 방법으로 진단할 수 없다 — 대신 `logs/Client.txt` 의
`Queue file to download` / `Recv failure` 를 본다. 클라이언트 패치 자체에는 영향이 없다
(패처는 서버 매니페스트와 대조하지 GGPK 내부 해시를 믿지 않는다).

**진단 도구**: `python scripts/ggpk_explore.py ls|cat|verify <GGPK 내부 경로>`.
142GB 라 트리 전체 재귀는 안 끝난다 — 경로를 따라 한 단계씩만 내려간다.

**포인터**:
- 하코 소스 명부(조사 방법·자막 49편 대응표·"방패벽은 하나의 빌드가 아니다"·0.5.5 버그수정 대조표·핸들 정정표) → `.claude/status/poe2_hardcore_sources.md`
- 자막 읽기 → `PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3> [검색어…]`
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·주입 지뢰) → `.claude/status/poe2_guides.md`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
