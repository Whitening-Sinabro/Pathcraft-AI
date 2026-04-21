# Phase H — 코치 품질 (LLM Hallucination 근본 해결)

> **근본 원인: LLM 출력을 ground truth에 강제로 정렬하는 후처리 레이어가 없음.**
> 정적 데이터(GGPK 추출 + Wiki/poedb 3중 검증)는 정확하지만, LLM은 prompt allowlist를 "참고"만 할 뿐 준수하지 않음. 그 결과 gem 약칭(`Bleed Chance` ↔ `Chance to Bleed Support`), 유니크 이름 hallucination, 베이스 아이템 변형이 UI에 그대로 노출됨.

---

## 1. 현상 (사용자 피드백 기반)

- **보조 젬 몇 개는 맞고 몇 개는 안 맞음** — `links_progression.gems` 배열 내 hallucination
- **장비 진행도 안 맞음** — `gear_progression.item`, `key_items.name` 검증 없음
- 유사 증상 예상 영역: `skill_transitions.change`, `aura_utility_progression`, `passive_priority`, `map_mod_warnings.regex_filter` (mod 이름), `farming_strategy`

## 2. 현 파이프라인 상태 (코드 기반, 2026-04-21)

```
POB input → parse_pob (Rust) → buildData JSON
  → SYSTEM_PROMPT 주입 (valid_gems 270개) + coachInput
  → Claude API (coach_build)
  → raw coachResult JSON
  → coach_validator.py  (gem warning만, 자동 교정 없음. gear는 스키마만)
  → UI 직행 (hallucination 통과)
```

**문제점:**
- `coach_validator.py:194-223` — gem warning만 출력, 자동 정식화 부재
- `REQUIRED_FIELDS` 에 `gear_progression` 포함되나 스키마/타입만 검증, **item 이름 검증 없음**
- `_validation_warnings` 필드가 존재하지만 **UI에 노출되지 않음** → 사용자가 경고 존재 여부 모름

## 3. 해결 아키텍처

**Normalizer 파이프라인 도입 (hard constraint).** prompt engineering은 보완(soft)이고, normalizer가 주 제약(hard)이어야 allowlist 100% 준수 가능.

```
coachResult raw →
  normalizer:
    1. gem 이름 (links_progression.gems, main_skill, skill_transitions.change)
       → valid_gems.json fuzzy match (cutoff 0.85)
       → alias 맵 보완
       → canonical 교체
    2. 유니크 이름 (gear_progression.item, key_items.name)
       → unique_base_mapping.json match
       → alias 맵 보완
    3. 베이스 이름 (gear_progression.item 중 레어/베이스)
       → BaseItemTypes (GGPK 추출) match
    4. 매칭 실패 시 → _validation_warnings 에 추가 + 해당 필드 UI 경고 배지 표시
  → UI
```

**원칙:**
- Normalizer는 **corrective**: 가능한 한 자동 교정 (사용자 개입 없이)
- 불확실한 교정(cutoff 임계 미달)은 **수정하지 않고 경고만** — false positive 방지
- 원본 LLM 값은 별도 필드 보존 (디버깅 + 대안 제시)

## 4. 단계별 실행 계획

### H1. `_validation_warnings` UI 노출 (가장 빠른 가시화)
- 오버레이 + 메인 창 상단에 경고 배지 ("LLM 출력 이상 N건" + 클릭 시 세부)
- 현재 validator가 뱉는 warning을 그대로 표시
- **교정 없음**, 사용자에게 "이 필드는 믿지 마세요" 신호
- 작업량: 0.5 세션
- 파일: `src/components/ValidationWarningsBanner.tsx` (신규), `App.tsx`, `OverlayApp.tsx`

### H2. Gem Normalizer
- `python/coach_normalizer.py` 신규
- `data/valid_gems.json` 로더 + fuzzy match (`difflib.get_close_matches`, cutoff 0.85)
- 명시적 alias 맵 (`data/gem_aliases.json` 신규):
  ```json
  {
    "bleed chance": "Chance to Bleed Support",
    "ele focus": "Elemental Focus Support",
    "melee phys": "Melee Physical Damage Support",
    "added fire": "Added Fire Damage Support",
    "added cold": "Added Cold Damage Support",
    "added lightning": "Added Lightning Damage Support",
    "cwdt": "Cast when Damage Taken Support",
    "cwc": "Cast while Channelling Support",
    "gmp": "Greater Multiple Projectiles Support",
    "lmp": "Lesser Multiple Projectiles Support",
    "inc aoe": "Increased Area of Effect Support",
    "conc effect": "Concentrated Effect Support"
  }
  ```
- 대상 필드: `leveling_skills.recommended.links_progression[].gems`, `leveling_skills.options[].links_progression[].gems`, `leveling_skills.recommended.name`, `leveling_skills.options[].name`, `skill_transitions[].change` (split + normalize)
- build_coach pipeline에서 validator 직전 삽입
- 작업량: 0.5~1 세션
- 테스트: `python/tests/test_coach_normalizer.py` (20+ 케이스)

### H3. Gear Normalizer + Validator
- `python/gear_normalizer.py` 신규
- `data/unique_base_mapping.json` (642 유니크) + GGPK BaseItemTypes 로더
- 대상 필드: `gear_progression[].phases[].item`, `key_items[].name`, `key_items[].alternatives[]`
- 슬롯 validation: `gear_progression[].slot` + `key_items[].slot` 이 POE 정식 슬롯명인지 (Helmet/Body Armour/Gloves/Boots/Weapon/Offhand/Belt/Ring/Amulet/Flask/Jewel/Abyss Jewel)
- Influence/변종 처리: `Kaom's Heart` vs `Kaom's Heart (Legacy)` 등
- 작업량: 1 세션
- 테스트: `python/tests/test_gear_normalizer.py` (20+ 케이스)

### H4. SYSTEM_PROMPT 정확성 강화
- `python/build_coach.py` SYSTEM_PROMPT 수정:
  - "정식 이름만 사용, 약칭/변형 금지"
  - "존재 확실하지 않은 아이템은 생성 금지, 대체는 null 또는 '미정'"
  - "gear_progression에는 POB 기반 확정된 슬롯만, 추측성 유니크 금지" (또는 "추측이면 `confidence: low` 표시")
- 작업량: 0.2 세션 (프롬프트 작성 + A/B 테스트)

### H5. Valid 데이터 감사 + 최신화
- `data/valid_gems.json` 현재 Mirage(3.28) 기준인지 확인
- `data/unique_base_mapping.json` 최신 유니크 커버리지 확인 (642 → 현재 리그 추가분?)
- `scripts/refresh_*` 자동화 존재 파일 여부 확인
- POB `src/Data/Skills/*.lua` 기준 정합성 (이미 일부 완료 — `python/extract_gem_weapon_reqs.py`)
- 작업량: 0.5 세션

---

## 5. 비용/시간 추정

| 단계 | 작업량 | 우선순위 | 비용 영향 |
|------|-------|---------|----------|
| H1 | 0.5 세션 | 즉시 | UI 변경만, 추론 비용 0 |
| H2 | 0.5~1 | 다음 | Python 후처리, API 비용 0 |
| H3 | 1 | 다음 | 동일 |
| H4 | 0.2 | 병렬 | 프롬프트 길이 소폭 증가 (캐싱으로 상쇄) |
| H5 | 0.5 | 낮음 | 데이터 작업만 |

**총 1.5~2.5 세션.** H1 먼저 → H2+H3 병렬 → H4/H5 마무리 순서.

---

## 6. 원칙 / 의사결정 가이드

1. **Normalizer는 모든 LLM 출력 필드에 적용 가능한 단일 구조**. gem/gear/mod/divcard 등 모두 동일 패턴 (lookup + fuzzy + alias + fallback)
2. **Prompt engineering 만으로는 100% 해결 불가** — hard constraint는 코드 레이어에만 존재
3. **False positive 경계** — normalizer가 사용자 의도를 바꾸지 않도록 cutoff 보수적으로 (0.85+)
4. **원본 보존** — 교정된 필드와 원본 필드 모두 JSON에 남겨 디버깅/수동 검토 가능
5. **회귀 방지 테스트 필수** — 각 normalizer 마다 골든 케이스 20건 이상

---

## 7. 검증 사례 수집 (사용자 피드백 기반)

> 다음 세션 H2/H3 alias 맵 시드용. 사용자가 "틀렸다"고 본 사례를 누적.

### Gem (H2 대상)
- (pending) 사용자가 구체 예시 제공 시 여기 누적

### Gear (H3 대상)
- (pending) 사용자가 구체 예시 제공 시 여기 누적

---

## 8. 관련 파일 인덱스

| 경로 | 역할 |
|------|------|
| `python/coach_validator.py` | 현 validator (스키마 + gem warning) — H2/H3 normalizer로 확장 |
| `python/build_coach.py` | SYSTEM_PROMPT + API 호출 — H4 프롬프트 수정 |
| `data/valid_gems.json` | 270 support gem 화이트리스트 |
| `data/unique_base_mapping.json` | 642 유니크 |
| `data/game_data/BaseItemTypes.datc64` (추출됨) | 모든 base 아이템 |
| `src/types.ts` | CoachResult 스키마 |
| `src/components/` | H1 경고 배지 위치 |

---

## 9. 비-목표 (이 Phase에서 다루지 않음)

- LLM 재요청(L3): 비용 2배, latency 문제. Normalizer로 충분하면 불필요
- 전체 코치 JSON 스키마 재설계: 현재 스키마 유지, 값만 정식화
- 멀티-언어: 한국어 alias는 향후 과제
- 실시간 피드백 루프(사용자가 UI에서 수정 → 데이터셋 학습): 별도 큰 기능
