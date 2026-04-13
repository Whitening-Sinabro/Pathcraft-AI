# Continue 체인 아키텍처 (β)

> Aurora Glow 단일 매칭 → Wreckers식 Continue 캐스케이드로 전면 전환.

## 원칙

1. **레이어 독립성**: 각 레이어는 단일 관심사(색/보더/아이콘/사운드 중 일부)만 수정
2. **순서 의존 명시**: 레이어 순서를 상수로 고정, 변경 시 반드시 문서 갱신
3. **Continue 기본**: 모든 레이어는 `Continue`로 종료 (마지막 Show 제외)
4. **디버그 주석**: 각 블록 주석에 `[layer:N]` 포함 → 최종 스타일 추적 가능
5. **SSF 철학**: 커런시/젬/플라스크/프래그먼트/디비카 절대 숨기지 않음

## 레이어 순서 (위 → 아래 = 먼저 평가 → 나중 평가)

| # | 이름 | 역할 | Continue |
|---|------|------|----------|
| 0 | HARD_HIDE | 절대 숨김 (Scroll Fragment 등) | × (정지) |
| 1 | CATCH_ALL | 오렌지 미분류 안전망 | ✓ |
| 2 | DEFAULT_RARITY | Normal/Magic/Rare 기본 색 | ✓ |
| 3 | SOCKET_BORDER | Chromatic RGB / Jeweller 6S 핑크 보더 | ✓ |
| 5 | CORRUPT_BORDER | 부패/타락/미러 빨강 보더 | ✓ |
| 6 | T1_BORDER | ilvl≥86 + 크래프팅 베이스 → 레어리티색 보더 + Star | ✓ |
| 7 | BUILD_TARGET | POB 빌드 타겟 아이템 강조 | ✓ |
| 8 | CATEGORY_SHOW | 커런시/젬/플라스크/맵/디비카/유니크 (최종 스타일) | × |
| 9 | PROGRESSIVE_HIDE | AL 기반 단계적 Hide (Normal AL≥14, Magic AL≥24 등) | ✓ (재Show 허용) |
|10 | RE_SHOW | Jewel/Flask/Tincture/Cluster 등 예외 Show | × |
|11 | ENDGAME_RARE | 엔드게임 레어 필터 | × |
|12 | REST_EX | 미분류 최종 안전망 | × |

**L4 SPECIAL_BASE 폐기 (2026-04-13)**: Wreckers의 "특수 베이스 오렌지 복원"은 PathcraftAI에서 불필요.
L1 오렌지가 이미 catch-all이고 L2에서 레어리티 색 씌운 후 L8 CATEGORY_SHOW가 카테고리별 최종 스타일 칠함.
특수 베이스(Abyss Jewel, Cluster Jewel 등)는 L8에서 각 카테고리로 직접 처리. 상수 `LAYER_SPECIAL_BASE=4`는 예약만 유지 (추후 필요 시 재활성).

## 블록 빌더 API (sections_continue.py)

```python
def make_layer_block(
    layer: int,           # 레이어 번호 (0~12)
    comment: str,         # 블록 주석 (layer 태그 자동 추가)
    conditions: list[str],
    style: dict,          # {text, border, bg, font, sound, effect, icon}
    action: str = "Show", # Show | Hide
    continue_: bool = True,
) -> str
```

**style 부분만 설정**: None인 필드는 출력 안 함 (이전 레이어 값 유지 = Continue 캐스케이드 핵심).

예) T1 보더 레이어는 `{"border": "255 255 0", "icon": "0 Yellow Star"}`만 설정. 텍스트 색/폰트는 이전 레이어 유지.

## 엄격도 재설계

기존: 주석 패턴 매칭으로 블록 제거/Hide 전환.
신규: 각 레이어별 `min_strictness` 속성 + **PROGRESSIVE_HIDE** 레이어에서 AL + Strictness 복합 조건.

```python
LAYERS_BY_STRICTNESS = {
    0: 전체 레이어,
    1: [8, 10, 11, ...] + AL 기반 Hide 강화,
    2: ..., 3: ..., 4: ...
}
```

## 디버그 지원

블록 주석 포맷:
```
Show # PathcraftAI [L3|socket] RGB 크로매틱 레시피
```
- `L3` = layer 3 (SOCKET_BORDER)
- `socket` = 카테고리 태그
- 본문 = 사람이 읽는 설명

인게임에서 이상한 스타일 보면 주석으로 어느 레이어가 영향 줬는지 추적.

## 마이그레이션 전략 (브리지 모델)

**핵심 원칙: 구 Aurora 경로를 β-5 완료까지 보존한다.** 중간 단계에서도 항상 동작하는 필터가 나온다.

### 공존 구조

```
filter_generator.py
  ├─ generate_overlay(arch="aurora")   ← 기존 경로 (default, β-5까지 보존)
  └─ generate_overlay(arch="continue") ← 신규 β 경로 (단계적 채움)

CLI: --arch aurora|continue (기본 aurora)
```

- 각 β-N 단계에서 `arch=continue` 출력이 점진적으로 풍부해짐
- `arch=aurora`는 손대지 않음 → 기존 인게임 검증 자산 보존
- β-5 완료 + 인게임 확인 후 `arch=aurora` 경로 삭제

### 단계별 산출물

| 단계 | continue 경로 출력 가능 여부 |
|------|------------------------------|
| β-0 | 빈 문자열 (빌더만 있음) |
| β-1 | Catch-All + Default Display만 |
| β-2 | + RGB/부패/T1 보더 |
| β-3 | + AL 기반 Hide |
| β-4 | + 커런시/맵/디비카 → **aurora 기능 동등** |
| β-5 | + 빌드 오버레이 → aurora 대체 준비 완료 |

### 파일별 변경

| 파일 | β-0 | β-1 | β-2 | β-3 | β-4 | β-5 |
|------|-----|-----|-----|-----|-----|-----|
| `sections_continue.py` | 생성 | 확장 | 확장 | 확장 | 확장 | 확장 |
| `data/t1_craft_bases.json` | 생성 | — | 소비 | — | — | — |
| `filter_generator.py` | — | `--arch` | — | — | — | aurora 제거 |
| `sections_*.py` (구 4개) | — | — | — | — | — | 삭제 |
| `pathcraft_sections.py` facade | — | — | — | — | — | 삭제 or 재지정 |
| `filter_merge.py` | — | — | — | — | — | Sanavi 주입 로직 제거 |

## 기존 시스템과의 관계

### Sanavi 베이스 필터

**결정: β = standalone 전면 필터.** Sanavi 오버레이 주입 방식 폐기.
- 이유: Continue 체인은 전체 필터를 한 덩어리로 관리해야 레이어 순서 보장
- 영향: `filter_merge.apply_overlay_to_file` → β-5에서 제거
- 임시: β-0~β-4 동안 aurora 경로는 계속 Sanavi 주입 방식 유지

### 팔레트(`pathcraft_palette.py`)

**결정: 팔레트 유지, LayerStyle 팩토리로 연결.**
- `sections_continue.style_from_palette(category, tier, **overrides) -> LayerStyle` 헬퍼 제공
- Aurora 색 자산 보존. 새 레이어에서도 기존 카테고리×티어 매핑 재사용
- 팔레트 자체는 "색/상수 데이터"로 계속 존재, `sections_*.py` 섹션 모듈만 삭제됨

### `apply_strictness()` (주석 패턴 매칭)

**결정: β-3에서 제거.**
- 대체: `sections_continue.apply_layer_strictness(filter_text, level) -> str`
  - 레이어 태그 `[L{n}|{cat}]` 기반 블록 제거/Hide 전환
  - AL + StackSize 복합 조건도 Hide 블록으로 직접 생성 (Wreckers 방식)
- 이유: 현재 주석 패턴 매칭은 Aurora 전용 주석 컨벤션. β 주석 포맷과 다름

## 성능

POE 엔진은 각 아이템마다 매칭되는 Continue 블록을 전부 평가. Wreckers 2,460줄 기준 문제 없음. PathcraftAI β 예상 2,000~3,000줄 → OK.

## 리스크

- **디버그 어려움**: L0~L12 중 어느 레이어가 최종 스타일을 결정했는지 불명확 → 주석 태그로 완화
- **순서 변경 파급**: 레이어 순서 변경 시 전체 재검증 필요 → 순서 고정, 변경 = 메이저 버전
- **인게임 검증 초기화**: Aurora Glow 2026-04-12 피드백 반영 분량 재검증 필요 → 검증 체크리스트 사전 준비
