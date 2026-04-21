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
}

#[derive(Deserialize)]
struct SchemaRef {
    table: Option<String>,
    column: Option<String>,
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
    pub fn load_for_game(path: &Path, game: Game) -> Result<Self, String> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| format!("스키마 파일 읽기 실패: {}", e))?;

        let schema_file: SchemaFile = serde_json::from_str(&content)
            .map_err(|e| format!("스키마 JSON 파싱 실패: {}", e))?;

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

            let fields: Vec<FieldDef> = table.columns.iter().enumerate().map(|(i, col)| {
                let name = col.name.clone()
                    .unwrap_or_else(|| format!("Unknown{}", i));

                let is_array = col.array.unwrap_or(false);
                let base_type = col.col_type.as_deref().unwrap_or("i32");

                let field_type = if is_array {
                    FieldType::List
                } else {
                    match base_type {
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
                    }
                };

                FieldDef { name, field_type }
            }).collect();

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
}
