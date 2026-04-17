# 리그 교체 시 데이터 재수집 체크리스트

POE1 리그가 바뀔 때마다 아래 순서로 refresh 스크립트 실행.
각 스크립트는 `data/` 아래 JSON을 갱신하고 `_meta.collected_at`을 업데이트한다.

## 사전 확인

1. 새 리그명 확인 (poe.ninja URL로 검증):
   - SC: `https://poe.ninja/poe1/economy/<league-slug>/` 접근 가능 여부
   - HC: `Hardcore <League Name>` (예: `Hardcore Mirage`)
2. `python/poe_ninja_api.py`에 하드코딩된 기본 리그명 있는지 확인 (CLI 파라미터로 override 가능하면 수정 불필요)

## 실행 순서

### 1. `scripts/refresh_unique_base_mapping.py`

유니크 → 베이스 아이템 매핑 자동 재수집 (poewiki Cargo API).

```bash
python scripts/refresh_unique_base_mapping.py --dry-run   # 미리보기
python scripts/refresh_unique_base_mapping.py             # 실제 기록
```

**출력**: `data/unique_base_mapping.json`
**재수집 주기**: 새 리그 시작 직후 (신규/변경 유니크 반영)
**의존**: Wiki 편집 반영에 수일 소요. 리그 시작 후 3-5일 뒤 재실행 권장

### 2. `scripts/refresh_hc_divcard_tiers.py`

HCSSF 디비카 T1/T2 override 자동 재수집 (poe.ninja HC 경제).

```bash
python scripts/refresh_hc_divcard_tiers.py --league "Hardcore Mirage"
```

**출력**: `data/hc_divcard_tiers.json`
**재수집 주기**: 리그 시작 2-3주 후 (경제 안정화 필요). 중반 1회 추가 권장
**리그 교체 시**: `--league` 값을 새 HC 리그명으로 교체
**스키마**: `{_meta, t1_override, t2_override}` — 백분위 컷 (top 5% / next 10%)

### 3. `python/extract_gem_damage_types.py` (POE 패치 시)

Gem → damage axis(attack/caster/dot/minion) 매핑. POB Community `src/Data/Skills/*.lua`의 `skillTypes` 실측 기반.

```bash
python python/extract_gem_damage_types.py              # live fetch + cache 갱신
python python/extract_gem_damage_types.py --cache-only # 오프라인 (기존 캐시만)
```

**출력**: `data/gem_damage_types.json` (~741 entries × 4 axis bool)
**재수집 주기**: POE 패치 시 (신규 젬 추가 / Transfigured 변형 / SkillType 리네임)
**소비처**: `python/damage_type_extractor.py` → L7 accessory_proxy 분기
**캐시 위치**: `data/pob_skills_cache/*.lua` (Phase B `extract_gem_weapon_reqs.py`와 공유)

### 4. `scripts/extract_accessory_mod_tiers.py` (NeverSink 업데이트 시)

악세서리(amu/ring/belt) × damage axis 별 mod 리스트. NeverSink 1-REGULAR.filter 라인 1238-1501 파싱.

```bash
python scripts/extract_accessory_mod_tiers.py
```

**출력**: `data/accessory_mod_tiers.json` (3 slots × 4-5 axis, ~681 mods)
**재수집 주기**: NeverSink 필터 메이저 업데이트 시 (`_analysis/neversink_*` 갱신 후)
**짝 파일**: `scripts/extract_defense_mod_tiers.py` (Phase D 방어 mod)

### 5. `scripts/validate_divcard_mapping.py`

유니크 → 디비카 매핑 Wiki 대조 검증 (regression).

```bash
python scripts/validate_divcard_mapping.py
```

**출력**: 콘솔 리포트 (mismatch 있으면 비0 exit)
**실행 시점**: refresh_unique_base_mapping 이후
**용도**: `data/divcard_mapping.json` 수동 엔트리가 Wiki와 일치하는지 확인

## 검증 체크리스트

갱신 후:

- [ ] `python -m pytest python/tests/ -q` 전체 PASS
- [ ] `git diff data/` 확인 — 의도치 않은 대량 삭제 없는지
- [ ] 샘플 빌드로 β 오버레이 생성 후 필터 스모크 (`python -m python.filter_generator ...`)
- [ ] 인게임에서 신규 유니크/카드가 반영됐는지 육안 확인

## 알려진 제한

- **poe.ninja 집계 지연**: 리그 시작 첫 주는 카드 가격이 매우 불안정 → HC override refresh는 2주 이후 권장
- **Wiki 업데이트 지연**: GGG 릴리스 직후 며칠은 신규 유니크가 Wiki에 없을 수 있음
- **수동 매핑**: `data/divcard_mapping.json`의 `unique_to_cards`는 일부 수동 엔트리 보존. 자동화 불가 시 validate 스크립트로 drift만 감지
