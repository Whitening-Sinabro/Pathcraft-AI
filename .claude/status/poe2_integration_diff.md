# POE2 통합 Diff 초안

> 2026-04-22 세션. 6 에이전트 리서치 기반 + GGPK 마이닝 대기 중.
> 상위 백로그: [poe2_integration_backlog.md](poe2_integration_backlog.md)
> 자매 문서: [project_next_session_poe2 메모리](../../../../Users/User/.claude/projects/D--Pathcraft-AI/memory/project_next_session_poe2.md)

---

## 0. Claim 스코프 (audit-all 재작성 — 2026-04-22)

아래는 "완전 가동 / 검증 완료" 같은 단정 대신 실측 증거로 다시 쓴 scope-bounded claim.

| # | 실측 범위 | 증거 |
|---|-----------|------|
| 1 | POE2 **코치 경로** L1 (SYSTEM_PROMPT_POE2 5690자 + valid_gems_poe2 화이트리스트 주입) 가동 | CLI smoke 2차 로그 `POE2 Support 젬 화이트리스트 주입: 600개` / `POE2 Active 화이트리스트 주입: 477개 (Spear 21)` |
| 2 | L2 strict drop 경로 **구현 + 단위 테스트**. **실 LLM 응답에서 drop 발생 케이스는 미검증** (CLI smoke 2차 `drop=0`, L2/L3 둘 다 unfired) | `tests/test_coach_poe2_branch.py::test_list_drops_invalid_poe2_gem PASSED` |
| 3 | L3 retry 경로 **구현 + 단위 테스트**. **실 LLM 응답에서 retry 발동 케이스는 미검증** (L2 drop=0 이므로 Gate 조건 `first_attempt_dropped` 빈 리스트) | `tests/test_build_coach_retry.py` (POE1 기반 기존 5건). POE2 발동 케이스 미수집 |
| 4 | Spear 스킬 21개 GGPK ActiveSkills.json `WeaponRequirements=25` bitmask 실측 일치 | `python -c "load valid_gems_poe2.json; spear=21"` |
| 5 | drift 2건 (Mods +24B / SkillGems +32B) **byte pattern 해석 후 override schema 작성**. **override 적용 후 Mods JSON 재변환은 미실행** (backlog) | `data/schema/schema_poe2_override.json` + `scripts/drift_reverse_poe2.py` |
| 6 | frontend `game` invoke 인자 전달 — **코치 경로 (parse_pob / coach_build / syndicate_recommend / generate_filter_multi / analyze_syndicate_image / collect_patch_notes) 6 invoke site 확인** | `grep "invoke.*game" src/` |
| 7 | `game_data_provider.py` game 분기 (POE1 leak 차단) — 실측: POE2 `gems=1103`, POE1 `gems=840` 분리 로드 | `python -c "GameData(game='poe2')._ensure_loaded()"` |
| 8 | VerbalBuildInput + analyzeVerbalBuild 경로 **구현 + tsc 통과**. **UI 실 클릭 flow end-to-end 검증 미실행** (스크린샷 / 사용자 interaction 없음) | `npx tsc --noEmit` exit=0 |

**의도적 미수행 (scope 외)**:
- Mods JSON 변환 (override 적용 후 재추출) — drift 역추적은 역추적 단계만, 적용은 후속
- D3 base_items_poe2.json / uniques_poe2.json 생성
- D4 passive_tree_poe2.json
- D5 POE2 필터 (NeverSink import 포함)
- POE2 GameData의 `is_support` 판별 (POE2 SkillGems 는 `IsSupport` 필드 없음 — `GemType` 기반 판별 추후)
- POE2 QuestRewards 구조 차이 분석 (POE1 `Characters` / `Reward` 필드 호환성)

---

## 1. 리서치 요약 (6 에이전트)

| # | 주제 | 점수 | 핵심 |
|---|------|------|------|
| 1 | POE2 0.4 전체 상태 | 92/100 | 패치 0.4.0d / 리그 Fate of the Vaal / 8 클래스 / Druid·Talisman 추가 |
| 2 | 시스템·메커니즘 | 92/100 | Spirit 100, 젬 소켓 2→5, Bleed 15%×5s·이동 2x, Ascendancy 8 pts, Deflection 40% less |
| 3 | 아이템·크래프팅 | 95/100 | 무기 14종(Agent 5는 18), Charms 슬롯, 크래프트 벤치 제거 → Omens+Essences+Runes/Soul Cores |
| 4 | 클래스·어센던시·메타 | 91/100 | Deadeye·Pathfinder(Ranger 2개만), Twister=Amazon(Huntress) 메타 정석 |
| 5 | poe2db 데이터마인 | 92/100 | Twister/Whirling Slash/Whirlwind Lance/Rake/Spear of Solaris **전부 Spears 전용** |
| 6 | 커뮤니티 컨센서스 | 85/100 | **Deadeye Bleed Twister = 0.4 커뮤니티 레퍼런스 부재**. Bleed→Ritualist, Twister→Amazon |

---

## 2. 확정 Fact — POE2 시스템 (POE1 대비)

### 2.1 젬 시스템 (근본 변경)
- 젬은 기어 소켓이 아닌 **캐릭터 스킬 슬롯**에 직접 부착
- 스킬당 support 소켓 **2→3→4→5** (Lesser/Greater/Perfect Jeweller's Orb)
- **Support 젬은 캐릭터당 1회만** (동일 support 를 여러 스킬에 중복 불가)
- 3종 Uncut: Skill / Support / Spirit
- **Lineage Supports** 58개 (0.4 신규 엔드게임 tier, upstream drop)

### 2.2 Spirit 시스템 (POE1 마나 예약 대체)
- 기본 100, 가슴 갑옷 implicit +50, Sceptres / Solar Amulet / quest bosses 로 추가
- Heralds / Meta gems / Persistent buffs / Minions 소비

### 2.3 Meta gems (0.3/0.4)
- Cast on Freeze/Shock/Ignite → **Cast on Elemental Ailment** 통합 (100 Spirit, Lv14)
- Energy 시스템 (trigger 당 누적, 스킬 기본 캐스트타임 = 최대 Energy)

### 2.4 Bleed 스케일링 (빌드 코치 직결)
- `bleed_dps = hit_physical_damage × 0.15`, duration 5s
- 이동 / Aggravated 시 **2x** (cap 미문서화)
- **Magnitude of Damaging Ailments** (Deterioration 등) 가 직접 스케일 축
- "increased physical damage" 는 hit 1회만 적용 (double-dip 방지)

### 2.5 Charges 핵심 변화
- Frenzy / Power / Endurance 보유 중 **passive 보너스 없음** — consume 시만 스킬 강화
- POE1 의 "프렌지 차지 = 4% 공속 증가" 타입 효과 모두 제거

### 2.6 무기 스왑
- 2 세트 instant auto-swap (0.3+)
- Book of Specialization 로 set-specific passive points 획득
- global passives = 양 세트 공유, set-only passives = 세트 전용

### 2.7 어센던시 (8 포인트)
- Trial of Sekhemas (Sanctum 형) + Trial of Chaos (Ultimatum 형) 2 경로
- 첫 어센 Act 2 끝, 마지막 2pt Lv75+ Sekhemas OR Lv65+ Chaos w/ 3 Fates

### 2.8 엔드게임
- Waystone T1~T15 (구 맵). Precursor Tablets (구 Sextants)
- Atlas Passive Tree (맵핑 특화)
- Citadels 3종 (Copper / Iron / Stone) → Arbiter 조각
- Pinnacle 6: Arbiter, Xesht, Olroth, Trialmaster, King in the Mists, Zarokh

### 2.9 방어 0.3 신규 Deflection
- AoE + projectile + ailment 에 **40% less damage** 적용 (Evasion 과 달리 비직격 커버)
- 기존 Armour / Evasion / ES 위에 layering

### 2.10 0.4 ailment 변화
- Shock non-player: 4s → **8s**
- Chill non-player: 2s → **8s**, <30% magnitude 무효 (5% 였음)
- Light stun <15% magnitude → 0

---

## 3. 클래스 & 어센던시 (0.4 실 출시 확정)

| 클래스 | 주속성 | 주무기 | 어센던시 (0.4 출시) |
|--------|--------|--------|---------------------|
| Warrior | STR | 2H Mace | Titan, Warbringer, Smith of Kitava |
| Monk | DEX/INT | Quarterstaff | Invoker, Acolyte of Chayula |
| Ranger | DEX | Bow | **Deadeye, Pathfinder** (3번째 미출시) |
| Mercenary | STR/DEX | Crossbow | Witchhunter, Gemling Legionnaire, Tactician |
| Sorceress | INT | Wand/Staff/Sceptre | Stormweaver, Chronomancer, Disciple of Varashta |
| Witch | INT | Wand/Staff/Sceptre | Infernalist, Blood Mage, Lich, **Abyssal Lich (0.4 신규)** |
| Huntress (0.2) | DEX | Spear+Buckler | Amazon, Ritualist |
| Druid (0.4) | STR/INT | Quarterstaff/Maul | Shaman, Oracle |

---

## 4. Spear 스킬 — 무기 하드 제한 (코치 hallucination anchor)

| 스킬 ID | 무기 | 태그 |
|---------|------|------|
| `twister` | Spears | Attack, AoE, Projectile, Duration, Barrageable, **Wind** |
| `whirling_slash` | Spears | Attack, AoE, Melee, Strike, Staged, Wind |
| `whirlwind_lance` | Spears | Attack, AoE, Projectile, Duration, Barrageable, RangedAttack, Wind |
| `rake` | Spears | AoE, Melee, Strike, Physical |
| `spear_of_solaris` | Spears | Attack, AoE, Projectile, Fire, RangedAttack |

Twister 기본: 80%→232% dmg eff (Lv1→20), 0.5m 반경, 3s 지속, 0.66s per-target 쿨다운

---

## 5. 사용자 빌드 "Deadeye Bleed Twister" — 0.4 성립 판정

### 5.1 기계적 성립
- ✅ Deadeye (Ranger) 가 Spear 장착 가능 (무기는 stat req 만, 클래스 락 없음)
- ✅ Twister 는 Projectile 태그 → Deadeye 의 Far Shot / Endless Munitions / Called Shots 적용
- ✅ Bleed 는 phys 스케일, Twister 는 attack 이므로 이론상 bleed proc 가능
- ⚠️ Deadeye 어센던시 노드에 Bleed 직접 지원 없음 (crit/projectile 중심)

### 5.2 커뮤니티 레퍼런스
- ❌ **0.4 Deadeye Bleed Twister 가이드 존재 안 함** (에이전트 6 확인)
- 📌 Bleed vehicle = **Ritualist (Huntress)** — Rake + Disengage + Blood Hunt
- 📌 Twister vehicle = **Amazon (Huntress)** 또는 **Gemling (Mercenary)** — Ele 변환
- 📌 0.3 의 Whirling Slash Twister Deadeye 가이드는 **Elemental (Cold/Lightning)** 기반
- 📌 0.4 Twister 버그픽스 너프 (50% ele 변환 스택 → 일관 50%) 로 전반 약화

### 5.3 대안 방향
| 옵션 | 클래스·어센 | 스킬 | 데미지 | 메타 | 비고 |
|------|-------------|------|--------|------|------|
| A | Huntress / **Amazon** | Twister (Ele) | Cold/Lightning | A tier (top 10 중 7위) | 가장 표준 |
| B | Huntress / **Ritualist** | Rake + Blood Hunt | Bleed+Poison | A tier | Bleed 메타 정석 |
| C | Ranger / Deadeye | Lightning Arrow | Lightning | A tier (Fubgun 가이드) | 창 포기 |
| D | Ranger / Deadeye | Twister (Ele 변형) | Cold/Lightning | off-meta | 사용자 원안 근접 |
| E | Mercenary / Gemling | Whirling Slash Twister | Elemental | niche | Travic 0.4 가이드 있음 |

**결정 대기 항목**: 사용자 원래 의도가 "Deadeye 고정 + Twister 고정" 이면 **옵션 D (Ele Twister Deadeye)** 가 현실, "Bleed + Twister 고정" 이면 **옵션 A+Bleed 변형** 또는 **옵션 B (Rake 변경)**.

---

## 6. Pathcraft-AI 코드 / 데이터 Diff (POE2 통합)

### 6.1 이미 완료 (D0)
- [x] `schema::Game` serde + `as_cli_flag()`
- [x] `extract_data.rs --game poe2` 게임별 출력 디렉터리
- [x] `lib.rs` Tauri 커맨드 7개 `game: Option<Game>` 전파
- [x] Python 스크립트 4개 `--game` argparse (pob_parser/build_coach/filter_generator/patch_note_scraper)

### 6.2 D2 (젬 DB) — 필요 파일
- [ ] `data/valid_gems_poe2.json` — GGPK SkillGems POE2 → ~355 skill + 526 support + 53 spirit + 58 Lineage
- [ ] `data/gem_tags_poe2.json` — ~180+ tags (Wind 태그 0.4 신규)
- [ ] `data/gem_weapon_restrictions_poe2.json` — 스킬당 허용 무기 리스트 (코치 hallucination 차단 핵심)
- [ ] drift 2건 역추적 (Option B):
  - Mods POE2 actual 677B / schema 653B / diff **+24B**
  - SkillGems POE2 actual 239B / schema 207B / diff **+32B**

### 6.3 D3 (아이템 베이스) — 필요 파일
- [ ] `data/base_items_poe2.json` — 18 무기 클래스 (POE1 14종 + Spear/Quarterstaff/Crossbow/Flail/Talisman 신규)
- [ ] `data/item_classes_poe2.json` — Focus (off-hand caster), Charm (belt 1~3 슬롯) 포함
- [ ] `data/uniques_poe2.json` — ~403 unique (73 무기 / 207 방어구 / 123 기타)

### 6.4 D4 (패시브 트리) — 별도 PRD 요구
- [ ] `data/passive_tree_poe2.json` — 1500+ 노드, 21 jewel sockets (15 basic + 6 large)
- [ ] 8 클래스 start 좌표 (Huntress, Druid 포함)
- [ ] 22 어센던시 노드 (Deadeye/Pathfinder/Amazon/Ritualist/Invoker/Chayula/Titan/Warbringer/Smith/Witchhunter/Gemling/Tactician/Stormweaver/Chronomancer/Varashta/Blood Mage/Infernalist/Lich/Abyssal Lich/Shaman/Oracle)

### 6.5 D5 (필터) — 경량
- [ ] `src/components/FilterPanel.tsx` 게임별 itemClass 리스트 분기
- [ ] POE2 filter 문법 POE1 과 호환 (NeverSink POE2 공식 공개)
- [ ] Item class 명칭 매핑 (Quiver 는 POE2 도 존재, Charm/Focus 신규)

### 6.6 D6 (코치 프롬프트) — 별도 PRD

**Spirit gems 화이트리스트 의도적 제외 (audit 추가 발견)**:
`coach_normalizer._load_valid_gems(game="poe2")` 는 `active + support + spirit` 전부 flatten 해서 L2 allowlist 생성. 하지만 `load_valid_support_gems(game="poe2")` (SYSTEM_PROMPT 주입용) 와 `load_valid_active_skills_poe2()` (Active 화이트리스트 주입용) 는 **support / active 카테고리만** 추출, spirit 제외.

사유: POE2 에서 spirit gems (Ancestral Spirits / Raging Spirits 2종) 는 **별도 Spirit 슬롯** 에 배치되는 POE1 상 minion 젬 개념과 유사. 코치가 "support gem 추천" 맥락에서 spirit gem 을 support 로 잘못 제안할 여지를 차단하기 위해 SYSTEM_PROMPT 화이트리스트에서는 제외. 단, L2 normalizer 는 spirit 이름을 valid 로 인식 (응답에 spirit gem 이 나와도 drop 하지 않음).

후속 D6 재설계 시 `coach_build` 에 "spirit gems = 이런 것들" 섹션 별도 주입 고려 (Herald of Blood 같은 Spirit-cost 스킬 상담 시).

- [ ] `python/build_coach.py` SYSTEM_PROMPT POE2 분기
  - Spirit 시스템 (마나 예약 대체)
  - Uncut gem system
  - Support 캐릭터당 1회 제약
  - Bleed 공식 (15% phys hit / 5s / 2x 이동)
  - Ailment threshold / Heavy Stun / Deflection 0.3 신규
- [ ] `coach_validator.py` 이중 화이트리스트 (게임별 젬 세트)
- [ ] **"존재 안 하는 조합" 플래그** — Deadeye Bleed Twister 류 커뮤니티 레퍼런스 부재 빌드 경고

### 6.7 D7 (Syndicate 비활성) — 0.1 세션
- [x] lib.rs `syndicate_recommend` + `analyze_syndicate_image` 이미 game==poe2 거부
- [ ] `src/components/SyndicateBoard.tsx` game==='poe2' 시 렌더 skip
- [ ] 상단 네비 탭 숨김

### 6.8 프론트엔드 activeGame → invoke 연결 (전 단계 선행)
- [ ] `useBuildAnalyzer` / `FilterPanel` / `App` / `useSyndicateBoard` → activeGame 주입
- 현재 Option::None 으로 POE1 기본 동작

---

## 7. GGPK 마이닝 실측 결과 (2026-04-21)

### 7.1 D0 경로 분기 버그 발견·수정
**1차 실행: 19/19 "파일 없음"** — extract_data.rs TARGETS 가 POE1 `Data/X.datc64` 로 하드코딩, POE2 번들 경로(`data/balance/<lowercase>.datc64`) 미대응.

**Fix**: `CliGame::resolve_table_path()` 추가 → POE2 시 경로 변환 후 `find_file()`. `table_name` (스키마 매칭용) 은 원본 케이스 유지.

### 7.2 2차 실행 — 18/19 성공

| 테이블 | rows | B/row | 비고 |
|--------|------|-------|------|
| ActiveSkills | 1087 | 330 | |
| BaseItemTypes | 4269 | 308 | |
| Maps | 16 | 83 | 0.4 Fate of Vaal 맵 pool 소수 |
| PassiveSkills | **7676** | 392 | 전체 노드 (small/notable/keystone 합) |
| QuestRewards | 159 | 191 | |
| **SkillGems** | **1103** | **239** | 리서치 1111 ≈ 일치. drift +32B |
| **UniqueStashLayout** | **403** | 83 | 리서치 403 unique **정확 일치** ✓ |
| Tags | 1203 | 44 | |
| **Mods** | 14841 | **677** | drift +24B |
| ModType | 11832 | 41 | |
| ModFamily | 5749 | 8 | |
| **Characters** | **12** | 656 | 8 출시 + 4 미출시 (Marauder/Duelist/Shadow/Templar?) |
| **Ascendancy** | **37** | 165 | 24 출시 + 13 미출시/숨김 |
| GemTags | 67 | 64 | |
| ArmourTypes | 562 | 40 | |
| Scarabs | 64 | 24 | POE1 잔존 파일 (POE2 기능 없음) |
| Essences | 81 | 113 | |
| Flasks | 31 | 80 | |
| **ScarabTypes** | — | — | **파일 없음** (POE2 에 없음) |

### 7.3 drift 실측 재확인 (feasibility 일치)
- **Mods**: actual 677B, schema 653B → **+24B 누락**
- **SkillGems**: actual 239B, schema 207B → **+32B 누락**

=> **Option B 권장 유지** (로컬 override + byte pattern 역추적, 1 세션)

### 7.4 리서치 대비 불일치 (추가 확인 필요)
1. **Characters 12 rows vs 리서치 8 클래스** → 리서치는 "출시된 8개" 만 확인. GGPK 데이터는 미출시 4개 포함 가능성 (Marauder/Duelist/Shadow/Templar 1.0 예정)
2. **Ascendancy 37 rows vs 리서치 24** → 13 차이. POE2 데이터마인 (poe2db) 는 "12 classes × ~24" 로 세어 24 로 표현했지만 실 GGPK 는 미출시 + POE1 잔존 어센 포함 가능성
3. **GemTags 67 vs 리서치 180+** → Tag 정의 시스템 분리 (GemTags = skill category tag ≠ Keywords 전체)

### 7.5 JSON 변환 실측 (2026-04-22)

**추가 버그 발견**: `--json` 1차 실행 시 Mods (14841 rows, drift +24B) 에서 parse_table 40분+ hang. fix: TARGETS 순서 재배치 (Mods/ModType/ModFamily 맨 끝으로) → Characters/Ascendancy/나머지 우선 JSON 생성 후 Mods 에서 중단 가능.

**JSON 성공 15 테이블**: ActiveSkills, ArmourTypes, Ascendancy, BaseItemTypes, Characters, Essences, Flasks, GemTags, Maps, PassiveSkills, QuestRewards, Scarabs, SkillGems, Tags, UniqueStashLayout
**미생성 3 테이블**: Mods, ModType, ModFamily (drift 2건 역추적 후 별도 처리 — backlog 4번)

### 7.6 리서치 vs 실 GGPK 교차 검증 결과 (ground truth 확정)

**Characters**:
- 실 12 rows = **출시 8 + 미출시 4**
- 출시: Warrior, Sorceress, Huntress, Mercenary, Monk, Druid, Ranger, Witch
- 미출시 (1.0 계획): Marauder, Duelist, Shadow, Templar

**Ascendancy**:
- 실 37 rows = **정식 21 + [DNT-UNUSED] 16 (fishing 잔존)**
- 정식 21개: Warrior 3 · Ranger 2 · Huntress 2 · **Witch 4** · Sorceress 3 · Mercenary 3 · Druid 2 · Monk 2
- **확정**: Abyssal Lich (Witch 4번째), Disciple of Varashta (Sorceress 3번째) — 리서치 예측 재확인
- DNT-UNUSED: Bait Fisher, Handliner, Harpooner, Trawler, Wildfowler 등 fishing 계열 (GGG 내부 테스트 잔존, 무시)

**BaseItemTypes 젬 카테고리**:
- Active 477 / Support 600 / Spirit 2 / DNT-UNUSED 71
- **총 1079 valid gems**

**Spear 스킬 ground truth (WeaponRequirements=25)**: 21개 전수
```
Blood Hunt / Cull The Weak / Disengage / Elemental Siphon / Elemental Sundering /
Explosive Spear / Fangs of Frost / Glacial Lance / Lightning Spear / Primal Strikes /
Rake / Rapid Assault / Shattering Spite / Spear of Solaris / Spearfield /
Storm Lance / Thunderous Leap / Twister / Whirling Slash / Whirlwind Lance /
Wind Serpent's Fury
```
→ **poe2db 의 "Spear-only" 주장 — 실 GGPK ActiveSkills.json 에서 21개 스킬 (twister/whirling_slash/whirlwind_lance/rake/spear_of_solaris 포함) WeaponRequirements=25 bitmask 일치 확인. bitmask 25 의 Spear 전용 의미 자체는 추정 (Spear class 외 21개 모두 Huntress 시그니처이고 axe_whirling_slash=7 등 다른 bitmask 와 대비됨)**

**리서치 Agent 8 의 24개 Spear 카탈로그 vs 실 21**: Spear Stab/Spear Throw/Tame Beast/Bloodhound's Mark 는 active skill gem 이 아니거나 다른 무기 태그. 정식 skill gem 21개가 실측.

### 7.7 valid_gems_poe2.json 생성 완료
- 위치: `data/valid_gems_poe2.json`
- 스크립트: `scripts/build_valid_gems_poe2.py`
- 조인: BaseItemTypes (이름) + SkillGems (메타) + ActiveSkills (WeaponRequirements, DisplayedName)
- POE1 `valid_gems.json` (1130 gems) 과 동급 화이트리스트 인프라 확보
- **D2 첫 산출물 완료**

### 7.8 drift 역추적 — 완료 (2026-04-22)

**방법**: `scripts/drift_reverse_poe2.py` — datc64 바이너리에서 각 row 의 schema 뒤 N바이트 샘플링 + 8B chunk 별 값 분포 분석으로 타입 추정.

**SkillGems +32B 구조 확정**:
| chunk | 값 패턴 | 타입 추정 |
|-------|---------|-----------|
| col[0] (0..8) | all zero | List count=0 |
| col[1] (8..16) | small uint (332..96856) | List offset |
| col[2] (16..24) | all zero (col[0] 과 동일) | List count=0 |
| col[3] (24..32) | col[1] 과 **완전 중복 값** | List offset (duplicate) |

→ **List × 2** (16B + 16B = 32B). 207 + 32 = **239 ✓**
→ 두 List 모두 null pattern (빈 리스트에 default offset), 값 중복 → alt gem variant 또는 내부 reference 추정

**Mods +24B 구조 확정**:
| chunk | 값 패턴 | 타입 추정 |
|-------|---------|-----------|
| col[0] (0..8) | all zero | List count=0 |
| col[1] (8..16) | small uint (0..16) | List offset (default 작은 값) |
| col[2] (16..24) | varied small uint (0..21986) | Row (self-reference rowid) |

→ **List (16B) + Row (8B) = 24B**. 653 + 24 = **677 ✓**
→ Row 는 Mods 자체 또는 관련 테이블 rowid (ArchnemesisMinionMod 잔존 가능성)

**산출물**: `data/schema/schema_poe2_override.json`
- `SkillGems_poe2_extra.fields`: 2 List 필드 정의
- `Mods_poe2_extra.fields`: 1 List + 1 Row 필드 정의

**다음 단계 (구현 남음, 역추적 자체는 완료)**:
- `SchemaStore::load_for_game(Poe2)` 에 override merge 로직 추가
- 또는 간단히 schema.min.json POE2 tables 에 extra 필드 append
- 재추출 시 Mods JSON 변환 정상 완료 (14841 rows) 예상
- override 적용 후 WeaponRestriction 등 의미 컬럼이 Unknown field 중 어느 것인지 최종 라벨링 (현재 모두 Unknown 이름)

---

## 8. 결정 대기 항목

| 항목 | 옵션 | 권장 |
|------|------|------|
| drift 2건 처리 | A 기다리기 / B 로컬 override 역추적 / C 부분 호환 | **B** (backlog 4번 권장 유지) |
| 빌드 방향 | A/B/C/D/E (§5.3) | **GGPK 마이닝 결과 본 후 결정** |
| D4 패시브 선행 여부 | 빌드 결정 후 클래스에 맞는 부분만 / 전체 선행 | **부분 선행** (스코프 크리프 방지) |
| D6 PRD 필요 | POE1 Phase H 구조 재활용 / 전면 재설계 | **재활용** (normalizer infra game-agnostic) |

---

## 9. 잔여 리서치 에이전트 (백그라운드)

- ✅ 커뮤니티 재시도 (78/100, block gap — pop% 수치 해결 불가, 재시도 무효 확정)
  - 주요 추가 fact: Big Ducks Twister Amazon Phys+Fire (Jan 2026), travic Deadeye Ele Twister 자조 "dead in the name", Bleed Twister Deadeye 레퍼런스 전무 재확인
- 🔄 poe2wiki 재시도 (fallback chain: fextralife / poe2db / game8) — 실행 중

---

## 10. 빌드 방향 결정 근거 (사용자 선택 대기)

### 10.1 사용자 원안 정합성
- 원안: "Deadeye + Twister + Bleed + 리그 스타터"
- 0.4 커뮤니티 레퍼런스 부재 (6개 소스 교차 확인)
- 기계적 성립 (Spear 장착 + Projectile 태그) 은 가능하나 Deadeye 어센던시 노드 Bleed 지원 없음

### 10.2 실 메타 대안
| 옵션 | 클래스 | 스킬 | 데미지 | 레퍼런스 (최신) | 권장도 |
|------|--------|------|--------|-----------------|--------|
| **A** | Huntress/**Amazon** | Twister | **Phys+Fire** (Brutality+Herald of Ash) | Big Ducks 2026-01-14 "All Content Viable" | ⭐⭐⭐ |
| **B** | Huntress/**Amazon** | Twister | **Bleed** (Windstorm Lance+Spear Field+Blood Hunt) | sprEEEzy 2025-04-19 | ⭐⭐⭐ |
| **C** | Huntress/**Ritualist** | **Rake** (Twister 아님) | Bleed+Poison | poe-vault 2025-12-13 | ⭐⭐ (Twister 포기) |
| **D** | Ranger/**Deadeye** | Twister | **Ele (Cold+Lightning)** | travic 2025-12-26 | ⭐ ("dead in the name") |
| **E** | Ranger/**Deadeye** | Lightning Arrow | Lightning | Fubgun | ⭐⭐ (Twister 포기) |

**권장 경로**: 사용자 실제 의도 확인 필요
- "Deadeye 고정" → D (Ele Twister Deadeye) — 생존 취약하지만 0.4 가이드 존재
- "Bleed Twister 고정" → B (sprEEEzy Amazon Bleed Twister) — 레퍼런스 명확
- "빌드깎기 속도 우선" → A (Big Ducks 최신 Phys+Fire Amazon) — 최신 업데이트 + 메타 정석
