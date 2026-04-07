//! POE GGPK (Grinding Gears Package) 파일 리더
//!
//! Content.ggpk에서 특정 경로의 파일을 추출한다.
//! Standalone 클라이언트용 (Steam Bundle은 별도 모듈).
//!
//! GGPK 구조:
//! - 모든 record: [record_length: u32][tag: [u8;4]][...payload]
//! - 태그: "GGPK" (루트), "PDIR" (디렉토리), "FILE" (파일), "FREE" (빈 공간)

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read, Seek, SeekFrom};
use std::path::Path;

/// GGPK 리더
pub struct GgpkReader {
    file: File,
    /// 경로 → 파일 오프셋 맵 (경로는 "/" 구분, 소문자)
    file_index: HashMap<String, FileEntry>,
}

#[derive(Debug, Clone)]
struct FileEntry {
    offset: u64,     // FILE record의 파일 내 절대 위치
    data_offset: u64, // 실제 데이터 시작 위치
    data_size: u32,   // 데이터 크기
}

impl GgpkReader {
    /// GGPK 파일 열기 + 인덱스 빌드
    pub fn open(path: &Path) -> Result<Self, String> {
        let mut file = File::open(path)
            .map_err(|e| format!("GGPK 파일 열기 실패: {}", e))?;

        // 루트 GGPK record 읽기
        let root_record = read_record_header(&mut file, 0)?;
        if &root_record.tag != b"GGPK" {
            return Err("유효하지 않은 GGPK 파일 (루트 태그 불일치)".into());
        }

        // GGPK record에서 child offsets 읽기
        file.seek(SeekFrom::Start(8)).map_err(io_err)?;
        let version = read_u32(&mut file)?;
        if version < 3 || version > 4 {
            return Err(format!("지원하지 않는 GGPK 버전: {}", version));
        }

        // child offsets (보통 2~3개)
        let child_count = (root_record.length as usize - 12) / 8;
        let mut child_offsets = Vec::with_capacity(child_count);
        for _ in 0..child_count {
            child_offsets.push(read_u64(&mut file)?);
        }

        // root PDIR 찾기
        let mut root_dir_offset = 0u64;
        for &offset in &child_offsets {
            let header = read_record_header(&mut file, offset)?;
            if &header.tag == b"PDIR" {
                root_dir_offset = offset;
                break;
            }
        }

        if root_dir_offset == 0 {
            return Err("루트 디렉토리를 찾을 수 없음".into());
        }

        // 인덱스 빌드 (재귀적 디렉토리 탐색)
        let mut file_index = HashMap::new();
        build_index(&mut file, root_dir_offset, "", &mut file_index)?;

        Ok(Self { file, file_index })
    }

    /// 인덱스된 파일 수
    pub fn file_count(&self) -> usize {
        self.file_index.len()
    }

    /// 특정 경로의 파일 데이터 추출
    pub fn extract(&mut self, path: &str) -> Result<Vec<u8>, String> {
        let normalized = path.to_lowercase().replace('\\', "/");
        let entry = self.file_index.get(&normalized)
            .ok_or_else(|| format!("파일 없음: {}", path))?
            .clone();

        self.file.seek(SeekFrom::Start(entry.data_offset)).map_err(io_err)?;
        let mut buf = vec![0u8; entry.data_size as usize];
        self.file.read_exact(&mut buf).map_err(io_err)?;

        Ok(buf)
    }

    /// 특정 디렉토리의 파일 목록
    pub fn list_dir(&self, dir: &str) -> Vec<String> {
        let prefix = dir.to_lowercase().replace('\\', "/");
        let prefix = if prefix.ends_with('/') { prefix } else { format!("{}/", prefix) };

        self.file_index.keys()
            .filter(|k| k.starts_with(&prefix))
            .cloned()
            .collect()
    }

    /// .dat64 파일 목록
    pub fn list_dat64(&self) -> Vec<String> {
        self.file_index.keys()
            .filter(|k| k.ends_with(".dat64"))
            .cloned()
            .collect()
    }
}

struct RecordHeader {
    length: u32,
    tag: [u8; 4],
}

fn read_record_header(file: &mut File, offset: u64) -> Result<RecordHeader, String> {
    file.seek(SeekFrom::Start(offset)).map_err(io_err)?;
    let length = read_u32(file)?;
    let mut tag = [0u8; 4];
    file.read_exact(&mut tag).map_err(io_err)?;
    Ok(RecordHeader { length, tag })
}

/// PDIR record를 파싱하고 재귀적으로 하위 디렉토리/파일 인덱싱
fn build_index(
    file: &mut File,
    pdir_offset: u64,
    parent_path: &str,
    index: &mut HashMap<String, FileEntry>,
) -> Result<(), String> {
    file.seek(SeekFrom::Start(pdir_offset)).map_err(io_err)?;
    let record_length = read_u32(file)?;
    let mut tag = [0u8; 4];
    file.read_exact(&mut tag).map_err(io_err)?;

    if &tag != b"PDIR" {
        return Ok(()); // PDIR이 아니면 스킵
    }

    let name_length = read_u32(file)? as usize; // UTF-16LE 문자 수 (null 포함)
    let entry_count = read_u32(file)? as usize;

    // SHA256 해시 스킵 (32바이트)
    file.seek(SeekFrom::Current(32)).map_err(io_err)?;

    // 이름 읽기 (UTF-16LE)
    let dir_name = read_utf16le(file, name_length)?;

    let current_path = if parent_path.is_empty() {
        dir_name.clone()
    } else if dir_name.is_empty() {
        parent_path.to_string()
    } else {
        format!("{}/{}", parent_path, dir_name)
    };

    // 디렉토리 엔트리 읽기
    let mut entries = Vec::with_capacity(entry_count);
    for _ in 0..entry_count {
        let _name_hash = read_u32(file)?;
        let child_offset = read_u64(file)?;
        entries.push(child_offset);
    }

    // 각 엔트리 처리
    for child_offset in entries {
        let header = read_record_header(file, child_offset)?;

        match &header.tag {
            b"PDIR" => {
                build_index(file, child_offset, &current_path, index)?;
            }
            b"FILE" => {
                // FILE record 파싱
                let fname_length = read_u32(file)? as usize;
                // SHA256 스킵
                file.seek(SeekFrom::Current(32)).map_err(io_err)?;
                let file_name = read_utf16le(file, fname_length)?;

                let file_path = if current_path.is_empty() {
                    file_name.to_lowercase()
                } else {
                    format!("{}/{}", current_path, file_name).to_lowercase()
                };

                // 현재 위치가 데이터 시작점
                let data_offset = file.stream_position().map_err(io_err)?;
                let header_size = 4 + 4 + 4 + 32 + (fname_length * 2); // length + tag + name_length + hash + name
                let data_size = header.length - header_size as u32;

                index.insert(file_path, FileEntry {
                    offset: child_offset,
                    data_offset,
                    data_size,
                });
            }
            _ => {} // FREE 등 무시
        }
    }

    Ok(())
}

fn read_u32(file: &mut File) -> Result<u32, String> {
    let mut buf = [0u8; 4];
    file.read_exact(&mut buf).map_err(io_err)?;
    Ok(u32::from_le_bytes(buf))
}

fn read_u64(file: &mut File) -> Result<u64, String> {
    let mut buf = [0u8; 8];
    file.read_exact(&mut buf).map_err(io_err)?;
    Ok(u64::from_le_bytes(buf))
}

fn read_utf16le(file: &mut File, char_count: usize) -> Result<String, String> {
    let byte_count = char_count * 2;
    let mut buf = vec![0u8; byte_count];
    file.read_exact(&mut buf).map_err(io_err)?;

    let u16s: Vec<u16> = buf.chunks_exact(2)
        .map(|c| u16::from_le_bytes([c[0], c[1]]))
        .collect();

    // null terminator 제거
    let end = u16s.iter().position(|&c| c == 0).unwrap_or(u16s.len());
    Ok(String::from_utf16_lossy(&u16s[..end]))
}

fn io_err(e: io::Error) -> String {
    format!("IO 오류: {}", e)
}
