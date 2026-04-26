# Design Exceptions Log

> 프로젝트당 최대 **2개**. 3개째 추가 시 pre-commit BLOCK.
> 각 예외는 아래 Format으로 기록. 예외 없으면 아래 "현재 예외 없음" 유지.

## Format

```
### Exception #N — <파일:라인>
- **Date:** YYYY-MM-DD
- **Pattern:** <어떤 금지 패턴이 사용됐는가>
- **Reason:** <왜 필요한가. 대안이 왜 불가능한가>
- **Alternatives considered:** <시도했지만 안 된 대안들>
- **Screenshot:** <경로>
- **Approved by:** <본인 이름>
```

---

## 현재 예외

### Exception #1 — global.css:43-44 (`--passive-notable` / `--passive-notable-border`)
- **Date:** 2026-04-26
- **Pattern:** raw hex (`#E8C068`, `#4A3F2A`) — design-tokens.css 의 "var(--color-*) 만 사용" 룰 외 정의
- **Reason:** POE 게임 도메인 컬러 (notable 노드 테두리/제목). 패시브 트리 viewer 가 게임 시각 언어를 보존해야 사용자 인지에 부합. accent 1개로 표현 불가능 (gold + brown 2색). 인라인 hex 사용 (PassiveTreeCanvas.tsx tooltip 4곳) 대비 토큰화가 더 정도.
- **Alternatives considered:**
  - `var(--rarity-unique)` (`#C89660`) — 색감 다름 (orange 톤), POE notable gold 표현 어색
  - `var(--accent-primary)` (`#8B6FFF` 보라) — 의미 불일치
  - design-tokens.css 의 `--color-accent` override — 단일 accent 룰 위반 (hero CTA 와 충돌)
- **Screenshot:** `_analysis/poe2_tree_after_fix.png` (tooltip border/title 시각 적용 확인)
- **Approved by:** Shovel (S12, 2026-04-26)
- **Note:** 기존 `global.css` 의 `--rarity-*` / `--tier-*` / `--syndicate-*` 등 도메인 토큰 다수가 raw hex 정의로 선례 존재. 본 추가는 동일 패턴.
