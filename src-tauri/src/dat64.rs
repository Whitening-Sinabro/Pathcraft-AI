//! POE DAT64 바이너리 파일 파서
//!
//! DAT64 포맷:
//! - [0..4]: row_count (u32 LE)
//! - [4..marker]: 고정 데이터 (row_count × row_size 바이트)
//! - [marker]: 0xBBBBBBBBBBBBBBBB (8바이트)
//! - [marker+8..EOF]: 가변 데이터 (UTF-16LE 문자열, 리스트)

use std::collections::HashMap;

const MARKER: [u8; 8] = [0xBB; 8];

/// List 요소 수 상한 — schema 불일치 시 count 가 garbage (수십억) 이면 파싱 hang + OOM.
/// POE 실 데이터 중 단일 List 가 10000 항목 넘기는 경우는 사실상 없음 (가장 긴 tag list 도 수백 수준).
/// count 가 이 값 초과거나 물리 용량 초과 → **가짜 값으로 판단 후 빈 리스트 반환** (cap push 아님).
/// 이유: 잘못된 schema 해석으로 매 row 마다 1만 entries 쌓으면 12MB file 파싱에 수십 GB 메모리 소비.
const MAX_LIST_ITEMS: usize = 10_000;

/// UTF-16LE 문자열 최대 길이 (u16 기준). garbage offset 으로 EOF 까지 scan 방지.
/// POE 최장 문자열 (설명문) 도 1KB 를 넘지 않음. 여유 두고 4096.
const MAX_STR_U16: usize = 4096;

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
    Row,      // 8 bytes (row/rid: row_index i64, same-table reference)
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
            FieldType::I64 | FieldType::U64 | FieldType::Str | FieldType::Row => 8,
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
    /// POE2 schema 의 `interval: true` — i32 가 (min, max) i32 pair 로 저장 → 8B.
    /// pypoe schema 컨벤션. POE1 에서는 사용 안 함 (validFor=2 테이블 전용).
    pub interval: bool,
    /// `field_type == List` 일 때 element 의 base type.
    /// foreignrow array → 16B per element (rowid_lo_8B, reserved_hi_8B). emit Value::Key.
    /// i32/enumrow array → 4B. string array → 8B. f32 array → 4B. bool array → 1B.
    /// None 이면 fallback 으로 8B i64 (legacy / unknown).
    pub element_type: Option<FieldType>,
}

impl FieldDef {
    /// 행 안에서 이 필드가 차지하는 byte 수.
    /// interval 컬럼은 base type 의 2배 (min/max pair).
    pub fn size_in_row(&self) -> usize {
        let base = self.field_type.size();
        if self.interval { base * 2 } else { base }
    }
}

/// 테이블 스키마
#[derive(Debug, Clone)]
pub struct TableSchema {
    pub name: String,
    pub fields: Vec<FieldDef>,
}

impl TableSchema {
    pub fn row_size(&self) -> usize {
        self.fields.iter().map(|f| f.size_in_row()).sum()
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
    ///
    /// 스키마 행 크기와 실제 행 크기가 다르면:
    /// - 스키마 > 실제: 실제 크기에 맞는 필드만 파싱 (초과 컬럼 무시)
    /// - 스키마 < 실제: 스키마 필드만 파싱 (나머지 바이트 무시)
    pub fn parse_table(&self, schema: &TableSchema) -> Result<Vec<HashMap<String, Value>>, String> {
        let schema_row_size = schema.row_size();
        let actual_row_size = self.estimated_row_size();

        // 실제 행 크기 기준으로 파싱
        let row_size = if actual_row_size > 0 { actual_row_size } else { schema_row_size };

        // 스키마 필드 중 실제 행 크기에 맞는 것만 사용
        let usable_fields: Vec<&FieldDef> = if schema_row_size != row_size && actual_row_size > 0 {
            let mut fields = Vec::new();
            let mut offset = 0;
            for field in &schema.fields {
                if offset + field.size_in_row() > actual_row_size {
                    break;
                }
                fields.push(field);
                offset += field.size_in_row();
            }
            log::warn!(
                "스키마/데이터 행 크기 불일치: schema={}B, actual={}B — {} / {} 필드 사용",
                schema_row_size, actual_row_size, fields.len(), schema.fields.len()
            );
            fields
        } else {
            schema.fields.iter().collect()
        };

        let mut rows = Vec::with_capacity(self.row_count as usize);

        for row_idx in 0..self.row_count as usize {
            let row_offset = 4 + (row_idx * row_size);
            let mut row = HashMap::new();
            let mut field_offset = row_offset;

            for field in &usable_fields {
                let value = if field.interval {
                    self.read_interval(field_offset, &field.field_type)?
                } else if matches!(field.field_type, FieldType::List) {
                    self.read_list_typed(field_offset, field.element_type.as_ref())?
                } else {
                    self.read_field(field_offset, &field.field_type)?
                };
                row.insert(field.name.clone(), value);
                field_offset += field.size_in_row();
            }

            rows.push(row);
        }

        Ok(rows)
    }

    /// element type 인지를 가진 List 파싱.
    /// foreignrow array (16B per element): low 8B = rowid → Value::Key.
    /// 기타 base type: type.size() per element. Str array 는 offset → 문자열 resolve.
    /// `element_type` 가 None 이면 legacy 8B i64 fallback (read_field 의 List branch 사용).
    fn read_list_typed(&self, offset: usize, element_type: Option<&FieldType>) -> Result<Value, String> {
        if offset + 16 > self.data.len() {
            return Ok(Value::List(vec![]));
        }
        let count = i64::from_le_bytes(self.data[offset..offset + 8].try_into().unwrap());
        let list_offset = i64::from_le_bytes(self.data[offset + 8..offset + 16].try_into().unwrap());

        if count <= 0 {
            return Ok(Value::List(vec![]));
        }
        let count_usize = count as usize;
        if count_usize > MAX_LIST_ITEMS {
            return Ok(Value::List(vec![]));
        }

        let elem_type = match element_type {
            Some(t) => *t,
            None => {
                // legacy fallback — 8B i64 stride
                return self.read_field(offset, &FieldType::List);
            }
        };
        // foreignrow array element 는 16B (low 8B rowid + high 8B reserved). 그 외는 base type size.
        let elem_size = match elem_type {
            FieldType::Key => 16,
            other => other.size(),
        };
        let abs_offset = self.variable_data_start.saturating_add(list_offset as usize);
        let bytes_remaining = self.data.len().saturating_sub(abs_offset);
        let plausible_items = bytes_remaining / elem_size.max(1);
        if count_usize > plausible_items {
            return Ok(Value::List(vec![]));
        }

        let mut items = Vec::with_capacity(count_usize);
        for i in 0..count_usize {
            let item_offset = abs_offset + i * elem_size;
            if item_offset + elem_size > self.data.len() {
                break;
            }
            let v = match elem_type {
                FieldType::Key => {
                    // foreignrow array: rowid 는 element 의 low 8B 슬롯 (POE 0.4.x 실측).
                    let rid = i64::from_le_bytes(
                        self.data[item_offset..item_offset + 8].try_into().unwrap(),
                    );
                    Value::Key(rid)
                }
                FieldType::Str => {
                    let str_off = i64::from_le_bytes(
                        self.data[item_offset..item_offset + 8].try_into().unwrap(),
                    );
                    if str_off < 0 {
                        Value::Null
                    } else {
                        Value::Str(self.read_string(str_off as usize))
                    }
                }
                FieldType::Bool => Value::Bool(self.data[item_offset] != 0),
                FieldType::U8 => Value::U8(self.data[item_offset]),
                FieldType::I16 => Value::I16(i16::from_le_bytes(
                    self.data[item_offset..item_offset + 2].try_into().unwrap(),
                )),
                FieldType::U16 => Value::U16(u16::from_le_bytes(
                    self.data[item_offset..item_offset + 2].try_into().unwrap(),
                )),
                FieldType::I32 => Value::I32(i32::from_le_bytes(
                    self.data[item_offset..item_offset + 4].try_into().unwrap(),
                )),
                FieldType::U32 => Value::U32(u32::from_le_bytes(
                    self.data[item_offset..item_offset + 4].try_into().unwrap(),
                )),
                FieldType::F32 => Value::F32(f32::from_le_bytes(
                    self.data[item_offset..item_offset + 4].try_into().unwrap(),
                )),
                FieldType::I64 => Value::I64(i64::from_le_bytes(
                    self.data[item_offset..item_offset + 8].try_into().unwrap(),
                )),
                FieldType::U64 => Value::U64(u64::from_le_bytes(
                    self.data[item_offset..item_offset + 8].try_into().unwrap(),
                )),
                FieldType::Row => {
                    let rid = i64::from_le_bytes(
                        self.data[item_offset..item_offset + 8].try_into().unwrap(),
                    );
                    Value::Key(rid)
                }
                FieldType::List => {
                    // List of List 은 schema 미지원 — fallback i64.
                    Value::I64(i64::from_le_bytes(
                        self.data[item_offset..item_offset + 8].try_into().unwrap(),
                    ))
                }
            };
            items.push(v);
        }
        Ok(Value::List(items))
    }

    /// interval 필드 (min, max) pair 읽기 — 결과는 `Value::List([min, max])` 형태로 emit.
    /// JSON 직렬화 시 `[min, max]` 배열로 출력됨.
    /// POE2 schema 의 `interval: true` 컬럼 (Mods.Stat*Value 등) 전용.
    fn read_interval(&self, offset: usize, field_type: &FieldType) -> Result<Value, String> {
        let base = field_type.size();
        if offset + base * 2 > self.data.len() {
            return Ok(Value::Null);
        }
        let lo = self.read_field(offset, field_type)?;
        let hi = self.read_field(offset + base, field_type)?;
        Ok(Value::List(vec![lo, hi]))
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
            FieldType::Row => {
                // row/rid: row_index (i64) — 8 bytes only, no reserved padding
                let key = i64::from_le_bytes(d[offset..offset + 8].try_into().unwrap());
                Value::Key(key)
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
                    return Ok(Value::List(vec![]));
                }

                let count_usize = count as usize;
                let abs_offset = self.variable_data_start.saturating_add(list_offset as usize);

                // 물리 용량 초과 (count * 8 > 남은 바이트) → garbage 판정, 빈 리스트.
                // 단일 row × 수만 컬럼이 이 경로 타면 GB 단위 메모리 폭증 방지.
                let bytes_remaining = self.data.len().saturating_sub(abs_offset);
                let plausible_items = bytes_remaining / 8;
                if count_usize > plausible_items {
                    return Ok(Value::List(vec![]));
                }

                // 상한 초과 → garbage 의심, 빈 리스트. POE 실 list 는 수백 수준.
                if count_usize > MAX_LIST_ITEMS {
                    return Ok(Value::List(vec![]));
                }

                let mut items = Vec::with_capacity(count_usize);
                for i in 0..count_usize {
                    let item_offset = abs_offset + i * 8;
                    if item_offset + 8 > self.data.len() {
                        break;
                    }
                    let val = i64::from_le_bytes(
                        self.data[item_offset..item_offset + 8].try_into().unwrap(),
                    );
                    items.push(Value::I64(val));
                }
                Value::List(items)
            }
        })
    }

    /// 가변 데이터 섹션에서 UTF-16LE 문자열 읽기.
    /// garbage offset 으로 null terminator 없이 EOF 까지 scan 하는 것을 방지하기 위해
    /// MAX_STR_U16 (u16 단위) 길이로 상한 두고 중단.
    fn read_string(&self, relative_offset: usize) -> String {
        let abs_offset = self.variable_data_start + relative_offset;
        if abs_offset >= self.data.len() {
            return String::new();
        }

        let max_end = self
            .data
            .len()
            .min(abs_offset + MAX_STR_U16 * 2);

        let mut end = abs_offset;
        while end + 1 < max_end {
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
        if self.variable_data_start > 4 {
            self.variable_data_start - 4 // row_count(4)만 빼기. marker는 가변 데이터에 포함.
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
///
/// 마커 위치 = 가변 데이터 섹션의 시작.
/// 문자열 오프셋은 마커 위치 기준 (마커 8바이트가 오프셋 0-7을 차지).
fn find_marker(data: &[u8]) -> Result<usize, String> {
    for i in 4..data.len().saturating_sub(7) {
        if data[i..i + 8] == MARKER {
            return Ok(i); // 마커 위치 = 가변 데이터 섹션 시작
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
                FieldDef { name: "flag".into(), field_type: FieldType::Bool, interval: false, element_type: None },
                FieldDef { name: "value".into(), field_type: FieldType::I32, interval: false, element_type: None },
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
        // row 0: string offset = 8 (마커 8바이트 건너뜀)
        data.extend_from_slice(&8i64.to_le_bytes());
        // marker (가변 데이터 섹션의 오프셋 0-7)
        data.extend_from_slice(&MARKER);
        // variable data: UTF-16LE "Hello" + null terminator (오프셋 8부터)
        for c in "Hello".encode_utf16() {
            data.extend_from_slice(&c.to_le_bytes());
        }
        data.extend_from_slice(&[0, 0]); // null terminator

        let parser = Dat64Parser::load(data).unwrap();
        let schema = TableSchema {
            name: "Test".into(),
            fields: vec![
                FieldDef { name: "name".into(), field_type: FieldType::Str, interval: false, element_type: None },
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

    /// pathological List count (schema 불일치 시 garbage 거대값) 에도 hang / OOM 없어야 함.
    /// 행에 count=10^9, offset=0 으로 된 List 를 넣고 파싱. garbage 판정 → 빈 리스트 즉시 반환.
    #[test]
    fn test_list_garbage_count_does_not_hang() {
        let mut data = Vec::new();
        // row_count = 1
        data.extend_from_slice(&1u32.to_le_bytes());
        // row 0: List count = 10^9 (garbage), list_offset = 0
        data.extend_from_slice(&1_000_000_000i64.to_le_bytes());
        data.extend_from_slice(&0i64.to_le_bytes());
        // marker
        data.extend_from_slice(&MARKER);
        // variable data 넉넉히 (8B × 100) — 일부는 read 가능하지만 전체 10^9 는 절대 아님
        for _ in 0..100 {
            data.extend_from_slice(&0i64.to_le_bytes());
        }

        let parser = Dat64Parser::load(data).unwrap();
        let schema = TableSchema {
            name: "Test".into(),
            fields: vec![FieldDef {
                name: "badlist".into(),
                field_type: FieldType::List,
                interval: false,
                element_type: None,
            }],
        };

        // 핵심: 실시간 hang 없이 return. garbage count (10^9) 는 물리 용량 초과 → 빈 리스트.
        let start = std::time::Instant::now();
        let rows = parser.parse_table(&schema).unwrap();
        let elapsed = start.elapsed();
        assert!(
            elapsed.as_secs() < 2,
            "List garbage count 파싱이 2초 초과 — 방어 로직 미동작: {:?}",
            elapsed
        );
        assert_eq!(rows.len(), 1);
        // garbage → 빈 리스트 (MAX_LIST_ITEMS 초과 + 물리 용량 초과 둘 중 하나로 reject)
        match &rows[0]["badlist"] {
            Value::List(items) => assert!(
                items.is_empty(),
                "garbage List 가 빈 리스트로 처리 안 됨: {} items",
                items.len()
            ),
            other => panic!("List 타입 아님: {:?}", other),
        }
    }

    /// pathological string offset (garbage) 으로 EOF 까지 scan 하지 않아야 함.
    /// 마커 뒤로 null terminator 없이 non-null bytes 채운 뒤 read_string 호출.
    /// MAX_STR_U16 cap 으로 빠르게 종료.
    #[test]
    fn test_string_garbage_offset_caps_at_max_len() {
        let mut data = Vec::new();
        // row_count = 1
        data.extend_from_slice(&1u32.to_le_bytes());
        // row 0: str offset = 0 (가변 데이터 시작부터)
        data.extend_from_slice(&0i64.to_le_bytes());
        // marker
        data.extend_from_slice(&MARKER);
        // variable data: 10000 non-null u16 chars (no null terminator)
        for _ in 0..10_000 {
            data.extend_from_slice(&0x0041u16.to_le_bytes()); // 'A'
        }

        let parser = Dat64Parser::load(data).unwrap();
        let schema = TableSchema {
            name: "Test".into(),
            fields: vec![FieldDef {
                name: "name".into(),
                field_type: FieldType::Str,
                interval: false,
                element_type: None,
            }],
        };

        let rows = parser.parse_table(&schema).unwrap();
        let s = rows[0]["name"].as_str().unwrap();
        // MAX_STR_U16=4096 u16 chars cap. 실 char count (BMP 기준) 가 cap 이하여야.
        let char_count = s.chars().count();
        assert!(
            char_count <= MAX_STR_U16,
            "문자열 char count cap 미동작: {} chars",
            char_count
        );
    }
}
