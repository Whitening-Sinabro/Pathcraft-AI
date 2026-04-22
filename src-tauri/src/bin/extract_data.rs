//! POE 게임 데이터 추출 CLI
//!
//! 사용법:
//!   cargo run --bin extract_data                          # POE1 자동탐지
//!   cargo run --bin extract_data -- "D:\POE"              # POE1 경로 지정
//!   cargo run --bin extract_data -- --json                # POE1 + JSON 변환
//!   cargo run --bin extract_data -- --game poe2           # POE2 자동탐지
//!   cargo run --bin extract_data -- --game poe2 --json    # POE2 + JSON
//!   cargo run --bin extract_data -- --game poe2 --json --reuse-datc64
//!     → data/game_data_poe2/*.datc64 재사용, GGPK 로드 skip, schema+JSON 만 재생성
//!
//! POE 설치 경로를 자동 탐지하거나, 인자로 직접 지정.
//! .datc64 파일을 추출하고 스키마 기반 JSON 변환까지 수행.
//!
//! --game 플래그 (POE2 확장, D0):
//! - poe1 (기본): data/game_data/ 에 출력, SchemaStore::load_for_game(Poe1) 필터
//! - poe2: data/game_data_poe2/ 에 출력, SchemaStore::load_for_game(Poe2) 필터
//!   drift 2건 (Mods +24B / SkillGems +32B) 은 schema_poe2_override.json 로 보정 (2026-04-22).
//!
//! --reuse-datc64 플래그 (검증 사이클 단축):
//! - 기존 .datc64 파일이 output_dir 에 있다고 가정. GGPK/Oodle/BundleIndex 로드 생략.
//! - --json 과 조합 시 schema 적용 + JSON 만 재생성. drift override 수정 → 재검증 루프에 적합.
//! - 원본 .datc64 는 git clean 대상이 아니므로 로컬 cache 로 활용.

use std::path::{Path, PathBuf};

use app_lib::bundle_index::BundleIndex;
use app_lib::dat64::Dat64Parser;
use app_lib::oodle::OodleLib;
use app_lib::schema::{Game, SchemaStore};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum CliGame {
    Poe1,
    Poe2,
}

impl CliGame {
    fn parse(s: &str) -> Result<Self, String> {
        match s.to_ascii_lowercase().as_str() {
            "poe1" | "1" => Ok(CliGame::Poe1),
            "poe2" | "2" => Ok(CliGame::Poe2),
            other => Err(format!("알 수 없는 --game 값: '{}'. 허용: poe1|poe2", other)),
        }
    }

    fn as_schema_game(self) -> Game {
        match self {
            CliGame::Poe1 => Game::Poe1,
            CliGame::Poe2 => Game::Poe2,
        }
    }

    fn output_subdir(self) -> &'static str {
        match self {
            CliGame::Poe1 => "game_data",
            CliGame::Poe2 => "game_data_poe2",
        }
    }

    fn label(self) -> &'static str {
        match self {
            CliGame::Poe1 => "POE1",
            CliGame::Poe2 => "POE2",
        }
    }

    /// POE1 TARGETS (`Data/X.datc64`) 를 게임별 실제 번들 경로로 변환.
    ///
    /// POE2 는 `data/balance/<lowercase>.datc64` 레이아웃 (probe_poe2_schema.rs 확정).
    /// POE1 은 `Data/X.datc64` 원본 유지.
    fn resolve_table_path(self, target: &str) -> String {
        match self {
            CliGame::Poe1 => target.to_string(),
            CliGame::Poe2 => {
                let filename = target.rsplit('/').next().unwrap_or(target).to_lowercase();
                format!("data/balance/{}", filename)
            }
        }
    }
}

/// 추출 대상 테이블.
///
/// 확장 근거: _analysis/ggpk_extraction_completeness_audit.md (Phase F0, 2026-04-17).
/// schema.min.json 전체 POE1 921 테이블 중 feature 의존도 기준 우선 추출.
///
/// - Tier 0 (기존): build parsing / L7-L8 필터 기본 인프라
/// - Tier 1 (Critical): Tags/Mods/Characters 부재로 휴리스틱 대체 중이던 것
/// - Tier 2 (다중 feature 활용): GemTags/ArmourTypes/Scarabs 등
const TARGETS: &[&str] = &[
    // Tier 0 — 기존 (Phase B/D/E 의존)
    "Data/ActiveSkills.datc64",
    "Data/BaseItemTypes.datc64",
    "Data/Maps.datc64",
    "Data/PassiveSkills.datc64",
    "Data/QuestRewards.datc64",
    "Data/SkillGems.datc64",
    "Data/UniqueStashLayout.datc64",
    // Tier 1 — Critical (F0 감사 Critical 1/2/3 해결)
    "Data/Tags.datc64",          // load_ggpk_items TagsKeys 해결
    "Data/Characters.datc64",    // 클래스 start node 자동 매핑 (POE2 드리프트 없음, 우선 처리)
    "Data/Ascendancy.datc64",    // 어센던시 자동 매핑 (POE2 드리프트 없음, 우선 처리)
    // Tier 2 — 다중 feature 활용
    "Data/GemTags.datc64",       // Phase E damage_type 대체 후보
    "Data/ArmourTypes.datc64",   // Phase D BaseItemTypes.Id 휴리스틱 업그레이드
    "Data/Scarabs.datc64",       // GGPKItems.scarabs_* 대체
    "Data/ScarabTypes.datc64",
    "Data/Essences.datc64",      // GGPKItems.essence_* 대체
    "Data/Flasks.datc64",
    // Words: UniqueStashLayout.WordsKey 참조용 (POE2 uniques 이름 매핑)
    "Data/Words.datc64",
    // POE2 Mods 는 schema 중간 필드 misinterpret 가능성 — 순서 맨 끝으로 이동.
    // 2026-04-22 관찰: drift override 적용 후에도 parse_table 25분+ CPU 소모 (POE2 backlog).
    // ModType/ModFamily 는 drift 없음 — Mods 앞으로 이동해 JSON 생성 보장.
    "Data/ModType.datc64",       // Mods 보조 (drift 없음)
    "Data/ModFamily.datc64",     // Mods 보조 (drift 없음)
    "Data/Mods.datc64",          // HasExplicitMod 검증. POE2 parse_table 느림 — 맨 마지막.
];

fn main() {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .target(env_logger::Target::Stderr)
        .init();

    let args: Vec<String> = std::env::args().skip(1).collect();
    let json_mode = args.iter().any(|a| a == "--json");
    let reuse_datc64 = args.iter().any(|a| a == "--reuse-datc64");

    // --game poe1|poe2 파싱. 공백 형식 (--game poe2) 및 등호 형식 (--game=poe2) 둘 다 지원.
    let game = match parse_game_arg(&args) {
        Ok(g) => g,
        Err(e) => {
            eprintln!("[오류] {}", e);
            std::process::exit(1);
        }
    };

    // custom_path: --game / --json / --reuse-datc64 와 그 다음 값을 제외한 첫 positional 인자
    let custom_path = positional_path_arg(&args);

    eprintln!("[게임] {}", game.label());

    // --reuse-datc64 모드: GGPK 로드 skip, 기존 .datc64 재사용
    if reuse_datc64 {
        run_reuse_mode(game, json_mode);
        return;
    }

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
        None => match detect_poe_path(game) {
            Some(p) => {
                eprintln!("[자동탐지] {}", p.display());
                p
            }
            None => {
                eprintln!("[오류] {} 설치 경로를 찾을 수 없습니다.", game.label());
                eprintln!("직접 지정: cargo run --bin extract_data -- --game {} \"C:\\경로\"",
                    if game == CliGame::Poe2 { "poe2" } else { "poe1" });
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

    // 4. 출력 디렉토리 — 게임별 분리
    let output_dir = project_data_dir(game);
    if let Err(e) = std::fs::create_dir_all(&output_dir) {
        eprintln!("[오류] 출력 디렉토리 생성 실패: {}", e);
        std::process::exit(1);
    }

    // 5. 스키마 로드 (JSON 변환용) — 게임별 validFor 필터링 적용
    let schema_store = if json_mode {
        eprintln!("[3/4] 스키마 로드 ({} validFor 필터)...", game.label());
        let schema_path = project_root().join("data").join("schema").join("schema.min.json");
        match SchemaStore::load_for_game(&schema_path, game.as_schema_game()) {
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
        // table_name: 스키마/출력파일명용 (원본 POE1 경로 기준 — 대소문자 보존)
        let table_name = target
            .rsplit('/')
            .next()
            .unwrap_or(target)
            .trim_end_matches(".datc64");

        // resolved: 실제 번들 내부 경로 (POE2는 data/balance/<lowercase>.datc64)
        let resolved = game.resolve_table_path(target);

        let file = match index.find_file(&resolved) {
            Some(f) => f.clone(),
            None => {
                eprintln!("  [-] {} — 파일 없음 ({})", table_name, resolved);
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

/// --reuse-datc64 모드 본체.
/// 기존 output_dir 의 .datc64 파일을 읽어 schema 적용 + JSON 변환만 수행.
/// GGPK/Oodle/BundleIndex 로드 단계를 건너뛰어 drift override 수정 → 재검증 루프 단축.
fn run_reuse_mode(game: CliGame, json_mode: bool) {
    let output_dir = project_data_dir(game);
    if !output_dir.exists() {
        eprintln!("[오류] 재사용 대상 디렉토리 없음: {}", output_dir.display());
        eprintln!("먼저 GGPK 에서 추출: cargo run --bin extract_data -- --game {}",
            if game == CliGame::Poe2 { "poe2" } else { "poe1" });
        std::process::exit(1);
    }

    let schema_store = if json_mode {
        eprintln!("[1/2] 스키마 로드 ({} validFor 필터 + drift override)...", game.label());
        let schema_path = project_root().join("data").join("schema").join("schema.min.json");
        match SchemaStore::load_for_game(&schema_path, game.as_schema_game()) {
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
        eprintln!("[1/2] 스키마 (--json 미사용, 재사용 모드에선 할 일 없음 — 종료)");
        return;
    };

    eprintln!("[2/2] .datc64 재사용 + JSON 재생성...");
    let mut success = 0;
    let mut failed = 0;

    for target in TARGETS {
        let table_name = target
            .rsplit('/')
            .next()
            .unwrap_or(target)
            .trim_end_matches(".datc64");

        let datc_path = output_dir.join(format!("{}.datc64", table_name));
        if !datc_path.exists() {
            eprintln!("  [-] {} — .datc64 없음 (skip)", table_name);
            failed += 1;
            continue;
        }

        let data = match std::fs::read(&datc_path) {
            Ok(d) => d,
            Err(e) => {
                eprintln!("  [-] {} — 읽기 실패: {}", table_name, e);
                failed += 1;
                continue;
            }
        };

        let row_info = match Dat64Parser::load(data.clone()) {
            Ok(parser) => format!("{} rows, {}B/row", parser.row_count(), parser.estimated_row_size()),
            Err(_) => "파싱 불가".into(),
        };
        eprintln!("  [+] {} — {}KB, {}", table_name, data.len() / 1024, row_info);

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
                                success += 1;
                            }
                        }
                        Err(e) => {
                            eprintln!("       JSON 변환 실패: {}", e);
                            failed += 1;
                        }
                    },
                    Err(e) => {
                        eprintln!("       파서 로드 실패: {}", e);
                        failed += 1;
                    }
                }
            } else {
                eprintln!("       스키마에 {} 없음 (JSON 생략)", table_name);
            }
        }
    }

    eprintln!("\n=== 재사용 완료 ===");
    eprintln!("JSON 성공: {}, 실패: {}", success, failed);
    eprintln!("출력: {}", output_dir.display());
}

/// --game 플래그 파싱 (--game <v> / --game=<v>). 없으면 Poe1 기본.
fn parse_game_arg(args: &[String]) -> Result<CliGame, String> {
    for (i, a) in args.iter().enumerate() {
        if let Some(rest) = a.strip_prefix("--game=") {
            return CliGame::parse(rest);
        }
        if a == "--game" {
            let v = args.get(i + 1).ok_or_else(|| "--game 뒤 값 누락".to_string())?;
            return CliGame::parse(v);
        }
    }
    Ok(CliGame::Poe1)
}

/// --game/--json 뒤에 붙은 값이 아닌 첫 positional 인자.
fn positional_path_arg(args: &[String]) -> Option<&String> {
    let mut skip_next = false;
    for a in args {
        if skip_next {
            skip_next = false;
            continue;
        }
        if a == "--game" {
            skip_next = true;
            continue;
        }
        if a.starts_with('-') {
            continue;
        }
        return Some(a);
    }
    None
}

/// POE 설치 경로 자동 탐지 (게임별 후보 경로)
fn detect_poe_path(game: CliGame) -> Option<PathBuf> {
    let candidates: &[&str] = match game {
        CliGame::Poe1 => &[
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
        ],
        CliGame::Poe2 => &[
            // Standalone (한국, Daum/Kakao 배포)
            r"C:\Daum Games\Path of Exile2",
            // Standalone (글로벌)
            r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile 2",
            r"C:\Program Files\Grinding Gear Games\Path of Exile 2",
            // Steam
            r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile 2",
            r"C:\Program Files\Steam\steamapps\common\Path of Exile 2",
            r"D:\Steam\steamapps\common\Path of Exile 2",
            r"D:\SteamLibrary\steamapps\common\Path of Exile 2",
            r"E:\SteamLibrary\steamapps\common\Path of Exile 2",
        ],
    };

    for path in candidates {
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

/// 추출 데이터 출력 디렉토리 (게임별 분리: game_data / game_data_poe2)
fn project_data_dir(game: CliGame) -> PathBuf {
    project_root().join("data").join(game.output_subdir())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_game_default_poe1() {
        let args: Vec<String> = vec!["--json".into()];
        assert_eq!(parse_game_arg(&args).unwrap(), CliGame::Poe1);
    }

    #[test]
    fn test_parse_game_space_form() {
        let args: Vec<String> = vec!["--game".into(), "poe2".into()];
        assert_eq!(parse_game_arg(&args).unwrap(), CliGame::Poe2);
    }

    #[test]
    fn test_parse_game_equals_form() {
        let args: Vec<String> = vec!["--game=poe2".into()];
        assert_eq!(parse_game_arg(&args).unwrap(), CliGame::Poe2);
    }

    #[test]
    fn test_parse_game_invalid() {
        let args: Vec<String> = vec!["--game".into(), "poe3".into()];
        assert!(parse_game_arg(&args).is_err());
    }

    #[test]
    fn test_parse_game_numeric() {
        let args: Vec<String> = vec!["--game".into(), "2".into()];
        assert_eq!(parse_game_arg(&args).unwrap(), CliGame::Poe2);
    }

    #[test]
    fn test_positional_path_skips_game_value() {
        let args: Vec<String> = vec![
            "--game".into(),
            "poe2".into(),
            "D:\\custom\\path".into(),
            "--json".into(),
        ];
        assert_eq!(positional_path_arg(&args), Some(&"D:\\custom\\path".to_string()));
    }

    #[test]
    fn test_positional_path_none() {
        let args: Vec<String> = vec!["--json".into(), "--game".into(), "poe1".into()];
        assert_eq!(positional_path_arg(&args), None);
    }

    #[test]
    fn test_output_subdir_per_game() {
        assert_eq!(CliGame::Poe1.output_subdir(), "game_data");
        assert_eq!(CliGame::Poe2.output_subdir(), "game_data_poe2");
    }
}
