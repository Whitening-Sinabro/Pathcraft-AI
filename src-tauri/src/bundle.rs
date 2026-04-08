//! POE Bundle 파일 리더
//!
//! *.bundle.bin 파일 포맷:
//! - Header (60 bytes): 압축/비압축 크기, 청크 정보, 압축 알고리즘
//! - Chunk sizes (chunk_count * 4 bytes): 각 청크의 압축 크기
//! - Compressed data: 청크별 Oodle 압축 데이터
//!
//! 참조: LibGGPK3/LibBundle3/Bundle.cs

use crate::oodle::OodleLib;
use std::io::{self, Read, Seek, SeekFrom};

const HEADER_SIZE: usize = 60;

/// Bundle 파일 헤더 (60 bytes, little-endian)
#[derive(Debug, Clone)]
pub struct BundleHeader {
    pub uncompressed_size: i32,
    pub compressed_size: i32,
    pub head_size: i32,
    pub compressor: i32,
    pub unknown: i32,
    pub uncompressed_size_long: i64,
    pub compressed_size_long: i64,
    pub chunk_count: i32,
    pub chunk_size: i32,
    pub unknown3: i32,
    pub unknown4: i32,
    pub unknown5: i32,
    pub unknown6: i32,
}

impl BundleHeader {
    fn read<R: Read>(r: &mut R) -> Result<Self, String> {
        let mut buf = [0u8; HEADER_SIZE];
        r.read_exact(&mut buf).map_err(|e| format!("Bundle 헤더 읽기 실패: {}", e))?;

        Ok(Self {
            uncompressed_size: i32::from_le_bytes(buf[0..4].try_into().unwrap()),
            compressed_size: i32::from_le_bytes(buf[4..8].try_into().unwrap()),
            head_size: i32::from_le_bytes(buf[8..12].try_into().unwrap()),
            compressor: i32::from_le_bytes(buf[12..16].try_into().unwrap()),
            unknown: i32::from_le_bytes(buf[16..20].try_into().unwrap()),
            uncompressed_size_long: i64::from_le_bytes(buf[20..28].try_into().unwrap()),
            compressed_size_long: i64::from_le_bytes(buf[28..36].try_into().unwrap()),
            chunk_count: i32::from_le_bytes(buf[36..40].try_into().unwrap()),
            chunk_size: i32::from_le_bytes(buf[40..44].try_into().unwrap()),
            unknown3: i32::from_le_bytes(buf[44..48].try_into().unwrap()),
            unknown4: i32::from_le_bytes(buf[48..52].try_into().unwrap()),
            unknown5: i32::from_le_bytes(buf[52..56].try_into().unwrap()),
            unknown6: i32::from_le_bytes(buf[56..60].try_into().unwrap()),
        })
    }

    /// 마지막 청크의 비압축 크기
    fn last_chunk_size(&self) -> i32 {
        self.uncompressed_size - (self.chunk_size * (self.chunk_count - 1))
    }

    /// 헤더 유효성 검증
    fn validate(&self) -> Result<(), String> {
        if self.chunk_count < 0 {
            return Err(format!("chunk_count 음수: {}", self.chunk_count));
        }
        if self.chunk_size <= 0 && self.chunk_count > 0 {
            return Err(format!("chunk_size 비정상: {}", self.chunk_size));
        }
        if self.uncompressed_size < 0 {
            return Err(format!("uncompressed_size 음수: {}", self.uncompressed_size));
        }
        if self.compressed_size < 0 {
            return Err(format!("compressed_size 음수: {}", self.compressed_size));
        }
        if self.head_size < 0 {
            return Err(format!("head_size 음수: {}", self.head_size));
        }
        // chunk_count와 uncompressed_size 일관성 (마지막 청크 크기가 양수여야 함)
        if self.chunk_count > 0 && self.last_chunk_size() <= 0 {
            return Err(format!(
                "마지막 청크 크기 비정상: uncompressed={}, chunk_size={}, count={}",
                self.uncompressed_size, self.chunk_size, self.chunk_count
            ));
        }
        Ok(())
    }
}

/// Bundle 전체 데이터를 읽고 압축 해제
pub fn decompress_bundle<R: Read + Seek>(
    reader: &mut R,
    oodle: &OodleLib,
) -> Result<Vec<u8>, String> {
    reader.seek(SeekFrom::Start(0)).map_err(|e| format!("Seek 실패: {}", e))?;

    let header = BundleHeader::read(reader)?;

    if header.chunk_count == 0 || header.uncompressed_size == 0 {
        return Ok(Vec::new());
    }

    header.validate()?;

    log::info!(
        "Bundle: {}B 압축 → {}B 비압축, {} 청크 ({}KB), compressor={}",
        header.compressed_size,
        header.uncompressed_size,
        header.chunk_count,
        header.chunk_size / 1024,
        header.compressor,
    );

    // 각 청크의 압축 크기 읽기
    let chunk_count = header.chunk_count as usize;
    let mut chunk_sizes = Vec::with_capacity(chunk_count);
    for _ in 0..chunk_count {
        let mut buf = [0u8; 4];
        reader.read_exact(&mut buf).map_err(|e| format!("청크 크기 읽기 실패: {}", e))?;
        chunk_sizes.push(i32::from_le_bytes(buf) as usize);
    }

    // 데이터 시작 오프셋 = 12 + head_size
    let data_offset = 12u64 + header.head_size as u64;
    reader.seek(SeekFrom::Start(data_offset))
        .map_err(|e| format!("데이터 영역 Seek 실패: {}", e))?;

    // 전체 비압축 결과 버퍼
    let total_size = header.uncompressed_size as usize;
    let mut result = vec![0u8; total_size];
    let chunk_size = header.chunk_size as usize;
    let last_chunk_size = header.last_chunk_size() as usize;

    // 청크별 압축 해제
    let max_compressed = chunk_sizes.iter().copied().max().unwrap_or(0);
    let mut compressed_buf = vec![0u8; max_compressed];

    for i in 0..chunk_count {
        let comp_size = chunk_sizes[i];
        reader
            .read_exact(&mut compressed_buf[..comp_size])
            .map_err(|e| format!("청크 {} 데이터 읽기 실패: {}", i, e))?;

        let dst_offset = i * chunk_size;
        let expected_size = if i == chunk_count - 1 {
            last_chunk_size
        } else {
            chunk_size
        };

        let decompressed = oodle.decompress(
            &compressed_buf[..comp_size],
            &mut result[dst_offset..dst_offset + expected_size],
        )?;

        if decompressed != expected_size {
            return Err(format!(
                "청크 {} 크기 불일치: expected={}, got={}",
                i, expected_size, decompressed
            ));
        }
    }

    Ok(result)
}

/// 메모리 상의 번들 데이터를 압축 해제
pub fn decompress_bundle_from_bytes(data: &[u8], oodle: &OodleLib) -> Result<Vec<u8>, String> {
    let mut cursor = io::Cursor::new(data);
    decompress_bundle(&mut cursor, oodle)
}

/// Bundle의 일부분만 읽기 (offset~offset+length)
pub fn read_bundle_slice<R: Read + Seek>(
    reader: &mut R,
    oodle: &OodleLib,
    offset: usize,
    length: usize,
) -> Result<Vec<u8>, String> {
    // 전체 압축 해제 후 슬라이스 (최적화는 추후)
    let full = decompress_bundle(reader, oodle)?;
    if offset + length > full.len() {
        return Err(format!(
            "범위 초과: offset={}, length={}, total={}",
            offset, length, full.len()
        ));
    }
    Ok(full[offset..offset + length].to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn header_size_is_60() {
        assert_eq!(HEADER_SIZE, 60);
    }

    fn make_header_bytes(
        uncompressed: i32, compressed: i32, head_size: i32,
        compressor: i32, chunk_count: i32, chunk_size: i32,
    ) -> [u8; HEADER_SIZE] {
        let mut buf = [0u8; HEADER_SIZE];
        buf[0..4].copy_from_slice(&uncompressed.to_le_bytes());
        buf[4..8].copy_from_slice(&compressed.to_le_bytes());
        buf[8..12].copy_from_slice(&head_size.to_le_bytes());
        buf[12..16].copy_from_slice(&compressor.to_le_bytes());
        buf[16..20].copy_from_slice(&1i32.to_le_bytes()); // unknown
        buf[20..28].copy_from_slice(&(uncompressed as i64).to_le_bytes());
        buf[28..36].copy_from_slice(&(compressed as i64).to_le_bytes());
        buf[36..40].copy_from_slice(&chunk_count.to_le_bytes());
        buf[40..44].copy_from_slice(&chunk_size.to_le_bytes());
        buf
    }

    #[test]
    fn header_read_valid() {
        let bytes = make_header_bytes(1024, 512, 52, 13, 1, 262144);
        let header = BundleHeader::read(&mut &bytes[..]).unwrap();
        assert_eq!(header.uncompressed_size, 1024);
        assert_eq!(header.compressed_size, 512);
        assert_eq!(header.compressor, 13); // Leviathan
        assert_eq!(header.chunk_count, 1);
        assert_eq!(header.chunk_size, 262144);
    }

    #[test]
    fn header_validate_rejects_negative_chunk_count() {
        let bytes = make_header_bytes(1024, 512, 52, 13, -1, 262144);
        let header = BundleHeader::read(&mut &bytes[..]).unwrap();
        assert!(header.validate().is_err());
    }

    #[test]
    fn header_validate_rejects_zero_chunk_size() {
        let bytes = make_header_bytes(1024, 512, 52, 13, 4, 0);
        let header = BundleHeader::read(&mut &bytes[..]).unwrap();
        assert!(header.validate().is_err());
    }

    #[test]
    fn header_validate_rejects_negative_uncompressed() {
        let bytes = make_header_bytes(-1, 512, 52, 13, 1, 262144);
        let header = BundleHeader::read(&mut &bytes[..]).unwrap();
        assert!(header.validate().is_err());
    }

    #[test]
    fn header_validate_passes_valid() {
        let bytes = make_header_bytes(262144, 100000, 52, 13, 1, 262144);
        let header = BundleHeader::read(&mut &bytes[..]).unwrap();
        assert!(header.validate().is_ok());
    }

    #[test]
    fn header_read_too_short() {
        let bytes = [0u8; 30]; // 60바이트 미만
        assert!(BundleHeader::read(&mut &bytes[..]).is_err());
    }
}
