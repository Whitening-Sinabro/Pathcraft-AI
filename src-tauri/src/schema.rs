//! POE DAT64 테이블 스키마
//!
//! poe-tool-dev/dat-schema의 schema.min.json을 런타임에 로드.
//! https://github.com/poe-tool-dev/dat-schema

use crate::dat64::{FieldDef, FieldType, TableSchema};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

#[derive(Deserialize)]
struct SchemaFile {
    version: u32,
    tables: Vec<SchemaTable>,
}

#[derive(Deserialize)]
struct SchemaTable {
    name: String,
    columns: Vec<SchemaColumn>,
    /// 1=POE1, 2=POE2, 3=both
    #[serde(rename = "validFor", default)]
    valid_for: u32,
}

#[derive(Deserialize)]
struct SchemaColumn {
    name: Option<String>,
    #[serde(rename = "type")]
    col_type: Option<String>,
    array: Option<bool>,
    unique: Option<bool>,
    references: Option<SchemaRef>,
    /// pypoe schema 의 interval 표시 — i32 가 (min, max) i32 pair 로 8B 차지.
    /// 현재 schema.min.json 에서 POE2 (validFor=2) 4 테이블만 사용 (Mods 등). POE1 미사용.
    #[serde(default)]
    interval: bool,
}

#[derive(Deserialize)]
struct SchemaRef {
    table: Option<String>,
    column: Option<String>,
}

/// POE2 drift override (schema_poe2_override.json)
///
/// schema.min.json 에 누락된 끝 컬럼을 테이블별로 append.
/// 현재 대상: Mods +24B / SkillGems +32B (2026-04-22 byte pattern 역추적).
#[derive(Deserialize)]
struct OverrideFile {
    #[serde(flatten)]
    entries: HashMap<String, OverrideEntry>,
}

#[derive(Deserialize)]
struct OverrideEntry {
    #[serde(default)]
    fields: Vec<OverrideField>,
}

#[derive(Deserialize)]
struct OverrideField {
    name: String,
    #[serde(rename = "type")]
    col_type: String,
    #[serde(default)]
    array: bool,
}

/// 대상 게임 — schema.min.json의 `validFor` 비트마스크 필터링에 사용.
/// bit 0 (1) = POE1, bit 1 (2) = POE2. validFor=3는 양쪽 공용.
///
/// Serde rename_all="lowercase" 로 프론트엔드/CLI 에서 "poe1"/"poe2" 문자열 호환.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Game {
    Poe1,
    Poe2,
}

impl Game {
    fn bit(self) -> u32 {
        match self {
            Game::Poe1 => 1,
            Game::Poe2 => 2,
        }
    }
    fn other_bit(self) -> u32 {
        match self {
            Game::Poe1 => 2,
            Game::Poe2 => 1,
        }
    }

    /// Python CLI 플래그 값 ("poe1"/"poe2"). Python 서브프로세스 인자 전달용.
    pub fn as_cli_flag(self) -> &'static str {
        match self {
            Game::Poe1 => "poe1",
            Game::Poe2 => "poe2",
        }
    }
}

impl Default for Game {
    fn default() -> Self {
        Game::Poe1
    }
}

/// 스키마 저장소
pub struct SchemaStore {
    tables: HashMap<String, TableSchema>,
    game: Game,
}

impl SchemaStore {
    /// schema.min.json 로드 (POE1 — back-compat)
    pub fn load(path: &Path) -> Result<Self, String> {
        Self::load_for_game(path, Game::Poe1)
    }

    /// schema.min.json 로드 (게임 지정)
    /// - POE1 요청 시: validFor & 1 인 테이블만 유지 (POE2 전용 305건 스킵)
    /// - POE2 요청 시: validFor & 2 인 테이블만 유지 (POE1 전용 174건 스킵)
    /// - 같은 이름 2버전 공존 시 (예: Mods POE1=78컬럼 / POE2=74컬럼) → 요청 게임 쪽 선택
    /// - POE2 요청 시 `schema_poe2_override.json` 이 schema 파일 옆에 있으면 자동 merge.
    ///   drift 보정 컬럼을 각 테이블 끝에 append (ex: Mods +24B, SkillGems +32B).
    pub fn load_for_game(path: &Path, game: Game) -> Result<Self, String> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| format!("스키마 파일 읽기 실패: {}", e))?;

        let schema_file: SchemaFile = serde_json::from_str(&content)
            .map_err(|e| format!("스키마 JSON 파싱 실패: {}", e))?;

        // POE2 시 drift override 자동 로드. 없으면 graceful skip.
        let override_entries: HashMap<String, OverrideEntry> = if game == Game::Poe2 {
            let override_path = path
                .parent()
                .map(|p| p.join("schema_poe2_override.json"))
                .filter(|p| p.exists());
            match override_path {
                Some(p) => match std::fs::read_to_string(&p) {
                    Ok(txt) => match serde_json::from_str::<OverrideFile>(&txt) {
                        Ok(of) => of.entries,
                        Err(e) => {
                            log::warn!("POE2 override 파싱 실패 ({}): {}", p.display(), e);
                            HashMap::new()
                        }
                    },
                    Err(e) => {
                        log::warn!("POE2 override 읽기 실패 ({}): {}", p.display(), e);
                        HashMap::new()
                    }
                },
                None => HashMap::new(),
            }
        } else {
            HashMap::new()
        };

        let mut tables = HashMap::new();
        let include_bit = game.bit();
        let exclude_only_bit = game.other_bit();

        for table in schema_file.tables {
            // validFor=0 (미지정)는 하위 호환으로 POE1 기본값 취급.
            // validFor가 타 게임 전용 bit만 세워져 있으면 스킵.
            let vf = if table.valid_for == 0 { 1 } else { table.valid_for };
            if vf & include_bit == 0 {
                continue;
            }
            // 같은 이름 2버전 공존 시: 공용(validFor=3)보다 전용 엔트리(= include_bit만) 우선.
            // 전용 entry가 "정확한 bit 하나만" 세워진 경우 무조건 교체.
            // 공용 entry가 먼저 insert된 뒤 전용이 와도 덮어씀. HashMap insert 특성 활용.
            let _ = exclude_only_bit; // reserved for future per-game dedup logic

            let mut fields: Vec<FieldDef> = table.columns.iter().enumerate().map(|(i, col)| {
                let name = col.name.clone()
                    .unwrap_or_else(|| format!("Unknown{}", i));

                let is_array = col.array.unwrap_or(false);
                let base_type = col.col_type.as_deref().unwrap_or("i32");

                let base_field_type = match base_type {
                    "bool" => FieldType::Bool,
                    "i8" | "u8" => FieldType::U8,
                    "enumrow" => FieldType::I32,
                    "i16" | "u16" => FieldType::I16,
                    "i32" | "u32" | "enum" => FieldType::I32,
                    "i64" | "u64" => FieldType::I64,
                    "f32" => FieldType::F32,
                    "string" => FieldType::Str,
                    "foreignrow" => FieldType::Key,
                    "row" | "rid" => FieldType::Row,
                    _ => FieldType::I32, // 알 수 없는 타입 → i32 폴백
                };

                let (field_type, element_type) = if is_array {
                    (FieldType::List, Some(base_field_type))
                } else {
                    (base_field_type, None)
                };

                // interval 은 array=false 인 단순 타입에만 의미 있음 (List/Key 와 결합 불가).
                // schema.min.json 데이터상으로도 모두 i32 + interval=true.
                let interval = col.interval && !is_array;

                FieldDef { name, field_type, interval, element_type }
            }).collect();

            // POE2 drift override merge — {TableName}_poe2_extra.fields 를 끝에 append.
            // 대상: Mods (+24B), SkillGems (+32B). 2026-04-22 byte pattern 역추적.
            if game == Game::Poe2 {
                let override_key = format!("{}_poe2_extra", table.name);
                if let Some(entry) = override_entries.get(&override_key) {
                    for extra in &entry.fields {
                        let field_type = if extra.array {
                            FieldType::List
                        } else {
                            match extra.col_type.as_str() {
                                "bool" => FieldType::Bool,
                                "i8" | "u8" => FieldType::U8,
                                "i16" | "u16" => FieldType::I16,
                                "i32" | "u32" | "enum" | "enumrow" => FieldType::I32,
                                "i64" | "u64" => FieldType::I64,
                                "f32" => FieldType::F32,
                                "string" => FieldType::Str,
                                "foreignrow" => FieldType::Key,
                                "row" | "rid" => FieldType::Row,
                                _ => FieldType::I32,
                            }
                        };
                        // override 도 array 면 element_type 에 base 보존.
                        let element_type = if extra.array {
                            Some(match extra.col_type.as_str() {
                                "bool" => FieldType::Bool,
                                "i8" | "u8" => FieldType::U8,
                                "i16" | "u16" => FieldType::I16,
                                "i32" | "u32" | "enum" | "enumrow" => FieldType::I32,
                                "i64" | "u64" => FieldType::I64,
                                "f32" => FieldType::F32,
                                "string" => FieldType::Str,
                                "foreignrow" => FieldType::Key,
                                "row" | "rid" => FieldType::Row,
                                _ => FieldType::I32,
                            })
                        } else {
                            None
                        };
                        fields.push(FieldDef {
                            name: extra.name.clone(),
                            field_type,
                            interval: false,
                            element_type,
                        });
                    }
                }
            }

            // 같은 이름 2버전 공존 처리: 전용 엔트리(vf == include_bit)가 공용(vf==3)보다 우선.
            // 순회 순서는 schema.min.json 순 — 공용이 먼저 오면 전용이 덮음, 전용이 먼저 오면 공용으로 덮여 정보 손실.
            // 후자 방지: 이미 들어있는 entry가 game-specific이면 공용으로 덮어쓰기 금지.
            let should_insert = match tables.get(&table.name) {
                Some(_existing) => {
                    // 현재 엔트리가 전용(vf == include_bit)이면 유지 (덮어쓰기 금지).
                    // 단, schema.min.json이 이미 들어간 게 공용(vf=3)이고 신규가 전용이면 덮음.
                    // HashMap에는 원본 vf가 없으므로 보수적 규칙: 신규가 전용일 때만 덮어씀.
                    vf == include_bit
                }
                None => true,
            };
            if should_insert {
                tables.insert(table.name.clone(), TableSchema {
                    name: table.name,
                    fields,
                });
            }
        }

        Ok(Self { tables, game })
    }

    /// 선택된 게임
    pub fn game(&self) -> Game {
        self.game
    }

    /// 테이블 스키마 조회
    pub fn get(&self, name: &str) -> Option<&TableSchema> {
        self.tables.get(name)
    }

    /// 모든 테이블 이름
    pub fn table_names(&self) -> Vec<&str> {
        self.tables.keys().map(|s| s.as_str()).collect()
    }

    /// 테이블 수
    pub fn table_count(&self) -> usize {
        self.tables.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn schema_path_or_skip() -> Option<PathBuf> {
        let p = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .join("data").join("schema").join("schema.min.json");
        if p.exists() { Some(p) } else { None }
    }

    #[test]
    fn test_load_schema() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let store = SchemaStore::load(&schema_path).unwrap();
        assert_eq!(store.game(), Game::Poe1);
        assert!(store.table_count() > 900, "테이블 수 부족: {}", store.table_count());

        // 핵심 테이블 확인
        assert!(store.get("ActiveSkills").is_some());
        assert!(store.get("SkillGems").is_some());
        assert!(store.get("BaseItemTypes").is_some());
        assert!(store.get("Maps").is_some());

        // 필드 확인
        let active_skills = store.get("ActiveSkills").unwrap();
        assert!(!active_skills.fields.is_empty());
    }

    /// POE2 schema 분리 — validFor bit 필터링이 올바른지 검증.
    /// schema.min.json에 Mods 테이블은 POE1(validFor=1)과 POE2(validFor=2) 2버전 존재.
    /// 로드된 게임별 컬럼 수가 다르면 필터링 동작 증명.
    #[test]
    fn test_load_for_poe2_separates_from_poe1() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let poe1 = SchemaStore::load_for_game(&schema_path, Game::Poe1).unwrap();
        let poe2 = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();

        assert_eq!(poe1.game(), Game::Poe1);
        assert_eq!(poe2.game(), Game::Poe2);

        // 두 store 모두 핵심 공용 테이블(validFor=3) 존재
        assert!(poe1.get("ModType").is_some());
        assert!(poe2.get("ModType").is_some());

        // Mods는 게임별 다른 컬럼 수로 로드돼야 함
        let mods_poe1 = poe1.get("Mods").expect("POE1 Mods 누락");
        let mods_poe2 = poe2.get("Mods").expect("POE2 Mods 누락");
        assert_ne!(
            mods_poe1.fields.len(),
            mods_poe2.fields.len(),
            "POE1/POE2 Mods 컬럼 수 동일 — validFor 필터가 안 먹음"
        );

        // POE1 전용(validFor=1)이 POE2 store에 들어가면 안 됨. 역도 성립.
        // 구체 테이블명 없이 카운트 차이로 검증 — POE1 store > POE2 store 일 수도, 반대도 가능하나 ≠ 확실.
        assert_ne!(
            poe1.table_count(),
            poe2.table_count(),
            "POE1/POE2 store 테이블 수 동일 — 필터링이 동작 안 함"
        );
    }

    /// 실제 .datc64 파일의 행 크기와 스키마 계산 행 크기 일치 검증
    #[test]
    fn test_schema_row_size_matches_actual() {
        let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().unwrap().to_path_buf();
        let schema_path = project_root.join("data").join("schema").join("schema.min.json");
        let game_data_dir = project_root.join("data").join("game_data");

        if !schema_path.exists() || !game_data_dir.exists() {
            return;
        }

        let store = SchemaStore::load(&schema_path).unwrap();

        let test_tables = [
            ("ActiveSkills", "ActiveSkills.datc64"),
            ("BaseItemTypes", "BaseItemTypes.datc64"),
            ("Maps", "Maps.datc64"),
            ("PassiveSkills", "PassiveSkills.datc64"),
            ("QuestRewards", "QuestRewards.datc64"),
        ];

        let mut failures = Vec::new();

        for (table_name, filename) in &test_tables {
            let file_path = game_data_dir.join(filename);
            if !file_path.exists() {
                continue;
            }

            let data = std::fs::read(&file_path).unwrap();
            let parser = crate::dat64::Dat64Parser::load(data).unwrap();
            let actual = parser.estimated_row_size();

            if let Some(schema) = store.get(table_name) {
                let expected = schema.row_size();
                if expected != actual {
                    failures.push(format!(
                        "{}: schema={}B, actual={}B (diff={})",
                        table_name, expected, actual, expected as i64 - actual as i64
                    ));
                }
            }
        }

        assert!(
            failures.is_empty(),
            "스키마/실제 행 크기 불일치:\n{}",
            failures.join("\n")
        );
    }

    /// POE2 row_size 기대값 검증.
    /// - Mods: 6 interval i32 컬럼 (4B→8B 각각) 으로 base 653B 가 자연스럽게 677B 가 됨. override 불요.
    /// - SkillGems: interval 없음 → override +32B 적용 후 239B (207+32).
    #[test]
    fn test_poe2_row_size_matches_actual() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let override_path = schema_path.parent().unwrap().join("schema_poe2_override.json");
        if !override_path.exists() {
            return; // override 파일 없으면 스킵 (개발 환경별 선택 적용)
        }

        let poe2 = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();

        let mods = poe2.get("Mods").expect("POE2 Mods 누락");
        assert_eq!(
            mods.row_size(),
            677,
            "POE2 Mods row_size 677B 기대 (interval 6 컬럼 8B 적용), 실제 {}B",
            mods.row_size()
        );

        let skill_gems = poe2.get("SkillGems").expect("POE2 SkillGems 누락");
        assert_eq!(
            skill_gems.row_size(),
            239,
            "POE2 SkillGems row_size 207+32=239 기대, 실제 {}B",
            skill_gems.row_size()
        );
    }

    /// interval=true 컬럼이 8B (i32 min/max pair) 로 처리되는지 회귀 가드.
    /// schema.min.json POE2 Mods 의 Stat1Value..Stat6Value (6 컬럼) 가 대상.
    #[test]
    fn test_poe2_interval_doubles_field_size() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let poe2 = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();
        let mods = poe2.get("Mods").expect("POE2 Mods 누락");

        let interval_fields: Vec<&FieldDef> = mods.fields.iter().filter(|f| f.interval).collect();
        assert_eq!(
            interval_fields.len(),
            6,
            "POE2 Mods interval 컬럼 6개 (Stat1..6Value) 기대, 실제 {}",
            interval_fields.len()
        );

        for f in &interval_fields {
            assert_eq!(
                f.size_in_row(),
                8,
                "interval 필드 {} size_in_row=8B 기대 (i32 pair), 실제 {}B",
                f.name,
                f.size_in_row()
            );
        }
    }

    /// POE1 Mods 는 interval 컬럼이 없어야 함 (validFor=2 전용 컨벤션).
    /// POE1 회귀 가드: interval 처리 추가로 POE1 row_size 가 변하면 안 됨.
    #[test]
    fn test_poe1_no_interval_columns() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let poe1 = SchemaStore::load_for_game(&schema_path, Game::Poe1).unwrap();
        let mods = poe1.get("Mods").expect("POE1 Mods 누락");

        let interval_count = mods.fields.iter().filter(|f| f.interval).count();
        assert_eq!(interval_count, 0, "POE1 Mods 에 interval 컬럼이 있으면 안 됨");
    }

    /// array 컬럼은 element_type 을 가져야 함 (List element-aware 파싱 회귀 가드).
    /// foreignrow array → Some(Key), i32 array → Some(I32), etc.
    /// element_type=None 이면 read_field 의 legacy 8B i64 로 떨어져 Tags/SpawnWeight_* 가 잘못 읽힘.
    #[test]
    fn test_array_columns_carry_element_type() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        for game in [Game::Poe1, Game::Poe2] {
            let store = SchemaStore::load_for_game(&schema_path, game).unwrap();
            let mods = store.get("Mods").expect("Mods 누락");

            let array_fields: Vec<&FieldDef> = mods.fields.iter()
                .filter(|f| matches!(f.field_type, FieldType::List))
                .collect();
            assert!(!array_fields.is_empty(), "{:?} Mods 에 array 필드 없음", game);

            for f in &array_fields {
                assert!(
                    f.element_type.is_some(),
                    "{:?} Mods.{} (List) 에 element_type 미설정 — read_list_typed 가 legacy fallback 으로 떨어짐",
                    game, f.name
                );
            }
        }
    }

    /// POE1 로드 시 POE2 override 적용 안 됨 — SkillGems Unknown_List1/2 가 POE1 SkillGems 에 섞이면 안 됨.
    #[test]
    fn test_poe1_load_skips_poe2_override() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let poe1 = SchemaStore::load_for_game(&schema_path, Game::Poe1).unwrap();
        let poe2 = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();

        let override_path = schema_path.parent().unwrap().join("schema_poe2_override.json");
        if !override_path.exists() {
            return;
        }

        let sg_poe1 = poe1.get("SkillGems").expect("POE1 SkillGems 누락");
        let sg_poe2 = poe2.get("SkillGems").expect("POE2 SkillGems 누락");

        let has_override_name = sg_poe1.fields.iter().any(|f| {
            f.name == "Unknown_List1" || f.name == "Unknown_List2"
        });
        assert!(
            !has_override_name,
            "POE1 SkillGems 에 POE2 override 필드가 섞였음"
        );

        let poe2_has_override = sg_poe2
            .fields
            .iter()
            .any(|f| f.name == "Unknown_List1" || f.name == "Unknown_List2");
        assert!(
            poe2_has_override,
            "POE2 SkillGems 에 override 필드 누락"
        );
    }

    /// POE2 실 .datc64 파일 row_size 일치 검증 (override 적용 후).
    /// Mods 677B, SkillGems 239B — drift 해소 증명.
    #[test]
    fn test_poe2_schema_matches_actual_after_override() {
        let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().unwrap().to_path_buf();
        let schema_path = project_root.join("data").join("schema").join("schema.min.json");
        let poe2_data_dir = project_root.join("data").join("game_data_poe2");
        let override_path = project_root.join("data").join("schema").join("schema_poe2_override.json");

        if !schema_path.exists() || !poe2_data_dir.exists() || !override_path.exists() {
            return;
        }

        let store = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();

        // drift 대상 2 테이블
        let test_tables = [("Mods", "Mods.datc64"), ("SkillGems", "SkillGems.datc64")];

        for (table_name, filename) in &test_tables {
            let file_path = poe2_data_dir.join(filename);
            if !file_path.exists() {
                continue;
            }
            let data = std::fs::read(&file_path).unwrap();
            let parser = crate::dat64::Dat64Parser::load(data).unwrap();
            let actual = parser.estimated_row_size();
            let schema = store.get(table_name).expect("POE2 테이블 누락");
            let expected = schema.row_size();
            assert_eq!(
                expected, actual,
                "{} drift 미해소: schema={}B, actual={}B",
                table_name, expected, actual
            );
        }
    }

    /// override 필드 타입 파싱 — SkillGems Unknown_List1/2 가 List(16B) 으로 매핑돼야 함.
    /// (Mods override 는 2026-04-25 제거 — interval 처리로 대체)
    #[test]
    fn test_poe2_override_field_type_mapping() {
        let Some(schema_path) = schema_path_or_skip() else { return };

        let override_path = schema_path.parent().unwrap().join("schema_poe2_override.json");
        if !override_path.exists() {
            return;
        }

        let poe2 = SchemaStore::load_for_game(&schema_path, Game::Poe2).unwrap();

        // SkillGems 끝 2 컬럼: Unknown_List1 + Unknown_List2 (각 16B)
        let sg = poe2.get("SkillGems").unwrap();
        let last_two_sg = &sg.fields[sg.fields.len() - 2..];
        assert_eq!(last_two_sg[0].name, "Unknown_List1");
        assert_eq!(last_two_sg[0].field_type.size(), 16);
        assert_eq!(last_two_sg[1].name, "Unknown_List2");
        assert_eq!(last_two_sg[1].field_type.size(), 16);
    }
}
