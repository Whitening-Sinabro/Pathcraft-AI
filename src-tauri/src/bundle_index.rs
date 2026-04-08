//! POE Bundle Index 리더
//!
//! _.index.bin은 번들 파일 자체(Oodle 압축)이며, 압축 해제하면:
//! - BundleRecord 목록: 번들 경로 + 비압축 크기
//! - FileRecord 목록: path_hash → (bundle_index, offset, size)
//! - DirectoryRecord 목록 + 경로 압축 데이터
//!
//! 참조: LibGGPK3/LibBundle3/Index.cs

use crate::bundle;
use crate::ggpk::GgpkReader;
use crate::oodle::OodleLib;
use std::collections::HashMap;
use std::fs::File;
use std::io::{Cursor, Read};
use std::path::{Path, PathBuf};

/// 번들 레코드: 번들 파일 경로 + 비압축 크기
#[derive(Debug, Clone)]
pub struct BundleRecord {
    pub path: String,
    pub uncompressed_size: i32,
}

/// 파일 레코드: 해시 기반 파일 위치
#[derive(Debug, Clone)]
pub struct FileRecord {
    pub path_hash: u64,
    pub bundle_index: usize,
    pub offset: i32,
    pub size: i32,
    /// ParsePaths로 복원된 경로 (없으면 None)
    pub path: Option<String>,
}

/// 디렉토리 레코드 (20 bytes)
#[derive(Debug, Clone)]
struct DirectoryRecord {
    path_hash: u64,
    offset: i32,
    size: i32,
    _recursive_size: i32,
}

/// 해시 알고리즘 종류 (첫 번째 DirectoryRecord의 path_hash로 판별)
#[derive(Debug, Clone, Copy, PartialEq)]
enum HashAlgorithm {
    MurmurHash64A, // since 3.21.2
    FNV1a64,       // legacy
}

/// 번들 데이터 소스
enum BundleSource {
    /// Steam/Epic: Bundles2/ 디렉토리가 디스크에 있음
    Disk(PathBuf),
    /// Standalone: Content.ggpk 안에 Bundles2/가 있음 (GgpkReader 재사용)
    Ggpk(GgpkReader),
}

/// Bundle Index — 전체 파일 시스템 매핑
pub struct BundleIndex {
    pub bundles: Vec<BundleRecord>,
    files: HashMap<u64, FileRecord>,
    directories: Vec<DirectoryRecord>,
    directory_bundle_data: Vec<u8>,
    hash_algorithm: HashAlgorithm,
    source: BundleSource,
    /// 압축 해제된 번들 캐시 (bundle_index → decompressed data)
    bundle_cache: HashMap<usize, Vec<u8>>,
}

impl BundleIndex {
    /// POE 설치 경로에서 인덱스 로드 (자동 감지: Standalone GGPK vs Steam 디스크)
    pub fn load(poe_path: &Path, oodle: &OodleLib) -> Result<Self, String> {
        let bundles_dir = poe_path.join("Bundles2");
        let ggpk_path = poe_path.join("Content.ggpk");

        if bundles_dir.is_dir() {
            // Steam/Epic: 디스크에서 직접 읽기
            Self::load_from_disk(&bundles_dir, oodle)
        } else if ggpk_path.exists() {
            // Standalone: GGPK에서 추출
            Self::load_from_ggpk(poe_path, oodle)
        } else {
            Err(format!(
                "Bundles2/ 디렉토리도 Content.ggpk도 없음: {}",
                poe_path.display()
            ))
        }
    }

    /// Steam/Epic: 디스크의 Bundles2/ 디렉토리에서 로드
    fn load_from_disk(bundles_dir: &Path, oodle: &OodleLib) -> Result<Self, String> {
        let index_path = bundles_dir.join("_.index.bin");
        if !index_path.exists() {
            return Err(format!("_.index.bin 없음: {}", index_path.display()));
        }

        log::info!("Bundle index (디스크): {}", index_path.display());

        let mut file = File::open(&index_path)
            .map_err(|e| format!("_.index.bin 열기 실패: {}", e))?;
        let data = bundle::decompress_bundle(&mut file, oodle)?;
        log::info!("Index 압축 해제: {} bytes", data.len());

        Self::parse_index(&data, BundleSource::Disk(bundles_dir.to_path_buf()))
    }

    /// Standalone: Content.ggpk에서 _.index.bin 추출 후 로드
    fn load_from_ggpk(poe_path: &Path, oodle: &OodleLib) -> Result<Self, String> {
        let ggpk_path = poe_path.join("Content.ggpk");
        log::info!("Bundle index (GGPK): {}", ggpk_path.display());

        let mut ggpk = GgpkReader::open(&ggpk_path)?;
        let index_data = ggpk.extract("bundles2/_.index.bin")?;
        log::info!("GGPK에서 _.index.bin 추출: {} bytes", index_data.len());

        let decompressed = bundle::decompress_bundle_from_bytes(&index_data, oodle)?;
        log::info!("Index 압축 해제: {} bytes", decompressed.len());

        // GgpkReader를 BundleSource에 보관 — 이후 번들 추출 시 재사용
        Self::parse_index(&decompressed, BundleSource::Ggpk(ggpk))
    }

    /// 압축 해제된 인덱스 데이터를 파싱
    fn parse_index(data: &[u8], source: BundleSource) -> Result<Self, String> {
        let mut cursor = Cursor::new(data);

        // 1. Bundle records
        let bundle_count = validated_count(read_i32(&mut cursor)?, "bundle_count")?;
        let mut bundles = Vec::with_capacity(bundle_count);
        for _ in 0..bundle_count {
            let path_length = read_i32(&mut cursor)? as usize;
            let mut path_bytes = vec![0u8; path_length];
            cursor
                .read_exact(&mut path_bytes)
                .map_err(|e| format!("번들 경로 읽기 실패: {}", e))?;
            let path = String::from_utf8_lossy(&path_bytes).to_string();
            let uncompressed_size = read_i32(&mut cursor)?;
            bundles.push(BundleRecord {
                path,
                uncompressed_size,
            });
        }
        log::info!("번들 레코드: {} 개", bundles.len());

        // 2. File records
        let file_count = validated_count(read_i32(&mut cursor)?, "file_count")?;
        let mut files = HashMap::with_capacity(file_count);
        for _ in 0..file_count {
            let path_hash = read_u64(&mut cursor)?;
            let bundle_index = read_i32(&mut cursor)? as usize;
            let offset = read_i32(&mut cursor)?;
            let size = read_i32(&mut cursor)?;
            files.insert(
                path_hash,
                FileRecord {
                    path_hash,
                    bundle_index,
                    offset,
                    size,
                    path: None,
                },
            );
        }
        log::info!("파일 레코드: {} 개", files.len());

        // 3. Directory records (20 bytes each)
        let directory_count = validated_count(read_i32(&mut cursor)?, "directory_count")?;
        let mut directories = Vec::with_capacity(directory_count);
        for _ in 0..directory_count {
            let path_hash = read_u64(&mut cursor)?;
            let offset = read_i32(&mut cursor)?;
            let size = read_i32(&mut cursor)?;
            let recursive_size = read_i32(&mut cursor)?;
            directories.push(DirectoryRecord {
                path_hash,
                offset,
                size,
                _recursive_size: recursive_size,
            });
        }
        log::info!("디렉토리 레코드: {} 개", directories.len());

        // 4. 나머지 = directory bundle data (경로 압축 데이터)
        let pos = cursor.position() as usize;
        let directory_bundle_data = data[pos..].to_vec();
        log::info!("디렉토리 번들 데이터: {} bytes", directory_bundle_data.len());

        // 해시 알고리즘 판별
        let hash_algorithm = if !directories.is_empty()
            && directories[0].path_hash == 0xF42A_94E6_9CFF_42FE
        {
            HashAlgorithm::MurmurHash64A
        } else {
            HashAlgorithm::FNV1a64
        };
        log::info!("해시 알고리즘: {:?}", hash_algorithm);

        Ok(Self {
            bundles,
            files,
            directories,
            directory_bundle_data,
            hash_algorithm,
            source,
            bundle_cache: HashMap::new(),
        })
    }

    /// 경로 해시 계산
    pub fn name_hash(&self, path: &str) -> u64 {
        let lower = path.to_lowercase();
        let utf8 = lower.as_bytes();
        match self.hash_algorithm {
            HashAlgorithm::MurmurHash64A => murmur_hash_64a(utf8),
            HashAlgorithm::FNV1a64 => fnv1a_64_hash(utf8),
        }
    }

    /// 경로로 파일 레코드 찾기
    pub fn find_file(&self, path: &str) -> Option<&FileRecord> {
        let hash = self.name_hash(path);
        self.files.get(&hash)
    }

    /// 파일 수
    pub fn file_count(&self) -> usize {
        self.files.len()
    }

    /// 파일 데이터 추출 (번들 캐시 활용)
    pub fn extract_file(&mut self, file: &FileRecord, oodle: &OodleLib) -> Result<Vec<u8>, String> {
        let bundle_idx = file.bundle_index;

        // 캐시에 없으면 읽기 + 압축 해제 후 캐시
        if !self.bundle_cache.contains_key(&bundle_idx) {
            let bundle_record = self
                .bundles
                .get(bundle_idx)
                .ok_or_else(|| format!("잘못된 bundle_index: {}", bundle_idx))?
                .clone();

            let bundle_data = self.read_bundle_raw(&bundle_record)?;
            let decompressed = bundle::decompress_bundle_from_bytes(&bundle_data, oodle)?;

            log::info!(
                "번들 #{} 압축 해제 → 캐시 ({}KB)",
                bundle_idx,
                decompressed.len() / 1024
            );
            self.bundle_cache.insert(bundle_idx, decompressed);
        } else {
            log::debug!("번들 #{} 캐시 히트", bundle_idx);
        }

        let decompressed = &self.bundle_cache[&bundle_idx];
        let offset = file.offset as usize;
        let size = file.size as usize;
        if offset + size > decompressed.len() {
            return Err(format!(
                "파일 범위 초과: offset={}, size={}, bundle_size={}",
                offset,
                size,
                decompressed.len()
            ));
        }

        Ok(decompressed[offset..offset + size].to_vec())
    }

    /// 번들 캐시 비우기 (메모리 해제)
    pub fn clear_cache(&mut self) {
        let count = self.bundle_cache.len();
        let bytes: usize = self.bundle_cache.values().map(|v| v.len()).sum();
        self.bundle_cache.clear();
        log::info!("번들 캐시 해제: {} 개, {}MB", count, bytes / (1024 * 1024));
    }

    /// 캐시된 번들 수
    pub fn cached_bundle_count(&self) -> usize {
        self.bundle_cache.len()
    }

    /// 번들 원본 데이터 읽기 (소스에 따라 분기)
    fn read_bundle_raw(&mut self, bundle_record: &BundleRecord) -> Result<Vec<u8>, String> {
        match &mut self.source {
            BundleSource::Disk(bundles_dir) => {
                let bundle_path = bundles_dir.join(format!("{}.bundle.bin", bundle_record.path));
                if !bundle_path.exists() {
                    return Err(format!("번들 파일 없음: {}", bundle_path.display()));
                }
                std::fs::read(&bundle_path)
                    .map_err(|e| format!("번들 읽기 실패: {}", e))
            }
            BundleSource::Ggpk(ggpk) => {
                let ggpk_bundle_path = format!("bundles2/{}.bundle.bin", bundle_record.path);
                ggpk.extract(&ggpk_bundle_path)
            }
        }
    }

    /// 경로로 파일 데이터 추출
    pub fn extract_by_path(&mut self, path: &str, oodle: &OodleLib) -> Result<Vec<u8>, String> {
        let file = self
            .find_file(path)
            .ok_or_else(|| format!("파일 없음: {}", path))?
            .clone();
        self.extract_file(&file, oodle)
    }

    /// 디렉토리 번들 데이터에서 경로 복원 (ParsePaths)
    pub fn parse_paths(&mut self, oodle: &OodleLib) -> Result<usize, String> {
        if self.directory_bundle_data.is_empty() {
            return Ok(0);
        }

        // directory_bundle_data 자체가 번들 → 압축 해제
        let dir_data = bundle::decompress_bundle_from_bytes(&self.directory_bundle_data, oodle)?;
        log::info!("디렉토리 경로 데이터 압축 해제: {} bytes", dir_data.len());

        let mut resolved = 0usize;
        let mut failed = 0usize;

        for dir in &self.directories {
            let offset = dir.offset as usize;
            let size = dir.size as usize;
            if offset + size > dir_data.len() {
                log::warn!(
                    "디렉토리 범위 초과: offset={}, size={}, total={}",
                    offset,
                    size,
                    dir_data.len()
                );
                continue;
            }

            let chunk = &dir_data[offset..offset + size];
            let paths = decode_path_rep(chunk);

            for path_bytes in paths {
                let hash = match self.hash_algorithm {
                    HashAlgorithm::MurmurHash64A => murmur_hash_64a(&path_bytes),
                    HashAlgorithm::FNV1a64 => fnv1a_64_hash(&path_bytes),
                };
                if let Some(file) = self.files.get_mut(&hash) {
                    file.path = Some(String::from_utf8_lossy(&path_bytes).to_string());
                    resolved += 1;
                } else {
                    failed += 1;
                }
            }
        }

        log::info!(
            "경로 복원: {} 성공, {} 실패 (전체 {})",
            resolved,
            failed,
            self.files.len()
        );
        Ok(failed)
    }

    /// 경로가 복원된 파일 중 특정 확장자 필터
    pub fn list_files_by_ext(&self, ext: &str) -> Vec<&FileRecord> {
        self.files
            .values()
            .filter(|f| {
                f.path
                    .as_ref()
                    .map(|p| p.ends_with(ext))
                    .unwrap_or(false)
            })
            .collect()
    }

    /// 모든 파일 레코드 반복자
    pub fn all_files(&self) -> impl Iterator<Item = &FileRecord> {
        self.files.values()
    }
}

/// 디렉토리 번들의 경로 압축 디코딩
///
/// 포맷: 인덱스 기반 문자열 조합
/// - index=0: base/non-base 모드 전환
/// - index>0: 이전 조각(temp[index-1])에 현재 문자열 연결
/// - null-terminated UTF-8 문자열
fn decode_path_rep(data: &[u8]) -> Vec<Vec<u8>> {
    let mut result = Vec::new();
    let mut temp: Vec<Vec<u8>> = Vec::new();
    let mut is_base = false;
    let mut pos = 0;

    while pos + 4 <= data.len() {
        let index = i32::from_le_bytes(data[pos..pos + 4].try_into().unwrap());
        pos += 4;

        if index == 0 {
            is_base = !is_base;
            if is_base {
                temp.clear();
            }
            continue;
        }

        // null-terminated 문자열 읽기
        let str_start = pos;
        while pos < data.len() && data[pos] != 0 {
            pos += 1;
        }
        let str_bytes = &data[str_start..pos];
        if pos < data.len() {
            pos += 1; // skip null terminator
        }

        let idx = (index - 1) as usize;
        if idx < temp.len() {
            // 이전 조각과 연결
            let mut combined = temp[idx].clone();
            combined.extend_from_slice(str_bytes);

            if is_base {
                temp.push(combined);
            } else {
                result.push(combined);
            }
        } else {
            // 새 조각
            let fragment = str_bytes.to_vec();
            if is_base {
                temp.push(fragment);
            } else {
                result.push(fragment);
            }
        }
    }

    result
}

// ── 해시 함수 ──────────────────────────────────────

/// MurmurHash64A (POE 3.21.2+)
/// 입력은 반드시 소문자 UTF-8이어야 함
fn murmur_hash_64a(data: &[u8]) -> u64 {
    if data.is_empty() {
        return 0xF42A_94E6_9CFF_42FE;
    }

    let mut key = data;
    // trailing '/' 제거
    if key.last() == Some(&b'/') {
        key = &key[..key.len() - 1];
    }

    const M: u64 = 0xC6A4_A793_5BD1_E995;
    const R: u32 = 47;
    let seed: u64 = 0x1337_B33F;

    let len = key.len();
    let mut h: u64 = seed ^ ((len as u64).wrapping_mul(M));

    // 8바이트 단위 처리
    let chunks = len / 8;
    for i in 0..chunks {
        let offset = i * 8;
        let k = u64::from_le_bytes(key[offset..offset + 8].try_into().unwrap());
        let k = k.wrapping_mul(M);
        let k = (k ^ (k >> R)).wrapping_mul(M);
        h = (h ^ k).wrapping_mul(M);
    }

    // 나머지 바이트
    let remaining = len % 8;
    if remaining > 0 {
        let offset = chunks * 8;
        let mut tail: u64 = 0;
        for i in 0..remaining {
            tail |= (key[offset + i] as u64) << (i * 8);
        }
        h = (h ^ tail).wrapping_mul(M);
    }

    // finalize
    h = (h ^ (h >> R)).wrapping_mul(M);
    h ^ (h >> R)
}

/// FNV-1a 64-bit (POE legacy, 3.21.2 이전)
fn fnv1a_64_hash(data: &[u8]) -> u64 {
    const FNV_OFFSET: u64 = 0xCBF2_9CE4_8422_2325;
    const FNV_PRIME: u64 = 0x0100_0000_01B3;

    let mut hash = FNV_OFFSET;

    let key = if data.last() == Some(&b'/') {
        // 디렉토리: trailing '/' 제거, 대소문자 변환 없음
        let trimmed = &data[..data.len() - 1];
        for &ch in trimmed {
            hash = (hash ^ ch as u64).wrapping_mul(FNV_PRIME);
        }
        // "++" 추가
        hash = (hash ^ b'+' as u64).wrapping_mul(FNV_PRIME);
        hash = (hash ^ b'+' as u64).wrapping_mul(FNV_PRIME);
        return hash;
    } else {
        data
    };

    for &ch in key {
        let c = if ch >= b'A' && ch <= b'Z' {
            // C# 원본: ch + (ulong)('A' - 'a') — wrapping subtract 32
            (ch as u64).wrapping_add(('A' as u64).wrapping_sub('a' as u64))
        } else {
            ch as u64
        };
        hash = (hash ^ c).wrapping_mul(FNV_PRIME);
    }

    // "++" 추가
    hash = (hash ^ b'+' as u64).wrapping_mul(FNV_PRIME);
    hash = (hash ^ b'+' as u64).wrapping_mul(FNV_PRIME);
    hash
}

// ── 유틸 ───────────────────────────────────────────

/// i32 카운트를 usize로 변환 (음수/비정상값 방어)
fn validated_count(value: i32, name: &str) -> Result<usize, String> {
    if value < 0 {
        return Err(format!("{} 음수: {}", name, value));
    }
    if value > 10_000_000 {
        return Err(format!("{} 비정상 (>10M): {}", name, value));
    }
    Ok(value as usize)
}

fn read_i32<R: Read>(r: &mut R) -> Result<i32, String> {
    let mut buf = [0u8; 4];
    r.read_exact(&mut buf)
        .map_err(|e| format!("i32 읽기 실패: {}", e))?;
    Ok(i32::from_le_bytes(buf))
}

fn read_u64<R: Read>(r: &mut R) -> Result<u64, String> {
    let mut buf = [0u8; 8];
    r.read_exact(&mut buf)
        .map_err(|e| format!("u64 읽기 실패: {}", e))?;
    Ok(u64::from_le_bytes(buf))
}

#[cfg(test)]
mod tests {
    use super::*;

    // ── 해시 함수 ──────────────────────────────────

    #[test]
    fn murmur_empty_returns_sentinel() {
        assert_eq!(murmur_hash_64a(b""), 0xF42A_94E6_9CFF_42FE);
    }

    #[test]
    fn murmur_deterministic() {
        let h1 = murmur_hash_64a(b"data/baseitemtypes.datc64");
        let h2 = murmur_hash_64a(b"data/baseitemtypes.datc64");
        assert_eq!(h1, h2);
        assert_ne!(h1, 0);
    }

    #[test]
    fn murmur_trailing_slash_trimmed() {
        let h1 = murmur_hash_64a(b"data/monsters");
        let h2 = murmur_hash_64a(b"data/monsters/");
        assert_eq!(h1, h2);
    }

    #[test]
    fn murmur_different_inputs_differ() {
        let h1 = murmur_hash_64a(b"data/a.datc64");
        let h2 = murmur_hash_64a(b"data/b.datc64");
        assert_ne!(h1, h2);
    }

    #[test]
    fn fnv1a_deterministic() {
        let h1 = fnv1a_64_hash(b"data/baseitemtypes.datc64");
        let h2 = fnv1a_64_hash(b"data/baseitemtypes.datc64");
        assert_eq!(h1, h2);
        assert_ne!(h1, 0);
    }

    #[test]
    fn fnv1a_trailing_slash_trimmed() {
        let h1 = fnv1a_64_hash(b"data/monsters/");
        let h2 = fnv1a_64_hash(b"data/monsters/");
        assert_eq!(h1, h2);
    }

    // ── decode_path_rep ────────────────────────────

    #[test]
    fn decode_path_rep_empty() {
        let result = decode_path_rep(&[]);
        assert!(result.is_empty());
    }

    #[test]
    fn decode_path_rep_simple_paths() {
        // 구조: [0] base_mode_on, [1, "data/"], [0] base_mode_off, [1, "test.txt"]
        let mut data = Vec::new();
        // index=0 → base mode ON
        data.extend_from_slice(&0i32.to_le_bytes());
        // index=1, string="data/"
        data.extend_from_slice(&1i32.to_le_bytes());
        data.extend_from_slice(b"data/\0");
        // index=0 → base mode OFF
        data.extend_from_slice(&0i32.to_le_bytes());
        // index=1 (base[0]="data/" + "test.txt")
        data.extend_from_slice(&1i32.to_le_bytes());
        data.extend_from_slice(b"test.txt\0");

        let result = decode_path_rep(&data);
        assert_eq!(result.len(), 1);
        assert_eq!(result[0], b"data/test.txt");
    }

    #[test]
    fn decode_path_rep_multiple_files_same_base() {
        let mut data = Vec::new();
        // base mode ON
        data.extend_from_slice(&0i32.to_le_bytes());
        // base[0] = "art/"
        data.extend_from_slice(&1i32.to_le_bytes());
        data.extend_from_slice(b"art/\0");
        // base mode OFF
        data.extend_from_slice(&0i32.to_le_bytes());
        // file = base[0] + "a.png"
        data.extend_from_slice(&1i32.to_le_bytes());
        data.extend_from_slice(b"a.png\0");
        // file = base[0] + "b.png"
        data.extend_from_slice(&1i32.to_le_bytes());
        data.extend_from_slice(b"b.png\0");

        let result = decode_path_rep(&data);
        assert_eq!(result.len(), 2);
        assert_eq!(result[0], b"art/a.png");
        assert_eq!(result[1], b"art/b.png");
    }

    // ── validated_count ────────────────────────────

    #[test]
    fn validated_count_rejects_negative() {
        assert!(validated_count(-1, "test").is_err());
    }

    #[test]
    fn validated_count_rejects_huge() {
        assert!(validated_count(99_999_999, "test").is_err());
    }

    #[test]
    fn validated_count_accepts_valid() {
        assert_eq!(validated_count(1000, "test").unwrap(), 1000);
        assert_eq!(validated_count(0, "test").unwrap(), 0);
    }
}
