//! POE DAT64 바이너리 파일 파서
//!
//! DAT64 포맷:
//! - [0..4]: row_count (u32 LE)
//! - [4..marker]: 고정 데이터 (row_count × row_size 바이트)
//! - [marker]: 0xBBBBBBBBBBBBBBBB (8바이트)
//! - [marker+8..EOF]: 가변 데이터 (UTF-16LE 문자열, 리스트)

use std::collections::HashMap;

const MARKER: [u8; 8] = [0xBB; 8];

/// DAT64 필드 타입
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FieldType {
    Bool,     // 1 byte
    I32,      // 4 bytes
    U32,      // 4 bytes
    I64,      // 8 bytes
    U64,      // 8 bytes
    F32,      // 4 bytes
    Str,      // 8 bytes (offset into variable data)
    List,     // 16 bytes (count: i64 + offset: i64)
    Key,      // 16 bytes (foreign row: row_index i64 + reserved i64)
    I16,      // 2 bytes
    U16,      // 2 bytes
    U8,       // 1 byte
}

impl FieldType {
    pub fn size(&self) -> usize {
        match self {
            FieldType::Bool | FieldType::U8 => 1,
            FieldType::I16 | FieldType::U16 => 2,
            FieldType::I32 | FieldType::U32 | FieldType::F32 => 4,
            FieldType::I64 | FieldType::U64 | FieldType::Str => 8,
            FieldType::Key => 16,
            FieldType::List => 16,
        }
    }
}

/// 필드 정의
#[derive(Debug, Clone)]
pub struct FieldDef {
    pub name: String,
    pub field_type: FieldType,
}

/// 테이블 스키마
#[derive(Debug, Clone)]
pub struct TableSchema {
    pub name: String,
    pub fields: Vec<FieldDef>,
}

impl TableSchema {
    pub fn row_size(&self) -> usize {
        self.fields.iter().map(|f| f.field_type.size()).sum()
    }
}

/// 파싱된 DAT64 값
#[derive(Debug, Clone)]
pub enum Value {
    Bool(bool),
    I32(i32),
    U32(u32),
    I64(i64),
    U64(u64),
    F32(f32),
    Str(String),
    List(Vec<Value>),
    Key(i64),
    I16(i16),
    U16(u16),
    U8(u8),
    Null,
}

impl Value {
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Value::Str(s) => Some(s),
            _ => None,
        }
    }

    pub fn as_i64(&self) -> Option<i64> {
        match self {
            Value::I64(v) => Some(*v),
            Value::I32(v) => Some(*v as i64),
            Value::U32(v) => Some(*v as i64),
            _ => None,
        }
    }

    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Value::Bool(v) => Some(*v),
            _ => None,
        }
    }

    pub fn to_json(&self) -> serde_json::Value {
        match self {
            Value::Bool(v) => serde_json::Value::Bool(*v),
            Value::I32(v) => serde_json::json!(*v),
            Value::U32(v) => serde_json::json!(*v),
            Value::I64(v) => serde_json::json!(*v),
            Value::U64(v) => serde_json::json!(*v),
            Value::F32(v) => serde_json::json!(*v),
            Value::Str(v) => serde_json::Value::String(v.clone()),
            Value::List(v) => serde_json::Value::Array(v.iter().map(|x| x.to_json()).collect()),
            Value::Key(v) => serde_json::json!(*v),
            Value::I16(v) => serde_json::json!(*v),
            Value::U16(v) => serde_json::json!(*v),
            Value::U8(v) => serde_json::json!(*v),
            Value::Null => serde_json::Value::Null,
        }
    }
}

/// DAT64 파서
pub struct Dat64Parser {
    data: Vec<u8>,
    row_count: u32,
    variable_data_start: usize,
}

impl Dat64Parser {
    /// DAT64 파일 로드
    pub fn load(data: Vec<u8>) -> Result<Self, String> {
        if data.len() < 4 {
            return Err("데이터가 너무 짧음 (최소 4바이트)".into());
        }

        let row_count = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
        let variable_data_start = find_marker(&data)?;

        Ok(Self {
            data,
            row_count,
            variable_data_start,
        })
    }

    pub fn row_count(&self) -> u32 {
        self.row_count
    }

    /// 스키마 기반으로 전체 테이블 파싱
    pub fn parse_table(&self, schema: &TableSchema) -> Result<Vec<HashMap<String, Value>>, String> {
        let row_size = schema.row_size();
        let mut rows = Vec::with_capacity(self.row_count as usize);

        for row_idx in 0..self.row_count as usize {
            let row_offset = 4 + (row_idx * row_size);
            let mut row = HashMap::new();
            let mut field_offset = row_offset;

            for field in &schema.fields {
                let value = self.read_field(field_offset, &field.field_type)?;
                row.insert(field.name.clone(), value);
                field_offset += field.field_type.size();
            }

            rows.push(row);
        }

        Ok(rows)
    }

    /// 특정 오프셋에서 필드 값 읽기
    fn read_field(&self, offset: usize, field_type: &FieldType) -> Result<Value, String> {
        if offset + field_type.size() > self.data.len() {
            return Ok(Value::Null);
        }

        let d = &self.data;
        Ok(match field_type {
            FieldType::Bool => Value::Bool(d[offset] != 0),
            FieldType::U8 => Value::U8(d[offset]),
            FieldType::I16 => Value::I16(i16::from_le_bytes([d[offset], d[offset + 1]])),
            FieldType::U16 => Value::U16(u16::from_le_bytes([d[offset], d[offset + 1]])),
            FieldType::I32 => Value::I32(i32::from_le_bytes(d[offset..offset + 4].try_into().unwrap())),
            FieldType::U32 => Value::U32(u32::from_le_bytes(d[offset..offset + 4].try_into().unwrap())),
            FieldType::I64 => Value::I64(i64::from_le_bytes(d[offset..offset + 8].try_into().unwrap())),
            FieldType::U64 => Value::U64(u64::from_le_bytes(d[offset..offset + 8].try_into().unwrap())),
            FieldType::F32 => Value::F32(f32::from_le_bytes(d[offset..offset + 4].try_into().unwrap())),
            FieldType::Str => {
                let str_offset = i64::from_le_bytes(d[offset..offset + 8].try_into().unwrap());
                if str_offset < 0 {
                    Value::Null
                } else {
                    Value::Str(self.read_string(str_offset as usize))
                }
            }
            FieldType::Key => {
                // foreignrow: row_index (i64) + reserved (i64, usually 0xFEFEFEFEFEFEFEFE)
                let key = i64::from_le_bytes(d[offset..offset + 8].try_into().unwrap());
                // skip reserved 8 bytes
                Value::Key(key)
            }
            FieldType::List => {
                let count = i64::from_le_bytes(d[offset..offset + 8].try_into().unwrap());
                let list_offset = i64::from_le_bytes(d[offset + 8..offset + 16].try_into().unwrap());
                if count <= 0 {
                    Value::List(vec![])
                } else {
                    // 리스트 요소 타입은 컨텍스트 필요 — 기본 i64로 처리
                    let abs_offset = self.variable_data_start + list_offset as usize;
                    let mut items = Vec::new();
                    for i in 0..count as usize {
                        let item_offset = abs_offset + i * 8;
                        if item_offset + 8 <= self.data.len() {
                            let val = i64::from_le_bytes(
                                self.data[item_offset..item_offset + 8].try_into().unwrap(),
                            );
                            items.push(Value::I64(val));
                        }
                    }
                    Value::List(items)
                }
            }
        })
    }

    /// 가변 데이터 섹션에서 UTF-16LE 문자열 읽기
    fn read_string(&self, relative_offset: usize) -> String {
        let abs_offset = self.variable_data_start + relative_offset;
        if abs_offset >= self.data.len() {
            return String::new();
        }

        let mut end = abs_offset;
        while end + 1 < self.data.len() {
            if self.data[end] == 0 && self.data[end + 1] == 0 {
                break;
            }
            end += 2;
        }

        let bytes: Vec<u16> = self.data[abs_offset..end]
            .chunks_exact(2)
            .map(|c| u16::from_le_bytes([c[0], c[1]]))
            .collect();

        String::from_utf16_lossy(&bytes)
    }

    /// 고정 데이터 크기 (행 크기 추정용)
    pub fn fixed_data_size(&self) -> usize {
        if self.variable_data_start > 12 {
            self.variable_data_start - 4 - 8 // row_count(4) 빼고, marker(8) 빼기
        } else {
            0
        }
    }

    /// 행 크기 추정 (row_count > 0일 때)
    pub fn estimated_row_size(&self) -> usize {
        if self.row_count > 0 {
            self.fixed_data_size() / self.row_count as usize
        } else {
            0
        }
    }
}

/// 0xBBBBBBBBBBBBBBBB 마커 찾기
fn find_marker(data: &[u8]) -> Result<usize, String> {
    for i in 4..data.len().saturating_sub(7) {
        if data[i..i + 8] == MARKER {
            return Ok(i + 8); // 마커 다음부터가 가변 데이터
        }
    }
    // 마커 없으면 전체가 고정 데이터
    Ok(data.len())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_test_dat64() -> Vec<u8> {
        let mut data = Vec::new();
        // row_count = 2
        data.extend_from_slice(&2u32.to_le_bytes());
        // row 0: bool=true(1), i32=42(4)  = 5 bytes
        data.push(1); // bool true
        data.extend_from_slice(&42i32.to_le_bytes());
        // row 1: bool=false(1), i32=100(4) = 5 bytes
        data.push(0); // bool false
        data.extend_from_slice(&100i32.to_le_bytes());
        // marker
        data.extend_from_slice(&MARKER);
        // variable data (empty)
        data
    }

    #[test]
    fn test_load_and_row_count() {
        let data = make_test_dat64();
        let parser = Dat64Parser::load(data).unwrap();
        assert_eq!(parser.row_count(), 2);
    }

    #[test]
    fn test_estimated_row_size() {
        let data = make_test_dat64();
        let parser = Dat64Parser::load(data).unwrap();
        assert_eq!(parser.estimated_row_size(), 5); // bool(1) + i32(4)
    }

    #[test]
    fn test_parse_table() {
        let data = make_test_dat64();
        let parser = Dat64Parser::load(data).unwrap();

        let schema = TableSchema {
            name: "Test".into(),
            fields: vec![
                FieldDef { name: "flag".into(), field_type: FieldType::Bool },
                FieldDef { name: "value".into(), field_type: FieldType::I32 },
            ],
        };

        let rows = parser.parse_table(&schema).unwrap();
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0]["flag"].as_bool(), Some(true));
        assert_eq!(rows[0]["value"].as_i64(), Some(42));
        assert_eq!(rows[1]["flag"].as_bool(), Some(false));
        assert_eq!(rows[1]["value"].as_i64(), Some(100));
    }

    #[test]
    fn test_string_parsing() {
        let mut data = Vec::new();
        // row_count = 1
        data.extend_from_slice(&1u32.to_le_bytes());
        // row 0: string offset = 0 (8 bytes)
        data.extend_from_slice(&0i64.to_le_bytes());
        // marker
        data.extend_from_slice(&MARKER);
        // variable data: UTF-16LE "Hello" + null terminator
        for c in "Hello".encode_utf16() {
            data.extend_from_slice(&c.to_le_bytes());
        }
        data.extend_from_slice(&[0, 0]); // null terminator

        let parser = Dat64Parser::load(data).unwrap();
        let schema = TableSchema {
            name: "Test".into(),
            fields: vec![
                FieldDef { name: "name".into(), field_type: FieldType::Str },
            ],
        };

        let rows = parser.parse_table(&schema).unwrap();
        assert_eq!(rows[0]["name"].as_str(), Some("Hello"));
    }

    #[test]
    fn test_load_too_short() {
        let result = Dat64Parser::load(vec![0, 0]);
        assert!(result.is_err());
    }
}
