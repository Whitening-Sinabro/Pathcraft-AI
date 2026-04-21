# 패시브 트리 Asset 추출 + 렌더 — Run-time 하이브리드

> 2026-04-20 결정. 사용자 피드백: PoB 수준 class portrait + tri-color mastery 필요.
> 근거: `_analysis/syndicate_ux_research_2026-04-20.md` 별도. 본 문서는 패시브 트리 자산 계획.

---

## 결정 요약

| 축 | 결정 |
|---|---|
| **추출 시점** | Run-time (사용자 첫 실행 시 or 설정) |
| **Fallback** | SVG placeholder 7 클래스 (번들 포함) |
| **라이선스** | 추출 자산 저장소 **미커밋** (GGG 저작권) |
| **DAT 소스** | `uiartascendancy.datc64` + `passiveskilltreeuiartascendancy.datc64` |
| **이미지 포맷** | DDS → PNG 변환 (Rust `image` + DDS crate) |
| **저장 경로** | `data/skilltree-export/assets/classes/` (`.gitignore` 추가) |

---

## Phase 분할

### P1 — SVG placeholder (번들 포함, POE 없어도 동작) ✅ 완료 2026-04-20
**목표**: 7 클래스 시각 식별 가능. PoB 수준은 아니지만 "검은 화면 + 프레임"보다 현저히 나음.

**설계**:
- 클래스별 색 (STR=red, DEX=green, INT=blue, 혼합 2색, Scion=tri-wedge)
- 원형 disc + 외곽 ring + 이니셜 (M/R/W/D/T/S, Scion=S gold/tri)
- 단일 컴포넌트 `ClassPortrait` — `classIndex` prop으로 7 variant

**Canvas 오버레이 전략** (실제 구현):
- classStart world 좌표 → screen 좌표 변환 (rAF 내 imperative 업데이트)
- 절대 포지션 DOM wrapper 7개 + `<svg width=100%>`
- pointer-events: none (canvas 클릭 보존)
- 직경 = `node.radius * 2 * camera.scale` (호버 링 1.4x 반경보다 작음 → 호버 링 가시)

**파일**:
- 신규: `src/components/passive-tree/ClassPortrait.tsx` (90줄)
- 수정: `PassiveTreeCanvas.tsx` (import + portraitRefs + overlay JSX + rAF 업데이트)

**검증**:
- tsc noEmit clean
- 82 vitest 통과
- 인게임 확인은 사용자 영역 (P1 완료 조건)

---

### P2 — DAT 테이블 파싱 (art 경로 추출)
**목표**: 실 GGPK DDS 경로 확보.

**작업**:
- `data/uiartascendancy.datc64` 스키마 확인 (`_analysis/ggpk_truth_reference.json` 활용)
- `data/passiveskilltreeuiartascendancy.datc64` 동일
- 테이블 row → art path 매핑 출력

**파일**:
- 신규: `src-tauri/src/bin/dump_passive_art_paths.rs`
- 수정: `src-tauri/src/schema.rs` (필요 시 스키마 추가)

---

### P3 — DDS 추출 + PNG 변환 + manifest
**목표**: 사용자 POE → 로컬 PNG + 매핑 JSON.

**작업**:
- Cargo: `image` + `ddsfile` (또는 `image-dds`) crate 추가
- CLI: `extract_tree_assets.rs`
  - BundleIndex 로드
  - P2에서 얻은 path 루프
  - DDS 바이트 → 디코드 → PNG 쓰기
  - `manifest.json` 생성: `{classes: {0: {name, portrait_path}}, ...}`

**저장 구조**:
```
data/skilltree-export/assets/ (gitignored)
├─ classes/
│  ├─ scion.png
│  ├─ marauder.png
│  ├─ ranger.png
│  ├─ witch.png
│  ├─ duelist.png
│  ├─ templar.png
│  └─ shadow.png
├─ ascendancy/
│  └─ {asc_name}.png
└─ manifest.json
```

---

### P4 — Renderer 통합
**목표**: Canvas가 manifest 읽어 class portrait 오버레이.

**작업**:
- manifest.json fetch
- classStart 노드 id ↔ class portrait 매핑
- Canvas 오버레이 또는 canvas draw (성능 비교 후 결정)
- Placeholder fallback (manifest 없으면 SVG)

**선택**:
- (a) DOM 오버레이 (SVG/img absolute position)
- (b) Canvas drawImage (HTMLImageElement preload)
**추정 권장 (b)** — zoom/pan 동기화 자연.

---

### P5 — 자동화
**목표**: 리그 업데이트 시 재추출.

**작업**:
- `npm run refresh-tree-assets` 스크립트
- Tauri 앱 내 "자산 재추출" 버튼 (설정)
- GGPK mtime 감지 → 자동 안내

**파일**:
- `package.json` script 추가
- 앱 설정 UI (추후)

---

### P6 — First-run UX
**목표**: 사용자 온보딩.

**작업**:
- 패시브 탭 첫 진입 시 manifest 없으면 안내 배너
- "POE 경로 지정 → 자산 추출" 버튼
- 추출 중 progress bar
- 실패 시 SVG fallback 유지 + 재시도 버튼

---

## 라이선스 / git 관리

### .gitignore 추가
```
# POE 추출 자산 — 저작권상 재배포 금지 (사용자 local 추출)
/data/skilltree-export/assets/classes/
/data/skilltree-export/assets/ascendancy/
/data/skilltree-export/assets/manifest.json
```

### README 명시
- "첫 실행 시 사용자 POE에서 class portrait 자동 추출"
- 저장소에 **추출 자산 미포함**

---

## 확장 인터페이스 (P5 이후 고려)

```rust
pub trait AssetExtractor {
    fn name(&self) -> &str;
    fn extract(&self, idx: &mut BundleIndex, oodle: &OodleLib, out: &Path) -> Result<()>;
}

pub struct ClassPortraitExtractor;   // P3
pub struct AscendancyExtractor;      // P3
pub struct SkillIconExtractor;       // 미래 (젬 아이콘)
pub struct ItemArtExtractor;         // 미래 (아이템 이미지)
```

단일 CLI가 모든 extractor 호출. 각 extractor 독립 검증.

---

## 우선순위 결정 포인트

1. **P1 먼저**: SVG placeholder로 "검은 프레임" 문제 즉시 해소 → 사용자 급한 불 끔
2. **P2+P3 다음 세션**: DAT 파싱 + 추출 파이프라인
3. **P4 통합 후**: 실 portrait 렌더 확인
4. **P5+P6 최종**: 자동화 + UX

**현 세션 범위**: P1만. 나머지는 차후.

---

## 참조

- `_analysis/syndicate_ux_research_2026-04-20.md` — 사용자 피드백 기록
- `_analysis/ggpk_truth_reference.json` — DAT 테이블 스키마
- `src-tauri/src/bin/scan_class_assets.rs` — 기존 스캐너 (경로 탐색용)
- `src-tauri/src/bin/extract_data.rs` — DAT 추출 CLI 패턴
