use std::process::Command;
use std::path::PathBuf;

fn project_root() -> PathBuf {
    // TAURI_PROJECT_ROOT 환경변수 > exe 위치 기준 > CWD 기준
    if let Ok(root) = std::env::var("TAURI_PROJECT_ROOT") {
        return PathBuf::from(root);
    }

    // 프로덕션: exe와 같은 디렉토리 또는 상위에 python/ 폴더 탐색
    if let Ok(exe) = std::env::current_exe() {
        if let Some(exe_dir) = exe.parent() {
            if exe_dir.join("python").is_dir() {
                return exe_dir.to_path_buf();
            }
            if let Some(parent) = exe_dir.parent() {
                if parent.join("python").is_dir() {
                    return parent.to_path_buf();
                }
            }
        }
    }

    // 개발: CWD(src-tauri/)의 상위 = 프로젝트 루트
    std::env::current_dir()
        .unwrap_or_default()
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_default()
}

fn python_dir() -> PathBuf {
    project_root().join("python")
}

fn run_python(script: &str, args: &[&str]) -> Result<String, String> {
    let output = Command::new("python")
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

#[tauri::command]
fn parse_pob(link: String) -> Result<String, String> {
    run_python("pob_parser.py", &[&link])
}

#[tauri::command]
fn coach_build(build_json: String) -> Result<String, String> {
    let mut child = Command::new("python")
        .arg(python_dir().join("build_coach.py"))
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
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();
        Err(format!("코치 에러: {}", stderr))
    }
}

#[tauri::command]
fn collect_patch_notes() -> Result<String, String> {
    run_python("patch_note_scraper.py", &["--collect"])
}

#[tauri::command]
fn get_latest_patch() -> Result<String, String> {
    run_python("patch_note_scraper.py", &["--latest"])
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
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![parse_pob, coach_build, collect_patch_notes, get_latest_patch])
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
