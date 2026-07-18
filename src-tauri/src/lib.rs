pub mod bundle;
pub mod bundle_index;
pub mod dat64;
pub mod ggpk;
pub mod oodle;
pub mod schema;

use schema::Game;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::{Mutex, OnceLock};
use std::time::{SystemTime, UNIX_EPOCH};

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

#[cfg(target_os = "windows")]
fn configure_webview2_browser_args() {
    const KEY: &str = "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS";
    const QUIET_ARGS: &str = "--disable-logging --log-level=3";

    match std::env::var(KEY) {
        Ok(existing) => {
            let has_logging_override = existing.contains("--log-level=")
                || existing.contains("--disable-logging")
                || existing.contains("--enable-logging");
            if !has_logging_override {
                std::env::set_var(KEY, format!("{} {}", existing.trim(), QUIET_ARGS));
            }
        }
        Err(_) => std::env::set_var(KEY, QUIET_ARGS),
    }
}

#[cfg(not(target_os = "windows"))]
fn configure_webview2_browser_args() {}

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
async fn resolve_build_source(url: String, game: Option<Game>) -> Result<String, String> {
    let _g = game_or_default(game);
    tauri::async_runtime::spawn_blocking(move || run_python("build_source_resolver.py", &[&url]))
        .await
        .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
async fn recommend_from_corpus_build(
    build_json: String,
    mode: String,
    game: Option<Game>,
) -> Result<String, String> {
    if game_or_default(game) == Game::Poe2 {
        return Err("대표 빌드 추천은 POE1 전용입니다 (POE2 미지원)".to_string());
    }

    let normalized_mode = match mode.as_str() {
        "sc" | "ssf" | "hcssf" => mode,
        _ => return Err(format!("허용되지 않은 모드: {}", mode)),
    };

    tauri::async_runtime::spawn_blocking(move || {
        let temp_dir = std::env::temp_dir();
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or_default();
        let build_path = temp_dir.join(format!(
            "pathcraft_representative_build_{}_{}.json",
            std::process::id(),
            nonce,
        ));
        std::fs::write(&build_path, &build_json)
            .map_err(|e| format!("대표 빌드 추천 임시파일 쓰기 실패: {}", e))?;

        let mut cmd = new_python_cmd();
        cmd.arg(python_dir().join("recommend_from_corpus.py"))
            .arg("--build-json")
            .arg(&build_path)
            .arg("--mode")
            .arg(&normalized_mode)
            .env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root());

        let output = cmd.output();
        let _ = std::fs::remove_file(&build_path);
        let output = output.map_err(|e| format!("Python 실행 실패: {}", e))?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            Err(format!("대표 빌드 추천 에러: {}", stderr))
        }
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
            Some("gpt-5-nano") => Some("gpt-5-nano"),
            Some("gpt-5-mini") => Some("gpt-5-mini"),
            Some("gpt-5") => Some("gpt-5"),
            Some("gpt-5.3-codex") => Some("gpt-5.3-codex"),
            Some("claude-haiku-4-5-20251001") => Some("claude-haiku-4-5-20251001"),
            Some("claude-sonnet-4-6") => Some("claude-sonnet-4-6"),
            Some("claude-opus-4-7") => Some("claude-opus-4-7"),
            Some(other) => return Err(format!("허용되지 않은 모델: {}", other)),
            None => None, // Python 기본값 사용
        };
        let mut cmd = new_python_cmd();
        cmd.arg(python_dir().join("build_coach.py"))
            .arg("-")
            .arg("--game")
            .arg(g.as_cli_flag())
            .env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root())
            .stdin(std::process::Stdio::piped())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::piped());
        if let Some(m) = model_arg {
            cmd.arg("--model").arg(m);
        }
        let mut child = cmd
            .spawn()
            .map_err(|e| format!("Python 실행 실패: {}", e))?;

        use std::io::Write;
        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(build_json.as_bytes())
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
            let mut slot = coach_child()
                .lock()
                .map_err(|e| format!("레지스트리 잠금 실패: {}", e))?;
            match slot.take() {
                Some(mut c) => c.wait().map_err(|e| format!("프로세스 대기 실패: {}", e))?,
                None => return Err("코치 취소됨".to_string()), // cancel_coach가 이미 회수
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
    let mut slot = coach_child()
        .lock()
        .map_err(|e| format!("레지스트리 잠금 실패: {}", e))?;
    match slot.take() {
        Some(mut child) => {
            let _ = child.kill();
            let _ = child.wait();
            Ok(true)
        }
        None => Ok(false), // 실행 중인 coach 없음
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
    std::fs::create_dir_all(&output_dir).map_err(|e| format!("출력 디렉토리 생성 실패: {}", e))?;

    let target_tables = [
        "Data/ActiveSkills.datc64",
        "Data/SkillGems.datc64",
        "Data/BaseItemTypes.datc64",
        "Data/Maps.datc64",
        "Data/QuestRewards.datc64",
        "Data/PassiveSkills.datc64",
        "Data/UniqueStashLayout.datc64",
        "Data/UniqueStashTypes.datc64",
        "Data/AttributeRequirements.datc64",
    ];

    let mut extracted = Vec::new();

    for target in &target_tables {
        match index.find_file(target) {
            Some(file) => {
                let file = file.clone();
                match index.extract_file(&file, &oodle) {
                    Ok(data) => {
                        let filename = target.rsplit('/').next().unwrap_or(target);

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
    generate_filter_multi(
        vec![build_json],
        coaching_json,
        strictness,
        false,
        "ssf".to_string(),
        67,
        game,
    )
    .await
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
            std::fs::write(&p, bj).map_err(|e| format!("빌드 {} 임시파일 쓰기 실패: {}", i, e))?;
            build_paths.push(p);
        }

        let mut cmd = new_python_cmd();
        cmd.arg(python_dir().join("filter_generator.py"));
        for p in &build_paths {
            cmd.arg(p);
        }
        cmd.arg("--coaching")
            .arg(&coach_path)
            .arg("--strictness")
            .arg(strictness.to_string())
            .arg("--mode")
            .arg(&mode)
            .arg("--al-split")
            .arg(al_split.to_string())
            .arg("--game")
            .arg(g.as_cli_flag())
            .arg("--json");
        if stage {
            cmd.arg("--stage");
        }
        cmd.env("PYTHONIOENCODING", "utf-8")
            .current_dir(project_root());

        let output = cmd
            .output()
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
            stdin
                .write_all(build_json.as_bytes())
                .map_err(|e| format!("stdin 전달 실패: {}", e))?;
        }
        let output = child
            .wait_with_output()
            .map_err(|e| format!("프로세스 대기 실패: {}", e))?;
        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            Err(format!(
                "Syndicate advisor 에러: {}",
                String::from_utf8_lossy(&output.stderr)
            ))
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
            stdin
                .write_all(image_base64.as_bytes())
                .map_err(|e| format!("stdin 전달 실패: {}", e))?;
        }
        let output = child
            .wait_with_output()
            .map_err(|e| format!("프로세스 대기 실패: {}", e))?;
        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            Err(format!(
                "Vision 분석 에러: {}",
                String::from_utf8_lossy(&output.stderr)
            ))
        }
    })
    .await
    .map_err(|e| format!("작업 스케줄 실패: {}", e))?
}

#[tauri::command]
fn collect_patch_notes(game: Option<Game>) -> Result<String, String> {
    // D8 별도 프로세스 전까지는 플래그만 전달, 실제 소스 분기는 Python 측 책임.
    let g = game_or_default(game);
    run_python(
        "patch_note_scraper.py",
        &["--collect", "--game", g.as_cli_flag()],
    )
}

#[tauri::command]
fn get_latest_patch(game: Option<Game>) -> Result<String, String> {
    let g = game_or_default(game);
    run_python(
        "patch_note_scraper.py",
        &["--latest", "--game", g.as_cli_flag()],
    )
}

fn read_data_json(rel_path: &str) -> Result<serde_json::Value, String> {
    let path = project_root().join("data").join(rel_path);
    let text =
        std::fs::read_to_string(&path).map_err(|e| format!("{} 읽기 실패: {}", rel_path, e))?;
    serde_json::from_str(&text).map_err(|e| format!("{} JSON 파싱 실패: {}", rel_path, e))
}

const BACKEND_GUARD_PATCH_BASELINE: &str = "3.29.0";

struct BackendRecommendationGuard {
    guard_id: &'static str,
    visibility: &'static str,
    tokens: &'static [&'static str],
    note: &'static str,
}

const BACKEND_RECOMMENDATION_GUARDS: &[BackendRecommendationGuard] = &[
    BackendRecommendationGuard {
        guard_id: "post_3_26_hexblast_trigger_cooldown_guard",
        visibility: "hold",
        tokens: &["hexblast"],
        note: "Hexblast Mine cannot be carried forward as a default recommendation without current-patch specialist PoB/live proof.",
    },
    BackendRecommendationGuard {
        guard_id: "patch_3_29_ballista_totem_guard",
        visibility: "practice_only",
        tokens: &["ballista"],
        note: "3.29 increases Ballista Totem less-damage pressure; old Ballista PoBs are practice-only until refreshed.",
    },
    BackendRecommendationGuard {
        guard_id: "patch_3_29_spell_totem_and_totem_scaling_guard",
        visibility: "practice_only",
        tokens: &["totem"],
        note: "3.29 directly changes Spell Totem penalty and multiple totem scaling passives; old Totem PoBs are practice-only until refreshed.",
    },
    BackendRecommendationGuard {
        guard_id: "patch_3_29_mine_support_guard",
        visibility: "practice_only",
        tokens: &[" mine", "_mine", "mines"],
        note: "3.29 changes Blastchain Mine, High-Impact Mine, and Charged Mines cost/damage/throw-speed values; old Mine PoBs are practice-only until refreshed.",
    },
];

fn lower_json_string(value: Option<&serde_json::Value>) -> String {
    value
        .and_then(serde_json::Value::as_str)
        .unwrap_or_default()
        .to_lowercase()
}

fn profile_guard_text(row: &serde_json::Value) -> String {
    let profile = row.get("build_profile").unwrap_or(&serde_json::Value::Null);
    let identity = profile.get("identity").unwrap_or(&serde_json::Value::Null);
    let parts = [
        lower_json_string(row.get("candidate_id")),
        lower_json_string(profile.get("build_id")),
        lower_json_string(identity.get("build_name")),
        lower_json_string(identity.get("main_skill")),
        lower_json_string(identity.get("leveling_skill")),
        lower_json_string(identity.get("ascendancy")),
    ];
    format!(" {} ", parts.join(" "))
}

fn match_backend_guard(row: &serde_json::Value) -> Option<&'static BackendRecommendationGuard> {
    let text = profile_guard_text(row);
    BACKEND_RECOMMENDATION_GUARDS
        .iter()
        .find(|guard| guard.tokens.iter().any(|token| text.contains(token)))
}

fn ensure_object_mut(
    value: &mut serde_json::Value,
) -> &mut serde_json::Map<String, serde_json::Value> {
    if !value.is_object() {
        *value = serde_json::json!({});
    }
    value
        .as_object_mut()
        .expect("value was just converted to object")
}

fn add_guard_pain_point(row: &mut serde_json::Value, guard_id: &str) {
    let row_obj = ensure_object_mut(row);
    let profile = row_obj
        .entry("build_profile".to_string())
        .or_insert_with(|| serde_json::json!({}));
    let profile_obj = ensure_object_mut(profile);
    let constraints = profile_obj
        .entry("constraints".to_string())
        .or_insert_with(|| serde_json::json!({}));
    let constraints_obj = ensure_object_mut(constraints);
    let pain_points = constraints_obj
        .entry("pain_points".to_string())
        .or_insert_with(|| serde_json::json!([]));
    if !pain_points.is_array() {
        *pain_points = serde_json::json!([]);
    }
    let points = pain_points
        .as_array_mut()
        .expect("pain_points was just converted to array");
    if !points.iter().any(|point| point.as_str() == Some(guard_id)) {
        points.push(serde_json::json!(guard_id));
    }
}

fn set_profile_status_hold(row: &mut serde_json::Value) {
    let row_obj = ensure_object_mut(row);
    let profile = row_obj
        .entry("build_profile".to_string())
        .or_insert_with(|| serde_json::json!({}));
    let profile_obj = ensure_object_mut(profile);
    let confidence = profile_obj
        .entry("confidence".to_string())
        .or_insert_with(|| serde_json::json!({}));
    ensure_object_mut(confidence).insert(
        "representative_build_status".to_string(),
        serde_json::json!("hold"),
    );
}

fn row_candidate_id(row: &serde_json::Value) -> Option<String> {
    row.get("candidate_id")
        .and_then(serde_json::Value::as_str)
        .map(str::to_string)
}

fn row_string(row: &serde_json::Value, key: &str) -> String {
    row.get(key)
        .and_then(serde_json::Value::as_str)
        .unwrap_or_default()
        .to_string()
}

fn is_backend_default_candidate(row: &serde_json::Value) -> bool {
    row.get("player_facing_default")
        .and_then(serde_json::Value::as_bool)
        != Some(false)
        && row_string(row, "board_status") != "hold"
        && row_string(row, "use_policy") != "do_not_default"
}

fn verify_backend_guard_row(
    row: &mut serde_json::Value,
) -> Option<&'static BackendRecommendationGuard> {
    if let Some(guard) = match_backend_guard(row) {
        {
            let row_obj = ensure_object_mut(row);
            row_obj.insert(
                "player_facing_default".to_string(),
                serde_json::json!(false),
            );
            row_obj.insert(
                "recommendation_visibility".to_string(),
                serde_json::json!(guard.visibility),
            );
            row_obj.insert(
                "forward_guard_note".to_string(),
                serde_json::json!(guard.note),
            );
            row_obj.insert(
                "backend_guard".to_string(),
                serde_json::json!({
                    "status": "blocked_from_default",
                    "guard_id": guard.guard_id,
                    "visibility": guard.visibility,
                    "verified_against_patch": BACKEND_GUARD_PATCH_BASELINE,
                }),
            );
            if guard.visibility == "hold" {
                row_obj.insert("board_status".to_string(), serde_json::json!("hold"));
                row_obj.insert(
                    "use_policy".to_string(),
                    serde_json::json!("do_not_default"),
                );
            }
        }
        add_guard_pain_point(row, guard.guard_id);
        if guard.visibility == "hold" {
            set_profile_status_hold(row);
        }
        return Some(guard);
    }

    let player_default = row
        .get("player_facing_default")
        .and_then(serde_json::Value::as_bool)
        .unwrap_or_else(|| {
            row_string(row, "board_status") != "hold"
                && row_string(row, "use_policy") != "do_not_default"
        });
    let visibility = row
        .get("recommendation_visibility")
        .and_then(serde_json::Value::as_str)
        .map(str::to_string)
        .unwrap_or_else(|| {
            if player_default {
                "default".to_string()
            } else {
                "hold".to_string()
            }
        });
    let row_obj = ensure_object_mut(row);
    row_obj.insert(
        "player_facing_default".to_string(),
        serde_json::json!(player_default),
    );
    let backend_visibility = visibility.clone();
    row_obj.insert(
        "recommendation_visibility".to_string(),
        serde_json::json!(visibility),
    );
    row_obj.insert(
        "backend_guard".to_string(),
        serde_json::json!({
            "status": "passed",
            "guard_id": null,
            "visibility": backend_visibility,
            "verified_against_patch": BACKEND_GUARD_PATCH_BASELINE,
        }),
    );
    None
}

fn apply_backend_recommendation_guard(
    mut profiles_payload: serde_json::Value,
) -> (serde_json::Value, serde_json::Value) {
    let mut blocked_candidate_ids: Vec<String> = Vec::new();
    let mut guard_ids = std::collections::BTreeSet::new();
    let mut profile_count = 0usize;
    let mut default_candidate_count = 0usize;

    if let Some(profiles) = profiles_payload
        .get_mut("profiles")
        .and_then(serde_json::Value::as_array_mut)
    {
        profile_count = profiles.len();
        for row in profiles.iter_mut() {
            if let Some(guard) = verify_backend_guard_row(row) {
                if let Some(candidate_id) = row_candidate_id(row) {
                    blocked_candidate_ids.push(candidate_id);
                }
                guard_ids.insert(guard.guard_id.to_string());
            }
        }
        default_candidate_count = profiles
            .iter()
            .filter(|row| is_backend_default_candidate(row))
            .count();
    }

    let summary = serde_json::json!({
        "dataset_kind": "poe1_backend_recommendation_guard_summary",
        "verified_against_patch": BACKEND_GUARD_PATCH_BASELINE,
        "profile_count": profile_count,
        "default_candidate_count": default_candidate_count,
        "blocked_from_default_count": blocked_candidate_ids.len(),
        "blocked_candidate_ids": blocked_candidate_ids,
        "guard_ids": guard_ids.into_iter().collect::<Vec<String>>(),
    });

    if let Some(obj) = profiles_payload.as_object_mut() {
        obj.insert("backend_guard_summary".to_string(), summary.clone());
    }

    (profiles_payload, summary)
}

fn strip_internal_profile_fields(row: &mut serde_json::Value) {
    if let Some(obj) = row.as_object_mut() {
        obj.remove("player_facing_default");
        obj.remove("recommendation_visibility");
        obj.remove("forward_guard_note");
        obj.remove("backend_guard");
    }
}

fn public_representative_profiles(mut profiles_payload: serde_json::Value) -> serde_json::Value {
    let mut public_summary: Option<(usize, usize, usize, usize)> = None;
    if let Some(profiles) = profiles_payload
        .get_mut("profiles")
        .and_then(serde_json::Value::as_array_mut)
    {
        profiles.retain(is_backend_default_candidate);
        for row in profiles.iter_mut() {
            strip_internal_profile_fields(row);
        }
        let profile_count = profiles.len();
        let confirmed = profiles
            .iter()
            .filter(|row| row_string(row, "board_status") == "confirmed")
            .count();
        let near_confirmed = profiles
            .iter()
            .filter(|row| row_string(row, "board_status") == "near_confirmed")
            .count();
        let hold = profiles
            .iter()
            .filter(|row| row_string(row, "board_status") == "hold")
            .count();
        public_summary = Some((profile_count, confirmed, near_confirmed, hold));
    }

    if let Some(obj) = profiles_payload.as_object_mut() {
        obj.remove("backend_guard_summary");
        if let Some((profile_count, confirmed, near_confirmed, hold)) = public_summary {
            obj.insert(
                "summary".to_string(),
                serde_json::json!({
                    "profile_count": profile_count,
                    "confirmed": confirmed,
                    "near_confirmed": near_confirmed,
                    "hold": hold,
                }),
            );
        }
    }

    profiles_payload
}

#[tauri::command]
fn load_poe1_research_dashboard() -> Result<String, String> {
    let (representative_profiles, _recommendation_guard) = apply_backend_recommendation_guard(
        read_data_json("poe1_representative_build_profiles.latest.json")?,
    );
    let representative_profiles = public_representative_profiles(representative_profiles);
    let result = serde_json::json!({
        "dataset_kind": "poe1_research_dashboard_payload",
        "creator_targets": read_data_json("poe1_global_creator_source_targets_v1.json")?,
        "priority_matrix": read_data_json("poe1_global_creator_priority_matrix_v1.json")?,
        "representative_profiles": representative_profiles,
        "watchlist_candidate_cards": read_data_json("poe1_watchlist_candidate_cards.latest.json")?,
        "patch_history_context": read_data_json("patch_notes/poe1_3_27_3_29_patch_history_context.json")?,
        "luminary_intake": read_data_json("poe1_3_29_luminary_merc_link_intake_v1.json")?,
        "corpus_reuse_review": read_data_json("poe1_3_29_corpus_reuse_review_v1.json")?,
        "live_validation_queue": read_data_json("poe1_3_29_live_validation_queue.json")?,
    });
    Ok(result.to_string())
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
            py,
            root
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

    fn guard_test_row(candidate_id: &str, main_skill: &str) -> serde_json::Value {
        serde_json::json!({
            "candidate_id": candidate_id,
            "board_status": "confirmed",
            "use_policy": "default",
            "build_profile": {
                "build_id": candidate_id,
                "identity": {
                    "build_name": main_skill,
                    "main_skill": main_skill,
                    "class_name": "Shadow",
                    "ascendancy": "Trickster"
                },
                "confidence": {
                    "representative_build_status": "confirmed"
                },
                "constraints": {
                    "pain_points": []
                }
            }
        })
    }

    fn guarded_row<'a>(
        payload: &'a serde_json::Value,
        candidate_id: &str,
    ) -> &'a serde_json::Value {
        payload
            .get("profiles")
            .and_then(serde_json::Value::as_array)
            .unwrap()
            .iter()
            .find(|row| {
                row.get("candidate_id").and_then(serde_json::Value::as_str) == Some(candidate_id)
            })
            .unwrap()
    }

    #[test]
    fn backend_recommendation_guard_blocks_patch_sensitive_families_from_default() {
        let payload = serde_json::json!({
            "profiles": [
                guard_test_row("hexblast_case", "Hexblast Mine"),
                guard_test_row("exsanguinate_case", "Exsanguinate Mine"),
                guard_test_row("shockwave_case", "Shockwave Totem"),
                guard_test_row("ballista_case", "Siege Ballista"),
                guard_test_row("safe_case", "Lightning Arrow")
            ]
        });

        let (guarded, summary) = apply_backend_recommendation_guard(payload);

        let hexblast = guarded_row(&guarded, "hexblast_case");
        assert_eq!(
            hexblast
                .get("player_facing_default")
                .and_then(serde_json::Value::as_bool),
            Some(false)
        );
        assert_eq!(
            hexblast
                .get("recommendation_visibility")
                .and_then(serde_json::Value::as_str),
            Some("hold")
        );
        assert_eq!(
            hexblast
                .get("board_status")
                .and_then(serde_json::Value::as_str),
            Some("hold")
        );
        assert_eq!(
            hexblast
                .get("use_policy")
                .and_then(serde_json::Value::as_str),
            Some("do_not_default")
        );
        assert_eq!(
            hexblast
                .pointer("/build_profile/confidence/representative_build_status")
                .and_then(serde_json::Value::as_str),
            Some("hold")
        );

        for candidate_id in ["exsanguinate_case", "shockwave_case", "ballista_case"] {
            let row = guarded_row(&guarded, candidate_id);
            assert_eq!(
                row.get("player_facing_default")
                    .and_then(serde_json::Value::as_bool),
                Some(false)
            );
            assert_eq!(
                row.get("recommendation_visibility")
                    .and_then(serde_json::Value::as_str),
                Some("practice_only")
            );
            assert_eq!(
                row.pointer("/backend_guard/status")
                    .and_then(serde_json::Value::as_str),
                Some("blocked_from_default")
            );
        }

        let safe = guarded_row(&guarded, "safe_case");
        assert_eq!(
            safe.get("player_facing_default")
                .and_then(serde_json::Value::as_bool),
            Some(true)
        );
        assert_eq!(
            safe.pointer("/backend_guard/status")
                .and_then(serde_json::Value::as_str),
            Some("passed")
        );

        assert_eq!(
            summary
                .get("profile_count")
                .and_then(serde_json::Value::as_u64),
            Some(5)
        );
        assert_eq!(
            summary
                .get("default_candidate_count")
                .and_then(serde_json::Value::as_u64),
            Some(1)
        );
        assert_eq!(
            summary
                .get("blocked_from_default_count")
                .and_then(serde_json::Value::as_u64),
            Some(4)
        );
        assert_eq!(
            guarded
                .get("backend_guard_summary")
                .and_then(|payload_summary| payload_summary.get("profile_count"))
                .and_then(serde_json::Value::as_u64),
            Some(5)
        );
    }

    #[test]
    fn public_representative_profiles_remove_internal_guard_fields() {
        let payload = serde_json::json!({
            "profiles": [
                guard_test_row("hexblast_case", "Hexblast Mine"),
                guard_test_row("safe_case", "Lightning Arrow")
            ]
        });

        let (guarded, _) = apply_backend_recommendation_guard(payload);
        let public_payload = public_representative_profiles(guarded);
        let profiles = public_payload
            .get("profiles")
            .and_then(serde_json::Value::as_array)
            .unwrap();

        assert_eq!(profiles.len(), 1);
        assert_eq!(
            profiles[0]
                .get("candidate_id")
                .and_then(serde_json::Value::as_str),
            Some("safe_case")
        );
        assert!(public_payload.get("backend_guard_summary").is_none());
        assert!(profiles[0].get("backend_guard").is_none());
        assert!(profiles[0].get("player_facing_default").is_none());
        assert!(profiles[0].get("recommendation_visibility").is_none());
        assert!(profiles[0].get("forward_guard_note").is_none());
        assert_eq!(
            public_payload
                .pointer("/summary/profile_count")
                .and_then(serde_json::Value::as_u64),
            Some(1)
        );
        assert_eq!(
            public_payload
                .pointer("/summary/confirmed")
                .and_then(serde_json::Value::as_u64),
            Some(1)
        );
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    configure_webview2_browser_args();

    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            parse_pob,
            resolve_build_source,
            recommend_from_corpus_build,
            coach_build,
            cancel_coach,
            generate_filter,
            generate_filter_multi,
            syndicate_recommend,
            analyze_syndicate_image,
            collect_patch_notes,
            get_latest_patch,
            extract_game_data,
            load_poe1_research_dashboard
        ])
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
