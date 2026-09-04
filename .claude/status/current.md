**지금**: 하코 문서 2종 재작성용 소스 보강 **완료**. 자막 49편 + 0.5.5 패치노트 판정까지 끝났다. 본문 집필 전이다.

**다음**: ①어느 빌드부터 쓸지 사용자 결정 대기 — 0.5.5 커버리지가 **바라시타 5명 / 화염파(Flameblast) 젬링 2명 / 방패벽 키타바 0명**으로 갈렸다(명부 "발견 2"). 방패벽은 패치가 죽인 게 아니라 크리에이터가 옮겨간 것으로 확인됨. ②집필 시작하면 자막 인용마다 명부 "발견 3" 표로 0.5.5 버그 수정 대조 필수(무기 세트 스냅샷 계열은 무효). ③9/5 패치 후 GGPK 재추출(아래 블로커).

**블로커**: POE2 GGPK 번들 인덱스 — **원인 재규명됨(2026-09-04). 우리 리더 결함이 아니다.**

- **GGPK 리더는 정상이다.** 같은 코드로 `gateway_list.txt` 를 뽑으면 UTF-16LE 텍스트가 정확히 읽힌다. FILE 레코드 레이아웃(헤더 68B = 4+4+4+32+이름)도 맞고, 산출 크기가 Rust 가 뽑은 113,947,385 와 정확히 일치한다. 그동안 "헤더 파싱이 죽는다"로 적어 둔 것은 리더가 아니라 **내용물 문제**였다.
- **`Bundles2` 구조가 바뀌었다.** 예전엔 평평했는데 지금은 하위 디렉터리 `Streaming` · `Folders`(16진수 이름 265개) · `Content`(art/data/metadata) 가 있고, **`_.index.high.bin` · `_.index.low.bin`(각 74B)** 이 새로 생겼다. 분할 인덱스로 보인다.
- **`_.index.bin`(113MB) 은 더 이상 평범한 Oodle 번들이 아니다.** 앞 8KB 를 4바이트 단위로 전수 스캔해도 유효 번들 헤더(compressor 9/12/13 + 정상 크기 + chunk_size 256KB)가 **0건**이고, 4KB 안에 고유 바이트가 233/256 이라 압축 또는 암호화된 상태다. 프리픽스가 붙은 단순 오프셋 문제가 아니다.
- 같은 폴더의 `Tiny.V*.bundle.bin` 중 **일부는 여전히 유효**하다(VE · V5 · V4 · V3.1 · VB · V2 · V7 · VE.1, 전부 compressor=9). 나머지는 헤더가 깨져 보인다 — 포맷이 섞여 있다.
- **`Bundles2/Content/data/` 우회는 안 된다.** `balance/worldareas` 만 있는 **희소 오버레이**다(패치된 일부 파일만). 전체 테이블은 여전히 번들 안에 있다.
- 설치 경로가 바뀌어 자동 탐지도 실패한다 — `--game poe2 "C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2 - poe2_production"` 로 직접 줘야 한다. Content.ggpk 는 **142.2 GiB**.
- 다음 수: `_.index.high.bin`/`_.index.low.bin`(74B) 부터 뜯어 새 인덱스 규약을 찾는다. LibGGPK3/LibBundle3 최신 커밋 대조가 빠른 길.
- 프로브 스크립트: `scratchpad/ggpk_probe.py` (트리 전체 재귀는 142GB 에서 안 끝난다 — 루트→Bundles2 만 직접 탈 것).

**포인터**:
- 하코 소스 명부(조사 방법·자막 49편 대응표·"방패벽은 하나의 빌드가 아니다"·0.5.5 버그수정 대조표·핸들 정정표) → `.claude/status/poe2_hardcore_sources.md`
- 자막 읽기 → `PYTHONIOENCODING=utf-8 python scripts/read_subs.py <file.json3> [검색어…]`
- POE2 가이드·필터·카드 파이프라인(산출물 위치·발행 닥 ID·디스코드 메시지 ID·주입 지뢰) → `.claude/status/poe2_guides.md`
- 0.5.5 패치노트 원문 → `data/_cache/patchnotes/poe2_0_5_5{,_faq,_filter_info,_press_release}.txt`
- 가이드 기준 템플릿 스펙 → `~/.claude/projects/D--Pathcraft-AI/POE2_BUILD_GUIDE_TEMPLATE.md`
