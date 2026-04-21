pub mod bundle;
pub mod bundle_index;
pub mod dat64;
pub mod ggpk;
pub mod oodle;
pub mod schema;

use schema::Game;
use std::process::{Child, Command};
use std::path::PathBuf;
use std::sync::{Mutex, OnceLock};

#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

/// 현재 실행 중인 coach subprocess handle. 사용자가 정지 버튼 누르면 kill.
/// 단일 데스크톱 앱 가정 — 동시에 coach는 1개만 돌음.
fn coach_child() -> &'static Mutex<Option<Child>> {
    static REG: OnceLock<Mutex<Option<Child>>> = OnceLock::new();
    REG.get_or_init(|| Mutex::new(None))
}

/// Windows에서 Python subprocess 호출 시 콘솔 창 표시 억제 flag.
/// CREATE_NO_WINDOW = 0x08000000 (WinAPI 상수).
#[cfg(target_os = "windows")]
const CREATE_NO_WINDOW: u32 = 0x08000000;

/// 플랫폼별로 Command 생성 + Windows는 콘솔 창 숨김.
fn new_python_cmd() -> Command {
    let mut cmd = Command::new("python");
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd
}

fn project_root() -> PathBuf {
    // TAURI_PROJECT_ROOT 환경변수 > exe 위치 조상 탐색 > CWD 조상 탐색
    if let Ok(root) = std::env::var("TAURI_PROJECT_ROOT") {
        return PathBuf::from(root);
    }

    // exe 조상 경로 모두 탐색 (target/release/app.exe → target → src-tauri → PROJECT_ROOT)
    if let Ok(exe) = std::env::current_exe() {
        for ancestor in exe.ancestors().skip(1) {
            if ancestor.join("python").is_dir() {
                return ancestor.to_path_buf();
            }
        }
    }

    // CWD 조상도 동일 방식으로 탐색 (개발 모드 fallback)
    if let Ok(cwd) = std::env::current_dir() {
        for ancestor in cwd.ancestors() {
            if ancestor.join("python").is_dir() {
                return ancestor.to_path_buf();
            }
        }
    }

    // 최후: CWD 자체
    std::env::current_dir().unwrap_or_default()
}

fn python_dir() -> PathBuf {
    project_root().join("python")
}

fn run_python(script: &str, args: &[&str]) -> Result<String, String> {
    let output = new_python_cmd()
        .arg(python_dir().join(script))
        .args(args)
        .env("PYTHONIOENCODING", "utf-8")
        .current_dir(project_root())
        .output()
        .map_err(|e| format!("Python 실행 실패: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        Err(format!("Python 에러: {}", stderr))
    }
}

/// 프론트엔드가 game 인자 생략 시 기본값 POE1. POE2 통합 전 후방 호환.
fn game_or_default(game: Option<Game>) -> Game {
    game.unwrap_or_default()
}

#[tauri::command]
async fn parse_pob(link: String, game: Option<Game>) -> Result<String, String> {
    // 블로킹 서브프로세스 → tokio blocking pool에서 실행 → UI 프리즈 방지
    let g = game_or_default(game);
    tauri::async_runtime::spawn_blocking(move || {
        run_python("pob_parser.py", &["--game", g.as_cli_flag(), &link])
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
async fn coach_build(
    build_json: String,
    model: Option<String>,
    game: Option<Game>,
) -> Result<String, String> {
    let g = game_or_default(game);
    tauri::async_runtime::spawn_blocking(move || {
        // 허용 모델 화이트리스트 — 임의 값 주입 차단 (subprocess 인자 인젝션 방지).
        let model_arg = match model.as_deref() {
            Some("claude-haiku-4-5-20251001") => Some("claude-haiku-4-5-20251001"),
            Some("claude-sonnet-4-6") => Some("claude-sonnet-4-6"),
            Some("claude-opus-4-7") => Some("claude-opus-4-7"),
            Some(other) => return Err(format!("허용되지 않은 모델: {}", other)),
            None => None,  // Python 기본값 사용
        };
        let mut cmd = new_python_cmd();
        cmd.arg(python_dir().join("build_coach.py"))
            .arg("-")
            .arg("--game").arg(g.as_cli_flag())
            .env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root())
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped());
        if let Some(m) = model_arg {
            cmd.arg("--model").arg(m);
        }
        let mut child = cmd.spawn()
            .map_err(|e| format!("Python 실행 실패: {}", e))?;

        use std::io::Write;
        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(build_json.as_bytes())
                .map_err(|e| format!("stdin 전달 실패: {}", e))?;
        }

        // stdout/stderr 수동 수집 — child 자체는 cancel을 위해 레지스트리로 이관 (wait_with_output은 child ownership을 소비하므로 사용 불가).
        // 중요: stdout/stderr를 **동시** 드레인해야 deadlock 방지 (build_coach.py는 stderr로 진행 로그를 계속 씀 — 파이프 버퍼 ~64KB 차면 Python 블록).
        let stdout_pipe = child.stdout.take();
        let stderr_pipe = child.stderr.take();

        // 기존 레지스트리 entry는 coach 중복 실행 가드 — 이전 것은 취소해 넘김.
        if let Ok(mut slot) = coach_child().lock() {
            if let Some(mut old) = slot.take() {
                let _ = old.kill();
                let _ = old.wait();
            }
            *slot = Some(child);
        }

        use std::io::Read;
        let stderr_handle = stderr_pipe.map(|mut p| {
            std::thread::spawn(move || {
                let mut buf = Vec::new();
                let _ = p.read_to_end(&mut buf);
                buf
            })
        });

        let mut stdout_buf = Vec::new();
        if let Some(mut p) = stdout_pipe {
            let _ = p.read_to_end(&mut stdout_buf);
        }

        let stderr_buf = stderr_handle
            .map(|h| h.join().unwrap_or_default())
            .unwrap_or_default();

        // 파이프가 닫혔으면 프로세스 종료 후 회수 — kill 여부 판별용 exit status 확보.
        let status = {
            let mut slot = coach_child().lock()
                .map_err(|e| format!("레지스트리 잠금 실패: {}", e))?;
            match slot.take() {
                Some(mut c) => c.wait().map_err(|e| format!("프로세스 대기 실패: {}", e))?,
                None => return Err("코치 취소됨".to_string()),  // cancel_coach가 이미 회수
            }
        };

        if status.success() {
            Ok(String::from_utf8_lossy(&stdout_buf).to_string())
        } else {
            let stderr = String::from_utf8_lossy(&stderr_buf).to_string();
            Err(format!("코치 에러: {}", stderr))
        }
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
fn cancel_coach() -> Result<bool, String> {
    let mut slot = coach_child().lock()
        .map_err(|e| format!("레지스트리 잠금 실패: {}", e))?;
    match slot.take() {
        Some(mut child) => {
            let _ = child.kill();
            let _ = child.wait();
            Ok(true)
        }
        None => Ok(false),  // 실행 중인 coach 없음
    }
}

#[tauri::command]
fn extract_game_data(poe_path: String, game: Option<Game>) -> Result<String, String> {
    let g = game_or_default(game);
    let poe_dir = std::path::Path::new(&poe_path);

    // 번들 파이프라인 시도
    let oodle = oodle::OodleLib::load(poe_dir)?;
    let mut index = bundle_index::BundleIndex::load(poe_dir, &oodle)?;

    // 게임별 출력 디렉터리 분리 (POE1: game_data / POE2: game_data_poe2)
    let output_subdir = match g {
        Game::Poe1 => "game_data",
        Game::Poe2 => "game_data_poe2",
    };
    let output_dir = project_root().join("data").join(output_subdir);
    std::fs::create_dir_all(&output_dir)
        .map_err(|e| format!("출력 디렉토리 생성 실패: {}", e))?;

    let target_tables = [
        "Data/ActiveSkills.datc64",
        "Data/SkillGems.datc64",
        "Data/BaseItemTypes.datc64",
        "Data/Maps.datc64",
        "Data/QuestRewards.datc64",
        "Data/PassiveSkills.datc64",
        "Data/UniqueStashLayout.datc64",
    ];

    let mut extracted = Vec::new();

    for target in &target_tables {
        match index.find_file(target) {
            Some(file) => {
                let file = file.clone();
                match index.extract_file(&file, &oodle) {
                    Ok(data) => {
                        let filename = target
                            .rsplit('/')
                            .next()
                            .unwrap_or(target);

                        let out_path = output_dir.join(filename);
                        std::fs::write(&out_path, &data)
                            .map_err(|e| format!("{} 저장 실패: {}", filename, e))?;

                        extracted.push(serde_json::json!({
                            "file": filename,
                            "size": data.len(),
                            "rows": dat64::Dat64Parser::load(data)
                                .map(|p| p.row_count())
                                .unwrap_or(0),
                        }));
                    }
                    Err(e) => {
                        log::warn!("추출 실패 {}: {}", target, e);
                    }
                }
            }
            None => {
                log::warn!("파일 없음: {}", target);
            }
        }
    }

    // 추출 완료 후 번들 캐시 해제
    index.clear_cache();

    let result = serde_json::json!({
        "total_files": index.file_count(),
        "extracted": extracted,
    });

    Ok(result.to_string())
}

#[tauri::command]
async fn generate_filter(
    build_json: String,
    coaching_json: String,
    strictness: u8,
    game: Option<Game>,
) -> Result<String, String> {
    generate_filter_multi(vec![build_json], coaching_json, strictness, false, "ssf".to_string(), 67, game).await
}

#[tauri::command]
async fn generate_filter_multi(
    build_jsons: Vec<String>,
    coaching_json: String,
    strictness: u8,
    stage: bool,
    mode: String,
    al_split: u8,
    game: Option<Game>,
) -> Result<String, String> {
    let g = game_or_default(game);
    tauri::async_runtime::spawn_blocking(move || {
        if build_jsons.is_empty() {
            return Err("빌드 JSON이 비어있습니다".to_string());
        }
        let temp_dir = std::env::temp_dir();
        let coach_path = temp_dir.join("pathcraft_coaching.json");
        std::fs::write(&coach_path, &coaching_json)
            .map_err(|e| format!("코칭 임시파일 쓰기 실패: {}", e))?;

        // 각 빌드 JSON을 temp 파일로 (다중 POB 지원)
        let mut build_paths: Vec<std::path::PathBuf> = Vec::with_capacity(build_jsons.len());
        for (i, bj) in build_jsons.iter().enumerate() {
            let p = temp_dir.join(format!("pathcraft_build_{}.json", i));
            std::fs::write(&p, bj)
                .map_err(|e| format!("빌드 {} 임시파일 쓰기 실패: {}", i, e))?;
            build_paths.push(p);
        }

        let mut cmd = new_python_cmd();
        cmd.arg(python_dir().join("filter_generator.py"));
        for p in &build_paths {
            cmd.arg(p);
        }
        cmd.arg("--coaching").arg(&coach_path)
            .arg("--strictness").arg(strictness.to_string())
            .arg("--mode").arg(&mode)
            .arg("--al-split").arg(al_split.to_string())
            .arg("--game").arg(g.as_cli_flag())
            .arg("--json");
        if stage {
            cmd.arg("--stage");
        }
        cmd.env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root());

        let output = cmd.output()
            .map_err(|e| format!("Python 실행 실패: {}", e))?;

        for p in &build_paths {
            let _ = std::fs::remove_file(p);
        }
        let _ = std::fs::remove_file(&coach_path);

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            Err(format!("필터 생성 에러: {}", stderr))
        }
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
async fn syndicate_recommend(build_json: String, game: Option<Game>) -> Result<String, String> {
    // Syndicate = Betrayal 리그 POE1 전용 메커닉 (backlog D7). POE2 요청 거부.
    if game_or_default(game) == Game::Poe2 {
        return Err("Syndicate 는 POE1 전용입니다 (POE2 미지원)".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        let mut child = new_python_cmd()
            .arg(python_dir().join("syndicate_advisor.py"))
            .arg("-")
            .env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root())
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()
            .map_err(|e| format!("Python 실행 실패: {}", e))?;
        use std::io::Write;
        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(build_json.as_bytes())
                .map_err(|e| format!("stdin 전달 실패: {}", e))?;
        }
        let output = child.wait_with_output()
            .map_err(|e| format!("프로세스 대기 실패: {}", e))?;
        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            Err(format!("Syndicate advisor 에러: {}",
                        String::from_utf8_lossy(&output.stderr)))
        }
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
async fn analyze_syndicate_image(
    image_base64: String,
    game: Option<Game>,
) -> Result<String, String> {
    // Claude Vision API 호출 — 큰 base64 페이로드는 stdin 전달.
    // .env 파일에서 ANTHROPIC_API_KEY 자동 로드 (프로젝트 루트).
    // Syndicate POE1 전용 (backlog D7).
    if game_or_default(game) == Game::Poe2 {
        return Err("Syndicate 는 POE1 전용입니다 (POE2 미지원)".to_string());
    }
    tauri::async_runtime::spawn_blocking(move || {
        let mut child = new_python_cmd()
            .arg(python_dir().join("syndicate_vision.py"))
            .env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root())
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped())
            .spawn()
            .map_err(|e| format!("Python 실행 실패: {}", e))?;
        use std::io::Write;
        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(image_base64.as_bytes())
                .map_err(|e| format!("stdin 전달 실패: {}", e))?;
        }
        let output = child.wait_with_output()
            .map_err(|e| format!("프로세스 대기 실패: {}", e))?;
        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            Err(format!("Vision 분석 에러: {}", String::from_utf8_lossy(&output.stderr)))
        }
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
fn collect_patch_notes(game: Option<Game>) -> Result<String, String> {
    // D8 별도 프로세스 전까지는 플래그만 전달, 실제 소스 분기는 Python 측 책임.
    let g = game_or_default(game);
    run_python("patch_note_scraper.py", &["--collect", "--game", g.as_cli_flag()])
}

#[tauri::command]
fn get_latest_patch(game: Option<Game>) -> Result<String, String> {
    let g = game_or_default(game);
    run_python("patch_note_scraper.py", &["--latest", "--game", g.as_cli_flag()])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn project_root_returns_existing_dir() {
        let root = project_root();
        // 빈 경로가 아니어야 함
        assert!(!root.as_os_str().is_empty(), "project_root가 빈 경로 반환");
    }

    #[test]
    fn python_dir_is_under_project_root() {
        let py = python_dir();
        let root = project_root();
        assert!(
            py.starts_with(&root),
            "python_dir({:?})가 project_root({:?}) 하위가 아님",
            py, root
        );
        assert!(py.ends_with("python"));
    }

    #[test]
    fn run_python_invalid_script_returns_err() {
        let result = run_python("nonexistent_script_xyz.py", &[]);
        assert!(result.is_err(), "존재하지 않는 스크립트인데 Ok 반환");
    }

    #[test]
    fn game_or_default_none_is_poe1() {
        assert_eq!(game_or_default(None), Game::Poe1);
    }

    #[test]
    fn game_or_default_some_preserves_value() {
        assert_eq!(game_or_default(Some(Game::Poe2)), Game::Poe2);
        assert_eq!(game_or_default(Some(Game::Poe1)), Game::Poe1);
    }

    #[test]
    fn game_deserializes_from_lowercase_string() {
        let g: Game = serde_json::from_str(r#""poe1""#).unwrap();
        assert_eq!(g, Game::Poe1);
        let g: Game = serde_json::from_str(r#""poe2""#).unwrap();
        assert_eq!(g, Game::Poe2);
    }

    #[test]
    fn game_serializes_to_lowercase_string() {
        assert_eq!(serde_json::to_string(&Game::Poe1).unwrap(), r#""poe1""#);
        assert_eq!(serde_json::to_string(&Game::Poe2).unwrap(), r#""poe2""#);
    }

    #[test]
    fn game_cli_flag_matches_lowercase() {
        assert_eq!(Game::Poe1.as_cli_flag(), "poe1");
        assert_eq!(Game::Poe2.as_cli_flag(), "poe2");
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![parse_pob, coach_build, cancel_coach, generate_filter, generate_filter_multi, syndicate_recommend, analyze_syndicate_image, collect_patch_notes, get_latest_patch, extract_game_data])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
