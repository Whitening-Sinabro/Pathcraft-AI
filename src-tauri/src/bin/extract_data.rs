//! POE 게임 데이터 추출 CLI
//!
//! 사용법:
//!   cargo run --bin extract_data
//!   cargo run --bin extract_data -- "D:\POE"
//!   cargo run --bin extract_data -- --json
//!
//! POE 설치 경로를 자동 탐지하거나, 인자로 직접 지정.
//! .datc64 파일을 추출하고 스키마 기반 JSON 변환까지 수행.

use std::path::{Path, PathBuf};

use app_lib::bundle_index::BundleIndex;
use app_lib::dat64::Dat64Parser;
use app_lib::oodle::OodleLib;
use app_lib::schema::SchemaStore;

/// 추출 대상 테이블
const TARGETS: &[&str] = &[
    "Data/ActiveSkills.datc64",
    "Data/BaseItemTypes.datc64",
    "Data/Maps.datc64",
    "Data/PassiveSkills.datc64",
    "Data/QuestRewards.datc64",
    "Data/SkillGems.datc64",
    "Data/UniqueStashLayout.datc64",
];

fn main() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .target(env_logger::Target::Stderr)
        .init();

    let args: Vec<String> = std::env::args().skip(1).collect();
    let json_mode = args.iter().any(|a| a == "--json");
    let custom_path = args.iter().find(|a| !a.starts_with('-'));

    // 1. POE 경로 결정
    let poe_path = match custom_path {
        Some(p) => {
            let path = PathBuf::from(p);
            if !path.exists() {
                eprintln!("[오류] 지정 경로 없음: {}", path.display());
                std::process::exit(1);
            }
            path
        }
        None => match detect_poe_path() {
            Some(p) => {
                eprintln!("[자동탐지] {}", p.display());
                p
            }
            None => {
                eprintln!("[오류] POE 설치 경로를 찾을 수 없습니다.");
                eprintln!("직접 지정: cargo run --bin extract_data -- \"C:\\경로\\Path of Exile\"");
                std::process::exit(1);
            }
        },
    };

    // 2. Oodle DLL 로드
    eprintln!("[1/4] Oodle DLL 로드...");
    let oodle = match OodleLib::load(&poe_path) {
        Ok(o) => o,
        Err(e) => {
            eprintln!("[오류] {}", e);
            std::process::exit(1);
        }
    };

    // 3. Bundle Index 로드
    eprintln!("[2/4] Bundle Index 로드...");
    let mut index = match BundleIndex::load(&poe_path, &oodle) {
        Ok(idx) => idx,
        Err(e) => {
            eprintln!("[오류] {}", e);
            std::process::exit(1);
        }
    };
    eprintln!("       번들 {}, 파일 {}", index.bundles.len(), index.file_count());

    // 4. 출력 디렉토리
    let output_dir = project_data_dir();
    if let Err(e) = std::fs::create_dir_all(&output_dir) {
        eprintln!("[오류] 출력 디렉토리 생성 실패: {}", e);
        std::process::exit(1);
    }

    // 5. 스키마 로드 (JSON 변환용)
    let schema_store = if json_mode {
        eprintln!("[3/4] 스키마 로드...");
        let schema_path = project_root().join("data").join("schema").join("schema.min.json");
        match SchemaStore::load(&schema_path) {
            Ok(s) => {
                eprintln!("       테이블 {} 개", s.table_count());
                Some(s)
            }
            Err(e) => {
                eprintln!("[경고] 스키마 로드 실패 (JSON 변환 생략): {}", e);
                None
            }
        }
    } else {
        eprintln!("[3/4] 스키마 (--json 미사용, 스킵)");
        None
    };

    // 6. 추출
    eprintln!("[4/4] 데이터 추출...");
    let mut success = 0;
    let mut failed = 0;

    for target in TARGETS {
        let table_name = target
            .rsplit('/')
            .next()
            .unwrap_or(target)
            .trim_end_matches(".datc64");

        let file = match index.find_file(target) {
            Some(f) => f.clone(),
            None => {
                eprintln!("  [-] {} — 파일 없음", table_name);
                failed += 1;
                continue;
            }
        };

        match index.extract_file(&file, &oodle) {
            Ok(data) => {
                let datc_path = output_dir.join(format!("{}.datc64", table_name));
                if let Err(e) = std::fs::write(&datc_path, &data) {
                    eprintln!("  [-] {} — 저장 실패: {}", table_name, e);
                    failed += 1;
                    continue;
                }

                let row_info = match Dat64Parser::load(data.clone()) {
                    Ok(parser) => format!("{} rows, {}B/row", parser.row_count(), parser.estimated_row_size()),
                    Err(_) => "파싱 불가".into(),
                };

                eprintln!("  [+] {} — {}KB, {}", table_name, data.len() / 1024, row_info);

                // JSON 변환
                if let Some(ref store) = schema_store {
                    if let Some(schema) = store.get(table_name) {
                        match Dat64Parser::load(data) {
                            Ok(parser) => match parser.parse_table(schema) {
                                Ok(rows) => {
                                    let json_rows: Vec<serde_json::Value> = rows
                                        .iter()
                                        .map(|row| {
                                            let mut obj = serde_json::Map::new();
                                            for field in &schema.fields {
                                                if let Some(val) = row.get(&field.name) {
                                                    obj.insert(field.name.clone(), val.to_json());
                                                }
                                            }
                                            serde_json::Value::Object(obj)
                                        })
                                        .collect();

                                    let json_path = output_dir.join(format!("{}.json", table_name));
                                    let json_str = serde_json::to_string_pretty(&json_rows)
                                        .unwrap_or_else(|_| "[]".into());
                                    if let Err(e) = std::fs::write(&json_path, &json_str) {
                                        eprintln!("       JSON 저장 실패: {}", e);
                                    } else {
                                        eprintln!("       → {}.json ({} rows)", table_name, json_rows.len());
                                    }
                                }
                                Err(e) => eprintln!("       JSON 변환 실패: {}", e),
                            },
                            Err(e) => eprintln!("       파서 로드 실패: {}", e),
                        }
                    } else {
                        eprintln!("       스키마에 {} 없음 (JSON 생략)", table_name);
                    }
                }

                success += 1;
            }
            Err(e) => {
                eprintln!("  [-] {} — 추출 실패: {}", table_name, e);
                failed += 1;
            }
        }
    }

    index.clear_cache();

    eprintln!("\n=== 완료 ===");
    eprintln!("성공: {}/{}, 실패: {}", success, TARGETS.len(), failed);
    eprintln!("출력: {}", output_dir.display());
}

/// POE 설치 경로 자동 탐지
fn detect_poe_path() -> Option<PathBuf> {
    let candidates = [
        // Standalone (한국)
        r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile",
        // Standalone (글로벌)
        r"C:\Program Files\Grinding Gear Games\Path of Exile",
        // Steam 기본
        r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile",
        r"C:\Program Files\Steam\steamapps\common\Path of Exile",
        // Steam 추가 라이브러리
        r"D:\Steam\steamapps\common\Path of Exile",
        r"D:\SteamLibrary\steamapps\common\Path of Exile",
        r"E:\SteamLibrary\steamapps\common\Path of Exile",
    ];

    for path in &candidates {
        let p = Path::new(path);
        // Content.ggpk (Standalone) 또는 Bundles2/ (Steam) 존재 여부로 판별
        if p.join("Content.ggpk").exists() || p.join("Bundles2").is_dir() {
            return Some(p.to_path_buf());
        }
    }

    None
}

/// 프로젝트 루트 (Cargo.toml 기준)
fn project_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."))
}

/// 추출 데이터 출력 디렉토리
fn project_data_dir() -> PathBuf {
    project_root().join("data").join("game_data")
}
