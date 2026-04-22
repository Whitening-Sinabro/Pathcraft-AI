# POE2 Passive Tree — 데이터 소스 + 어댑터 계획 (D4)

> 2026-04-22 S3. GGPK `PassiveSkills.datc64` 에는 좌표/연결이 없음 → 외부 소스 필요.

---

## 1. 데이터 소스 결정

### 선정: `PathOfBuildingCommunity/PathOfBuilding-PoE2`
- URL: `https://raw.githubusercontent.com/PathOfBuildingCommunity/PathOfBuilding-PoE2/dev/src/TreeData/0_4/tree.json`
- 버전: **0.4** (현재 PoE2 리그 대응 최신)
- 크기: 1,812,234 bytes (≈1.8 MB)
- 라이선스: MIT (PoB 코드), 데이터는 GGG 저작물 (업계 관행상 공개 사용)
- 로컬 저장: `data/skilltree-export-poe2/tree_0_4.json`

### 기각
| 후보 | 이유 |
|---|---|
| `grindinggear/skilltree-export` | POE1 전용 (최신 3.28.0 Mirage). POE2 분기 없음 |
| `marcoaaguiar/poe2-tree` | "scuffed version... extracted from videos and screenshots" — 정확도 미보장 |
| `poe-tool-dev/passive-skill-tree-json` | POE1 patch history 미러만 (0.9.6~3.25.0) |
| GGPK `PassiveSkills.datc64` | 7676 rows — 메타데이터뿐, 좌표/연결 없음 |

### POE2 → GGPK 브리지 (참고)
- `tree.json` node `skill` 필드 == GGPK `PassiveSkills.PassiveSkillGraphId`
- 교차 매치율: 2302/4701 (49%) — 나머지는 어센던시/프록시 노드
- tree.json 자체가 render 에 필요한 필드(name/stats/icon) 를 이미 포함 → GGPK 교차 필수 아님

---

## 2. Schema 비교 (POE1 vs POE2)

| 필드 | POE1 (3.28) | POE2 (0.4) | 어댑터 조치 |
|---|---|---|---|
| `groups` | `Record<string, TreeGroup>` | `TreeGroup[]` (0-indexed) | **list → dict 변환 필요** (`groups[i]` → `"i": groups[i]`) |
| node `connections` | `in: string[]` + `out: string[]` | `connections: [{id, orbit}]` | **`out` 배열 합성 필요** (`connections.map(c => String(c.id))`) |
| `skillsPerOrbit` | `[1,6,16,16,40,72,72]` (7) | `[1,12,24,24,72,72,72,24,72,144]` (10) | 런타임 주입 (상수 하드코딩 금지) |
| `orbitRadii` | POE1 값 | `[0,82,162,335,493,662,846,251,1080,1322]` (10, **orbit 7=251 out-of-order**) | 런타임 주입 |
| orbit 2/3 슬롯 | 16 (비균등 45°/135° 보정) | 24 (균등 15°) | `nodeAngleDeg` 가 `slots===16` 분기 — POE2 24-slot 은 균등 `(idx/slots)*360` fallback 자동 처리 |
| `classes` | 7 (Scion 포함) | 8 (Scion 없음, Huntress/Druid 등) | `classStartIndex` 대신 `classesStart: ["className"]` 사용 |
| `classStartIndex` | 있음 | **없음** | `classesStart: string[]` 기반 별도 매핑 |
| `isMastery` | 있음 | **없음** (0 노드) | 렌더에서 생략 OK |
| `isAscendancyStart` | 있음 | 있음 (20 노드) | 호환 |
| `isNotable/isKeystone/isJewelSocket` | 있음 | 있음 (1122/33/12) | 호환 |

### POE2 신규 필드
- `classes[i].integerId` — 1,2,6,7,8,9,10,11 (불연속, Scion=0 없음, Shadow=6 생략)
- `classes[i].ascendancies[j].internalId` — `"Ranger1"`, `"Ranger3"` 등
- `assets / ddsCoords / connectionArt / nodeOverlay` — 스프라이트 관련 POE2 확장
- `jewelSlots` — POE2 전용
- `tree: "Default"` — tree 타입 식별자

### 클래스 시작 노드 ID (POE2, `classesStart` 기반)
POE1 과 **동일한 노드 ID 재사용** (Scion 58833 만 미사용):

| Node ID | POE1 Class | POE2 Class |
|---|---|---|
| 47175 | Marauder | Warrior |
| 50459 | Ranger   | Huntress |
| 50986 | Duelist  | Mercenary |
| 54447 | Witch    | Sorceress |
| 61525 | Templar  | Druid |
| 44683 | Shadow   | Monk |
| 58833 | Scion    | — (POE2 사용 안 함) |

→ POE2 에서 2 클래스가 같은 start node 공유. 어센던시로 분기.

---

## 3. 소비자 코드 어댑터 (구현 scope)

### 수정 필요 파일
| 파일 | 변경 | 예상 라인 |
|---|---|---|
| `src/utils/passiveTree.ts` | POE2 노드→POE1-shape 변환 함수 `normalizePoe2Tree()` 추가. 기존 함수 (`buildAdjacency`/`resolveNodePosition`/`shortestPath`) 재사용 | +70 |
| `src/utils/passiveTreeConstants.ts` | `POE2_CLASS_START_NODE_IDS` 추가. `POE1_CLASS_START_NODE_IDS` rename | +30 |
| `src/components/PassiveTreeCanvas.tsx` | `game?: "poe1"\|"poe2"` prop + 동적 `dataUrl` 선택 (`data.json` ↔ `tree_0_4.json`) | +40, -15 |
| `src/components/PassiveTreeView.tsx` | `game` prop 전파 (activeGame store 연결) | +5 |
| `src/utils/passiveTree.test.ts` | POE2 geometry 검증 3-5 케이스 추가 | +60 |
| `data/skilltree-export-poe2/README.md` | 데이터 소스/라이선스/업데이트 절차 | 신규 30줄 |

### 미변경 유지
- `passiveTreeRender.ts` — POE2 정규화 후 동일 구조 소비 (sprites/stats rendering)
- `passiveTreeSprites.ts` — POE2 스프라이트는 POE1 과 경로가 달라 추후 별도 작업 (D4 범위 밖)
- `passiveTreeTranslate.ts` — 번역은 POE1 전용 한국어 stat 템플릿. POE2 번역은 차후.

### 어댑터 의사 코드 (`normalizePoe2Tree`)

```typescript
export function normalizePoe2Tree(raw: Poe2RawTree): TreeData {
  // groups: list → dict (key = index as string)
  const groups: Record<string, TreeGroup> = {};
  raw.groups.forEach((g, i) => { groups[String(i)] = g; });

  // nodes: connections → in/out
  const nodes: Record<string, TreeNode> = {};
  for (const [id, n] of Object.entries(raw.nodes)) {
    const out = (n.connections || []).map(c => String(c.id));
    nodes[id] = { ...n, out, in: [] };  // in은 adjacency에서 파생 가능
  }

  return {
    nodes, groups,
    constants: raw.constants,
    min_x: raw.min_x, min_y: raw.min_y,
    max_x: raw.max_x, max_y: raw.max_y,
  };
}
```

### 클래스 선택 매핑

`classStartIndex` 부재 → classesStart 역인덱스:
```typescript
export const POE2_CLASS_START_NODE_IDS: Record<string, string> = {
  // classesStart 배열의 [POE1name, POE2name] 중 POE2 name만 사용
  Warrior:   "47175",
  Huntress:  "50459",
  Mercenary: "50986",
  Sorceress: "54447",
  Druid:     "61525",
  Monk:      "44683",
  // Witch/Ranger는 POE1 이름이 POE2 에도 그대로 존재 — classes[].name 참조
  Witch:     "54447",
  Ranger:    "50459",
};
```

---

## 4. 구현 순서 (D4 본 세션 또는 후속)

1. ✅ 데이터 소스 선정 + tree.json 다운로드 (완료)
2. ✅ Schema 분석 + 매핑 테이블 작성 (본 문서)
3. [ ] `data/skilltree-export-poe2/README.md` 작성 (출처/라이선스/업데이트)
4. [ ] `.gitignore` 검토 — tree_0_4.json 은 POE1 data.json 과 동일하게 커밋 (비용 = 1.8 MB, 업데이트 주기 = 리그 교체시)
5. [ ] `passiveTree.ts` 에 `normalizePoe2Tree` + 타입 분리
6. [ ] `passiveTreeConstants.ts` POE2 class start 추가
7. [ ] `PassiveTreeCanvas` `game` prop + 동적 dataUrl
8. [ ] `PassiveTreeView` activeGame 전파
9. [ ] 테스트 5 케이스 추가 (orbit 2 24-slot, class start, connections 변환, group 0-index, ascendancy start)
10. [ ] `npm run check` + 82→90+ 테스트 PASS
11. [ ] 인게임 Tauri 실 렌더 확인 (사용자 영역)

---

## 5. 리스크 / 미해결

- **Orbit 7 반경 251 out-of-order** — 내부 9 (1322) 와 외부 6 (846) 사이에 시각적 역전. tree.json 가 맞다면 UI 겹침 가능성. 렌더 후 시각 확인 필수
- **16-slot 규칙 부재** — POE1 orbit 2/3 이 16 슬롯일 때 45°/135°/225°/315° 보정 각도표 사용. POE2 는 24 슬롯 균등 분포라 기존 코드의 `if (slots === 16)` 분기가 POE2 에 닿지 않음 → **동작함** (fallthrough 균등). 단 명시적 주석 필요
- **스프라이트** — POE1 은 `data/skilltree-export/assets/*.{png,jpg}` 스프라이트시트. POE2 는 PoB 에 DDS (`*_BC7.dds.zst` 압축) 로 있음. 웹 렌더에 쓰려면 별도 변환 파이프라인 → **D4 범위 밖**
- **번역** — `passive_tree_translations.json` 은 POE1 전용. POE2 번역은 D4 범위 밖
- **리그 업데이트** — POE2 0.5 시 tree_0_5.json 재다운로드 스크립트 필요 → `scripts/refresh_poe2_tree.py` 추가 (후속)

---

## 6. 참조
- [PoB-PoE2 repo](https://github.com/PathOfBuildingCommunity/PathOfBuilding-PoE2)
- [POE1 Passive Tree JSON Wiki](https://www.poewiki.net/wiki/Passive_Skill_Tree_JSON) — 포맷 기본 명세
- `data/skilltree-export/README.md` — POE1 3.20+ 변경사항
- `src/utils/passiveTree.ts:1` — POE1 소비자 현재 구현
