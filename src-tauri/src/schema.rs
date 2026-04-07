//! POE DAT64 테이블 스키마 정의
//!
//! 커뮤니티 소스 (poedat, PyPoE) 기반으로 핵심 테이블 스키마 정의.
//! 패치마다 컬럼이 변경될 수 있으므로, 향후 외부 JSON 스키마 파일로 분리 예정.

use crate::dat64::{FieldDef, FieldType, TableSchema};

/// 핵심 테이블 스키마 목록
pub fn get_schemas() -> Vec<TableSchema> {
    vec![
        gems_schema(),
        skill_gems_schema(),
        base_item_types_schema(),
        maps_schema(),
        quest_rewards_schema(),
    ]
}

/// ActiveSkills.dat64 — 스킬 젬 기본 정보
fn gems_schema() -> TableSchema {
    TableSchema {
        name: "ActiveSkills".into(),
        fields: vec![
            FieldDef { name: "Id".into(), field_type: FieldType::Str },
            FieldDef { name: "DisplayedName".into(), field_type: FieldType::Str },
            FieldDef { name: "Description".into(), field_type: FieldType::Str },
            FieldDef { name: "ActiveSkillTargetTypes".into(), field_type: FieldType::List },
            FieldDef { name: "ActiveSkillTypes".into(), field_type: FieldType::List },
            FieldDef { name: "WeaponRestriction_ItemClassesKeys".into(), field_type: FieldType::List },
            FieldDef { name: "WebsiteDescription".into(), field_type: FieldType::Str },
            FieldDef { name: "WebsiteImage".into(), field_type: FieldType::Str },
            FieldDef { name: "Unknown0".into(), field_type: FieldType::Bool },
            FieldDef { name: "IconDDSFile".into(), field_type: FieldType::Str },
        ],
    }
}

/// SkillGems.dat64 — 스킬 젬 메타데이터
fn skill_gems_schema() -> TableSchema {
    TableSchema {
        name: "SkillGems".into(),
        fields: vec![
            FieldDef { name: "BaseItemTypesKey".into(), field_type: FieldType::Key },
            FieldDef { name: "GrantedEffectsKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Str".into(), field_type: FieldType::I32 },
            FieldDef { name: "Dex".into(), field_type: FieldType::I32 },
            FieldDef { name: "Int".into(), field_type: FieldType::I32 },
            FieldDef { name: "IsVaalGem".into(), field_type: FieldType::Bool },
        ],
    }
}

/// BaseItemTypes.dat64 — 기본 아이템 타입 (유니크 포함)
fn base_item_types_schema() -> TableSchema {
    TableSchema {
        name: "BaseItemTypes".into(),
        fields: vec![
            FieldDef { name: "Id".into(), field_type: FieldType::Str },
            FieldDef { name: "ItemClassesKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Width".into(), field_type: FieldType::I32 },
            FieldDef { name: "Height".into(), field_type: FieldType::I32 },
            FieldDef { name: "Name".into(), field_type: FieldType::Str },
            FieldDef { name: "InheritsFrom".into(), field_type: FieldType::Str },
            FieldDef { name: "DropLevel".into(), field_type: FieldType::I32 },
        ],
    }
}

/// Maps.dat64 — 맵 정보
fn maps_schema() -> TableSchema {
    TableSchema {
        name: "Maps".into(),
        fields: vec![
            FieldDef { name: "BaseItemTypesKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Regular_WorldAreasKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Unique_WorldAreasKey".into(), field_type: FieldType::Key },
            FieldDef { name: "MapSeriesKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Tier".into(), field_type: FieldType::I32 },
        ],
    }
}

/// QuestRewards.dat64 — 퀘스트 보상 (젬 보상 포함)
fn quest_rewards_schema() -> TableSchema {
    TableSchema {
        name: "QuestRewards".into(),
        fields: vec![
            FieldDef { name: "QuestKey".into(), field_type: FieldType::Key },
            FieldDef { name: "Unknown0".into(), field_type: FieldType::I32 },
            FieldDef { name: "CharactersKey".into(), field_type: FieldType::Key },
            FieldDef { name: "BaseItemTypesKey".into(), field_type: FieldType::Key },
            FieldDef { name: "ItemLevel".into(), field_type: FieldType::I32 },
            FieldDef { name: "RarityKey".into(), field_type: FieldType::I32 },
        ],
    }
}
