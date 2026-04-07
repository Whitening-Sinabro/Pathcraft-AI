//! POE DAT64 테이블 스키마
//!
//! poe-tool-dev/dat-schema의 schema.min.json을 런타임에 로드.
//! https://github.com/poe-tool-dev/dat-schema

use crate::dat64::{FieldDef, FieldType, TableSchema};
use serde::Deserialize;
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

/// 스키마 저장소
pub struct SchemaStore {
    tables: HashMap<String, TableSchema>,
}

impl SchemaStore {
    /// schema.min.json 로드
    pub fn load(path: &Path) -> Result<Self, String> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| format!("스키마 파일 읽기 실패: {}", e))?;

        let schema_file: SchemaFile = serde_json::from_str(&content)
            .map_err(|e| format!("스키마 JSON 파싱 실패: {}", e))?;

        let mut tables = HashMap::new();

        for table in schema_file.tables {
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
                        "i8" | "u8" | "enumrow" => FieldType::U8,
                        "i16" | "u16" => FieldType::I16,
                        "i32" | "u32" | "enum" => FieldType::I32,
                        "i64" | "u64" => FieldType::I64,
                        "f32" => FieldType::F32,
                        "string" => FieldType::Str,
                        "foreignrow" | "row" | "rid" => FieldType::Key,
                        _ => FieldType::I32, // 알 수 없는 타입 → i32 폴백
                    }
                };

                FieldDef { name, field_type }
            }).collect();

            tables.insert(table.name.clone(), TableSchema {
                name: table.name,
                fields,
            });
        }

        Ok(Self { tables })
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

    #[test]
    fn test_load_schema() {
        let schema_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .join("data")
            .join("schema")
            .join("schema.min.json");

        if !schema_path.exists() {
            // 스키마 파일 없으면 스킵
            return;
        }

        let store = SchemaStore::load(&schema_path).unwrap();
        assert!(store.table_count() > 1000, "테이블 수 부족: {}", store.table_count());

        // 핵심 테이블 확인
        assert!(store.get("ActiveSkills").is_some());
        assert!(store.get("SkillGems").is_some());
        assert!(store.get("BaseItemTypes").is_some());
        assert!(store.get("Maps").is_some());

        // 필드 확인
        let active_skills = store.get("ActiveSkills").unwrap();
        assert!(!active_skills.fields.is_empty());
    }
}
