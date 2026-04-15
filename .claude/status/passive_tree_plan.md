# 패시브 트리 뷰어 플랜 (옵션 D-완전)

> 결정 기준: Canvas2D + 통합 ascendancy + Phase 1→3 순차

## 데이터 실측 (data.json)

- nodes: 3338 / groups: 776
- constants:
  - `orbitRadii`: [0, 82, 162, 335, 493, 662, 846]
  - `skillsPerOrbit`: [1, 6, 16, 16, 40, 72, 72]
  - `PSSCentreInnerRadius`: 130
- node 필드: `skill, name, icon, stats[], group, orbit, orbitIndex, in[], out[]`
- group 필드: `x, y, orbits[], background?{image,isHalfImage,offsetX,offsetY}, nodes[]`
- 좌표 범위: `min_x, min_y, max_x, max_y` 제공
- 이미지: spritesheet (`sprites` 키) — `imageZoomLevels` 별 다른 해상도

## 좌표 변환 공식 (3.17 이후)

```
node.x = group.x + orbitRadii[node.orbit] * sin(angle)
node.y = group.y - orbitRadii[node.orbit] * cos(angle)

# orbit별 각도 테이블
orbit 0: angle = 0
orbit 1: angle = (orbitIndex / 6) * 360°
orbit 2: angle = [0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330][orbitIndex]  # 16각
orbit 3: 동일 16각
orbit 4: angle = (orbitIndex / 40) * 360°
orbit 5,6: angle = (orbitIndex / 72) * 360°
```

## Phase 분리 (PASS 조건 포함)

### Phase 1: 정적 트리 표시 (8-12h)

**파일**:
- 신규: `src/utils/passiveTree.ts` — 좌표 변환 + 데이터 로더
- 신규: `src/utils/passiveTree.test.ts` — 좌표 변환 단위 테스트
- 수정: `src/components/PassiveTreeView.tsx` — iframe 제거, Canvas로 리라이트
- 신규: `src/components/PassiveTreeCanvas.tsx` — 렌더 컴포넌트 (분리)

**의존성 결정**:
- `vitest` 추가 필요 (devDependency) — 사용자 승인 대기
- 그 외 zero-dep (Canvas2D 네이티브)

**PASS 조건**:
1. `pnpm test` — 좌표 변환 테스트 통과 (orbit 0~6 각각 1개씩, 알려진 노드 좌표 일치)
2. `pnpm build` — 타입 에러 0
3. 수동 검증: `pnpm dev` 후 트리 탭 진입 → 3338 노드 모두 화면에 표시 + pan/zoom 동작
4. 그룹 background 스프라이트 매핑 (PSGroupBackground1/2/3)
5. 노드 frame: notable / keystone / mastery / jewel 분기 표시
6. 60fps 유지 (3338 노드 + 연결선)

### Phase 2: PoB allocated 노드 하이라이트 (4-6h)

**입력**: `App.tsx`의 `passive_tree_url` (포맷: `https://www.pathofexile.com/passive-skill-tree/AAAA...`)

**파일**:
- 신규: `src/utils/passiveTreeUrl.ts` — base64 URL 디코더 (POE 트리 URL 스펙)
- 신규: `src/utils/passiveTreeUrl.test.ts` — 알려진 URL → 노드 ID 셋 매칭
- 수정: `PassiveTreeCanvas.tsx` — `allocatedNodes: Set<number>` prop 추가, 하이라이트 렌더

**PASS 조건**:
1. 알려진 빌드 URL 디코드 결과가 PoB allocated nodes와 일치
2. Continue 단계 전환 시 하이라이트 갱신
3. ascendancy 노드도 하이라이트

### Phase 3: 한국어 stat 툴팁 (4-6h)

**파일**:
- 신규: `src/utils/passiveStatTranslate.ts` — 영문 stat → 한국어 매핑
- 수정: `PassiveTreeCanvas.tsx` — 호버 좌표 → 노드 detection → 툴팁 렌더

**번역 소스**:
- 1순위: `data/merged_translations.json` (확인 필요)
- 2순위: `data/poe_translations.json`
- 미매칭 stat은 영문 fallback + 로그 경고

**PASS 조건**:
1. 노드 80% 이상 한국어 stat 매칭 (커버리지 측정 스크립트)
2. 호버 → 50ms 이내 툴팁 표시
3. 미매칭 stat 영문 fallback 정상 동작

## 위험 / 미해결

- **번역 매핑 형식 미확인** — Phase 3 진입 전 `merged_translations.json` 구조 샘플링 필요
- **POE 트리 URL 인코딩 스펙** — Phase 2 시작 시 PoB 소스 코드 참조 (Lua), 또는 OSS pob-frontend 차용
- **이미지 sprite atlas 매핑** — `data.json:sprites` 구조 미확인, Phase 1에서 샘플링

## 추정 총합

- 의존성 추가 승인: 5분
- Phase 1: 8-12h
- Phase 2: 4-6h
- Phase 3: 4-6h
- **합계: 16-24h**

## 마일스톤

각 Phase 완료 시 별도 커밋 + 인게임 검증 (Continue 빌드 한 개로 트리 표시 → 하이라이트 → 한국어 툴팁 순서)
