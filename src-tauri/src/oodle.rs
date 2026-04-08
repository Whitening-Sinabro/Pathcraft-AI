//! Oodle DLL 동적 로더
//!
//! POE 번들 파일의 Oodle 압축(Leviathan/Kraken/Mermaid 등)을 해제한다.
//! oo2core_X_win64.dll을 런타임에 동적 로드하여 OodleLZ_Decompress를 호출.

use libloading::Library;
use std::path::{Path, PathBuf};

/// OodleLZ_Decompress 함수 시그니처 (Windows x64)
type OodleLZDecompressFn = unsafe extern "C" fn(
    src: *const u8,
    src_len: isize,
    dst: *mut u8,
    dst_len: isize,
    fuzz_safe: i32,
    check_crc: i32,
    verbosity: i32,
    dst_base: *const u8,
    dst_base_size: isize,
    fp_callback: *const (),
    callback_user_data: *const (),
    decoder_memory: *mut u8,
    decoder_memory_size: isize,
    thread_phase: i32,
) -> isize;

pub struct OodleLib {
    _lib: Library,
    decompress_fn: OodleLZDecompressFn,
}

impl OodleLib {
    /// POE 설치 경로에서 Oodle DLL을 찾아 로드
    pub fn load(poe_path: &Path) -> Result<Self, String> {
        let candidates = find_oodle_dll(poe_path);

        for path in &candidates {
            if !path.exists() {
                continue;
            }
            log::info!("Oodle DLL 시도: {}", path.display());
            match unsafe { Library::new(path) } {
                Ok(lib) => {
                    match unsafe {
                        lib.get::<OodleLZDecompressFn>(b"OodleLZ_Decompress\0")
                    } {
                        Ok(sym) => {
                            let decompress_fn = *sym;
                            log::info!("Oodle DLL 로드 성공: {}", path.display());
                            return Ok(Self {
                                _lib: lib,
                                decompress_fn,
                            });
                        }
                        Err(e) => {
                            log::warn!("OodleLZ_Decompress 심볼 없음: {}", e);
                        }
                    }
                }
                Err(e) => {
                    log::warn!("DLL 로드 실패: {} — {}", path.display(), e);
                }
            }
        }

        Err(format!(
            "oo2core DLL을 찾을 수 없습니다.\n\
             POE Steam 설치 경로에 oo2core_X_win64.dll이 있어야 합니다.\n\
             탐색 경로:\n{}",
            candidates
                .iter()
                .map(|p| format!("  - {}", p.display()))
                .collect::<Vec<_>>()
                .join("\n")
        ))
    }

    /// 압축된 데이터를 해제
    ///
    /// `dst`는 원본 크기만큼 미리 할당되어 있어야 함.
    /// 성공 시 해제된 바이트 수 반환.
    pub fn decompress(&self, src: &[u8], dst: &mut [u8]) -> Result<usize, String> {
        let result = unsafe {
            (self.decompress_fn)(
                src.as_ptr(),
                src.len() as isize,
                dst.as_mut_ptr(),
                dst.len() as isize,
                1,                    // fuzz_safe
                0,                    // check_crc
                0,                    // verbosity
                std::ptr::null(),     // dst_base
                0,                    // dst_base_size
                std::ptr::null(),     // fp_callback
                std::ptr::null(),     // callback_user_data
                std::ptr::null_mut(), // decoder_memory
                0,                    // decoder_memory_size
                3,                    // thread_phase
            )
        };

        if result < 0 {
            Err(format!("Oodle 압축 해제 실패 (코드: {})", result))
        } else {
            Ok(result as usize)
        }
    }
}

/// DLL 후보 경로 목록 생성
fn find_oodle_dll(poe_path: &Path) -> Vec<PathBuf> {
    let mut paths = Vec::new();

    // 1. POE 설치 경로에서 직접 탐색
    for version in (6..=10).rev() {
        paths.push(poe_path.join(format!("oo2core_{}_win64.dll", version)));
    }

    // 2. Steam 기본 설치 경로
    let steam_common = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Path of Exile",
        r"C:\Program Files\Steam\steamapps\common\Path of Exile",
        r"D:\Steam\steamapps\common\Path of Exile",
        r"D:\SteamLibrary\steamapps\common\Path of Exile",
        r"E:\SteamLibrary\steamapps\common\Path of Exile",
    ];
    for steam_path in &steam_common {
        let steam_dir = Path::new(steam_path);
        if steam_dir.is_dir() {
            for version in (6..=10).rev() {
                paths.push(steam_dir.join(format!("oo2core_{}_win64.dll", version)));
            }
        }
    }

    // 3. Unreal Engine (Oodle 번들 포함)
    let ue_base_dirs = [
        r"C:\Program Files\Epic Games",
        r"D:\Epic Games",
    ];
    for base in &ue_base_dirs {
        let base_path = Path::new(base);
        if !base_path.is_dir() {
            continue;
        }
        if let Ok(entries) = std::fs::read_dir(base_path) {
            for entry in entries.flatten() {
                let ue_dir = entry.path();
                if ue_dir.is_dir() {
                    let automaton_tool = ue_dir.join(r"Engine\Binaries\DotNET\AutomationTool");
                    for version in (6..=10).rev() {
                        paths.push(automaton_tool.join(format!("oo2core_{}_win64.dll", version)));
                    }
                    let win64 = ue_dir.join(r"Engine\Binaries\Win64");
                    for version in (6..=10).rev() {
                        paths.push(win64.join(format!("oo2core_{}_win64.dll", version)));
                    }
                }
            }
        }
    }

    paths
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn find_oodle_dll_includes_poe_path() {
        let paths = find_oodle_dll(Path::new(r"C:\Games\POE"));
        assert!(paths.iter().any(|p| p.to_string_lossy().contains("oo2core_9_win64.dll")));
        assert!(paths.iter().any(|p| p.to_string_lossy().contains(r"C:\Games\POE")));
    }
}
