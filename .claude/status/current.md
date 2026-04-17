## 지금
- **F0-fix-1 실행 대기** — `extract_data.rs` TARGETS 7→19 소스만 커밋됨 (`5bbede3`). cargo run 별도 세션

## 다음 (우선순위순)
1. [ ] **F0-fix-1 실행**: `cd src-tauri && cargo run --bin extract_data` (~10분, POE 경로 자동탐지)
   - 산출: `data/game_data/`에 Tags/Mods/ModType/ModFamily/Characters/Ascendancy/GemTags/ArmourTypes/Scarabs/ScarabTypes/Essences/Flasks JSON
   - 검증: 각 JSON 스모크 로드 + 기존 `load_category_data` 회귀 (pytest PASS)
2. [ ] **F0-fix-2**: `sections_continue.load_ggpk_items` 태그 기반 재작성 (1.5h, fix-1 후)
   - 현재 Name 패턴 매칭 → `BaseItemTypes.TagsKeys` → `Tags` 해결로 전환
   - 리스크: breach/scarab/essence 분류 결과가 기존과 달라질 수 있음 → 스냅샷 테스트로 diff 박제
3. [ ] **F0-fix-3**: `scripts/validate_mod_names.py` (1h)
   - `defense_mod_tiers.json` / `accessory_mod_tiers.json` / `weapon_mod_tiers.json` mod 이름이 GGPK `Mods.Name`과 일치하는지 스팟체크
4. [ ] **Phase F2~F7 본진 감사** (12~18h, F0-fix-1/2 완료 후)
   - F2 Breach/Legion/Scarab/Incursion/Expedition (테이블 다수 추출 완료 상태 가정)
   - F3 Heist/Delve/Blight 등
   - F4 Sanavi / F5 Syndicate / F7 Crafting mods
5. [ ] **인게임 검증** (사용자 영역, Claude 대기)
   - Phase B+C Step 6b: 무기 필터 Tyrannical vs Heavy, DropLevel 5 리튜닝
   - Phase D 방어 필터 스모크
   - Phase E 악세서리 필터 스모크
   - 패시브 트리 Phase 3 한국어 stat 툴팁 호버 지연

## 완료된 기능 (참조용, git log 대체 요약)
- **β Continue 필터 L0~L10**: weapon_phys_proxy(B+C), defense_proxy(D), accessory_proxy(E) 모두 L7 통합. L7 7-way 순서 박제됨
- **패시브 트리 Phase 1~3**: Canvas 뷰어 / PoB URL 자동 디코드 / 한국어 stat 툴팁 (91.9%)
- **F1+F6**: 디비카/유니크 단일 진실원 + HCSSF Mirage 파이프라인

## 도메인 파일 포인터
- [메커닉 데이터 감사 플랜 (Phase F)](mechanic_data_audit_plan.md)
- [Build-aware 무기 필터 플랜 (Phase B+C)](build_aware_weapon_filter_plan.md)
- [패시브 트리 플랜](passive_tree_plan.md)
- [Continue 아키텍처 (β)](continue_architecture.md)
- [필터 분석](filter_analysis.md)
- _analysis/ggpk_extraction_completeness_audit.md — F0 감사 (0.76% 커버리지)
- _analysis/mechanic_data_audit_divcard_unique.md — F1+F6 리포트
- _analysis/neversink_weaponphys_rules.md — NeverSink 812-844 무기 mod-tier
- _analysis/gem_weapon_restriction_audit.md — GGPK 부정확성 증거 (187 스킬)

## Class Start 노드 매핑 (data.json, 수동 — Characters.json 추출 후 자동화 예정)
- 0: Scion (58833) / 1: Marauder (47175) / 2: Ranger (50459)
- 3: Witch (54447) / 4: Duelist (50986) / 5: Templar (61525) / 6: Shadow (44683)

## 잔존 이슈 (허용됨)
- PassiveTreeCanvas.tsx 591 line (300 룰 초과, 기능 복잡도로 허용)
- 일부 엣지 굵기 불일치 (arc stroke vs 직선 sprite)

## 블로커
- 없음

## UX 결정 기록 (패시브 트리)
- 우클릭 dealloc 분리 시도 → 되돌림 (왼클릭 토글 유지)
- 수동 URL import UI 스킵 (Phase 2 자동 디코드로 대체)
- 드롭다운 형식 (공간 절약)
- AI 이모지 제거
