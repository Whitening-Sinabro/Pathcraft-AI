-- PathcraftAI HC Journey DB — POE2 하드코어(→이후 SSF) 니치
-- 설계 원칙: 자동 추출(transition_change)과 사람 큐레이션(transition_note)을 물리적으로 분리한다.
--   자동 = 밴드 PoB diff·ninja 스냅샷 (WHAT/WHEN). 확장 가능.
--   큐레이션 = VOD/자막에서 뽑은 비용·조건·함정·왜 (20%). HC/SSF의 진짜 가치.
-- game 컬럼은 지금 'poe2' 고정이나, 이후 POE1 포팅 시 데이터만 추가하도록 남긴다.

PRAGMA foreign_keys = ON;

-- Layer 2: 크리에이터 / 빌드 / 스냅샷 ------------------------------------------
CREATE TABLE IF NOT EXISTS creator (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  channel_url   TEXT,
  ninja_account TEXT,           -- poe.ninja account (개별 조회용)
  notes         TEXT,
  UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS build (
  id            INTEGER PRIMARY KEY,
  creator_id    INTEGER NOT NULL REFERENCES creator(id) ON DELETE CASCADE,
  game          TEXT NOT NULL DEFAULT 'poe2',
  league        TEXT,           -- 예: hc-forbidden-rites
  hardcore      INTEGER NOT NULL DEFAULT 1,
  ssf           INTEGER NOT NULL DEFAULT 0,
  name          TEXT NOT NULL,  -- 예: 젬링 화염파 → 검은화염 카오스
  ascendancy    TEXT,           -- 예: Gemling Legionnaire
  notes         TEXT,
  UNIQUE(creator_id, name)
);

-- 빌드 타임라인의 한 지점 (밴드 계획본, 실캐릭 라이브, 연구 판독 등)
CREATE TABLE IF NOT EXISTS snapshot (
  id            INTEGER PRIMARY KEY,
  build_id      INTEGER NOT NULL REFERENCES build(id) ON DELETE CASCADE,
  order_idx     INTEGER NOT NULL,     -- 타임라인 순서(0=가장 이름)
  stage_label   TEXT NOT NULL,        -- 예: ACT1, ACT3-4, 엔드게임(목표), 실캐릭 lv93
  level_hint    INTEGER,              -- 알면 캐릭터 레벨
  source_type   TEXT NOT NULL,        -- planner_band | ninja_live | research
  source_ref    TEXT,                 -- 파일 경로 또는 URL
  captured_utc  TEXT,
  passives_n    INTEGER,              -- 배정 패시브 수(요약)
  ascendancy_n  INTEGER,
  UNIQUE(build_id, order_idx)
);

CREATE TABLE IF NOT EXISTS snapshot_skill (
  id            INTEGER PRIMARY KEY,
  snapshot_id   INTEGER NOT NULL REFERENCES snapshot(id) ON DELETE CASCADE,
  main_gem      TEXT NOT NULL,        -- 정규화된 스킬명(메타 ID에서 유도)
  supports      TEXT NOT NULL DEFAULT '[]'  -- JSON 배열(보조 젬명)
);

CREATE TABLE IF NOT EXISTS snapshot_item (
  id            INTEGER PRIMARY KEY,
  snapshot_id   INTEGER NOT NULL REFERENCES snapshot(id) ON DELETE CASCADE,
  slot          TEXT NOT NULL,        -- Weapon1, Helm1 ...
  item_name     TEXT,                 -- 유니크명 또는 베이스 첫 줄
  mods_text     TEXT
);

-- Layer 3: 여정(전환) ---------------------------------------------------------
-- 연속한 두 스냅샷 사이의 한 단계.
CREATE TABLE IF NOT EXISTS transition (
  id            INTEGER PRIMARY KEY,
  build_id      INTEGER NOT NULL REFERENCES build(id) ON DELETE CASCADE,
  order_idx     INTEGER NOT NULL,
  from_snapshot INTEGER NOT NULL REFERENCES snapshot(id) ON DELETE CASCADE,
  to_snapshot   INTEGER NOT NULL REFERENCES snapshot(id) ON DELETE CASCADE,
  UNIQUE(build_id, order_idx)
);

-- 자동 추출: 밴드/스냅샷 diff 결과. 확장 가능·재생성 가능.
CREATE TABLE IF NOT EXISTS transition_change (
  id            INTEGER PRIMARY KEY,
  transition_id INTEGER NOT NULL REFERENCES transition(id) ON DELETE CASCADE,
  kind          TEXT NOT NULL,        -- skill_added|skill_removed|support_changed|item_changed|passive_delta
  subject       TEXT,                 -- 스킬명/슬롯 등
  detail        TEXT                  -- 사람이 읽는 요약
);

-- 사람 큐레이션(20%): 비용·조건·함정·왜.
--   source='hand' = 그 빌드에만 해당하는 고유 손노동(초반 창에서만 가능).
--   source='rule' = curation_rule 에서 자동 적용된 재사용 지식(DB 커져도 공짜로 붙음).
CREATE TABLE IF NOT EXISTS transition_note (
  id            INTEGER PRIMARY KEY,
  transition_id INTEGER NOT NULL REFERENCES transition(id) ON DELETE CASCADE,
  note_type     TEXT NOT NULL,        -- cost|condition|pitfall|why|offstream|survival
  text          TEXT NOT NULL,
  evidence_ref  TEXT,                 -- 예: (영상,초) 또는 문서 경로
  source        TEXT NOT NULL DEFAULT 'hand',  -- hand | rule
  rule_id       INTEGER REFERENCES curation_rule(id)
);

-- 재사용 큐레이션 규칙: 초반 손노동을 여기로 뽑아내면 이후 모든 빌드에 자동 적용된다.
-- trigger_kind: keystone | skill_added | item_slot_change | ascendancy | league
--   keystone         -> 빌드 키스톤 목록과 매칭
--   skill_added      -> 어느 전환에서 그 스킬이 추가되면 발화
--   item_slot_change -> 어느 전환에서 그 슬롯 장비가 바뀌면 발화
--   ascendancy       -> 빌드 전직과 매칭, 첫 전환에 부착
--   league           -> 빌드 리그 모드(trade | ssf)와 매칭, 첫 전환에 부착. 슬롯 무관 거래/SSF 지식은 여기.
CREATE TABLE IF NOT EXISTS curation_rule (
  id            INTEGER PRIMARY KEY,
  trigger_kind  TEXT NOT NULL,
  trigger_key   TEXT NOT NULL,
  note_type     TEXT NOT NULL,
  text          TEXT NOT NULL,
  evidence_ref  TEXT,
  UNIQUE(trigger_kind, trigger_key, note_type)
);

-- 빌드가 실제로 든 키스톤(ninja 실측). keystone 규칙 매칭용.
CREATE TABLE IF NOT EXISTS build_keystone (
  build_id      INTEGER NOT NULL REFERENCES build(id) ON DELETE CASCADE,
  keystone      TEXT NOT NULL,
  PRIMARY KEY(build_id, keystone)
);

CREATE INDEX IF NOT EXISTS ix_snap_build   ON snapshot(build_id, order_idx);
CREATE INDEX IF NOT EXISTS ix_skill_snap   ON snapshot_skill(snapshot_id);
CREATE INDEX IF NOT EXISTS ix_item_snap    ON snapshot_item(snapshot_id);
CREATE INDEX IF NOT EXISTS ix_trans_build  ON transition(build_id, order_idx);
CREATE INDEX IF NOT EXISTS ix_change_trans ON transition_change(transition_id);
CREATE INDEX IF NOT EXISTS ix_note_trans   ON transition_note(transition_id);
