# GGPK Truth Reference — Layer 2 & 4

`_analysis/ggpk_truth_reference.json`의 **독립 검증 계층**.

## Layer 2 — 독립 추출기 cross-check

### 원리

우리 Rust `extract_data`와 SnosMe `pathofexile-dat`(npm)는 완전 독립 구현이다.
동일 GGPK 데이터에서 동일 결과 → 우리 추출 파이프라인의 schema 호환 + 파싱 정확도 둘 다 신뢰 가능.

### 실행 순서

```bash
# 1. 독립 추출기 설치 (1회, 110KB)
npm install -g pathofexile-dat

# 2. 최신 patch 버전 확인 후 config.json 업데이트
curl -s https://raw.githubusercontent.com/poe-tool-dev/latest-patch-version/main/latest.txt
# → config.json의 "patch" 값 교체

# 3. 독립 추출 (약 1~2분, ~35MB 캐시 + ~50MB 다운로드)
cd _analysis/crosscheck
node "$(npm root -g)/pathofexile-dat/dist/cli/run.js"

# 4. 비교 실행
cd ../..
python python/scripts/ggpk_crosscheck.py

# 5. pytest 검증
python -m pytest python/tests/test_ggpk_crosscheck.py -v
```

### 현재 커버리지 (7 테이블)

Characters, Ascendancy, Tags, Scarabs, ScarabTypes, Flasks, GemTags.
`config.json`에서 확장 가능.

### 캐시/산출물 gitignore

- `_analysis/crosscheck/.cache/` — 독립 추출기의 bundle 캐시 (35MB)
- `_analysis/crosscheck/tables/` — 독립 추출기 산출 JSON

커밋되는 것: `config.json`, `README.md`, `report.json`(선택).

## Layer 4 — 인게임 골든 스크린샷

코드/스키마와 무관한 ground truth. 사용자가 수동으로 캡처.

### 필요 스크린샷 (리그 시작 시 1회)

| # | 화면 | 용도 | 검증 가능 항목 |
|---|------|------|----------------|
| 1 | **Ascendancy 선택 화면** (패시브 트리 우클릭 → Ascend) | 어센던시 수 | `Ascendancy.rows` (현재 20) |
| 2 | **Character 선택 화면** (로그인 직후) | 클래스 수 | `Characters.rows` (현재 7) |
| 3 | **스카랩 스택 탭** (currency 탭 → 스카랩 슬롯) | 스카랩 family 수 | `ScarabTypes.rows` (현재 27) |
| 4 | **Gem Progression 화면** (`L` 키, 젬 가이드) | Gem tag 계열 | `GemTags.rows` 샘플 (현재 53) |
| 5 | **Flask inventory 우클릭 → Flask types** | Flask base 수 | `Flasks.rows` (현재 51) |

### 저장 위치 (gitignore)

`_analysis/crosscheck/screenshots/YYYY-MM-DD_league/*.png`

`.claude/status/current.md`에 "다음 리그 시작 시 스크린샷 갱신" 리마인더 추가.

### 스크린샷이 왜 필요한가

- 코드가 GGPK를 잘못 파싱하고 레퍼런스 JSON에 잘못 박제했을 때, 게임 UI는 여전히 사실을 보여준다
- 리그 전환 시 패치노트의 요약이 누락되면 스크린샷 비교로 발견 가능
- 완전 자동화 불가능한 1계층 — 인간의 눈이 최종 anchor

## 실패 시 대응

| pytest 실패 | 원인 | 조치 |
|-------------|------|------|
| `test_all_content_hashes_match` 불일치 | 리그 변경 또는 회귀 | `anchored_to.expected_changes` 확인 → 설명되면 builder 재실행, 아니면 원인 조사 |
| `test_schema_sha256_matches_pin` 불일치 | schema.min.json 변경 | content_hash 전부 재해석 필요 → extract 재실행 |
| `test_anchor_not_stale` 실패 | 180일 경과 | 최신 리그 패치노트 확인 + `verified_at` 갱신 |
| `test_table_matches_independent_extractor` 불일치 | 독립 추출기와 diff | 양쪽 출력 비교 → schema 해석 차이 조사. 우리 실수면 수정, 라이브러리 이슈면 리포트 |
