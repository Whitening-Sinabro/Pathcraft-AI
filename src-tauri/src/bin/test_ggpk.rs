//! GGPK 리더 실제 테스트 — Content.ggpk에서 .dat64 파일 추출

use std::path::Path;

// app_lib 모듈 참조
use app_lib::ggpk::GgpkReader;
use app_lib::dat64::Dat64Parser;

fn main() {
    let ggpk_path = Path::new(r"C:\Program Files (x86)\Grinding Gear Games\Path of Exile\Content.ggpk");

    if !ggpk_path.exists() {
        eprintln!("Content.ggpk 없음: {:?}", ggpk_path);
        return;
    }

    eprintln!("GGPK 로딩 중: {:?} (63GB, 시간 걸릴 수 있음)...", ggpk_path);

    match GgpkReader::open(ggpk_path) {
        Ok(mut reader) => {
            eprintln!("인덱스된 파일 수: {}", reader.file_count());

            // .dat64 파일 목록
            let dat64_files = reader.list_dat64();
            eprintln!("DAT64 파일 수: {}", dat64_files.len());

            // 파일 경로 패턴 확인
            let all_files = reader.list_dir("");
            eprintln!("\n루트 디렉토리 파일/폴더 (첫 20개):");
            let mut sorted: Vec<_> = all_files.iter().collect();
            sorted.sort();
            for f in sorted.iter().take(20) {
                eprintln!("  {}", f);
            }

            // Bundles2 확인
            let bundles = reader.list_dir("bundles2");
            eprintln!("\nBundles2/ 파일 수: {}", bundles.len());
            for f in bundles.iter().take(5) {
                eprintln!("  {}", f);
            }

            // .dat64 검색
            for f in dat64_files.iter().take(10) {
                eprintln!("  {}", f);
            }

            // _.index.bin 추출 시도
            let index_candidates = ["bundles2/_.index.bin", "bundles2/.index.bin"];
            for idx_path in &index_candidates {
                match reader.extract(idx_path) {
                    Ok(data) => {
                        eprintln!("\n_.index.bin 추출 성공: {} bytes", data.len());
                        // 헤더 덤프
                        eprintln!("  첫 64 bytes (hex):");
                        for chunk in data[..std::cmp::min(64, data.len())].chunks(16) {
                            let hex: String = chunk.iter().map(|b| format!("{:02x} ", b)).collect();
                            eprintln!("    {}", hex);
                        }
                        break;
                    }
                    Err(_) => {}
                }
            }

            // 아무 bundle.bin 하나 읽어서 헤더 확인
            let some_bundle = bundles.iter().find(|f| f.ends_with(".bundle.bin"));
            if let Some(bp) = some_bundle {
                match reader.extract(bp) {
                    Ok(data) => {
                        eprintln!("\n번들 헤더 확인: {} ({} bytes)", bp, data.len());
                        if data.len() >= 28 {
                            let uncomp_size = u32::from_le_bytes(data[0..4].try_into().unwrap());
                            let total_payload = u32::from_le_bytes(data[4..8].try_into().unwrap());
                            let head_payload = u32::from_le_bytes(data[8..12].try_into().unwrap());
                            eprintln!("  uncompressed_size: {}", uncomp_size);
                            eprintln!("  total_payload_size: {}", total_payload);
                            eprintln!("  head_payload_size: {}", head_payload);
                            if data.len() >= 16 {
                                let encode = u32::from_le_bytes(data[12..16].try_into().unwrap());
                                eprintln!("  first_file_encode: {} (8=Kraken, 9=Mermaid, 13=Leviathan)", encode);
                            }
                        }
                    }
                    Err(e) => eprintln!("번들 읽기 실패: {}", e),
                }
            }

            let targets = ["data/activeskills.dat64", "data/skillgems.dat64", "data/baseitemtypes.dat64", "data/maps.dat64"];
            for target in &targets {
                eprintln!("\n추출 시도: {}", target);
                match reader.extract(target) {
                    Ok(data) => {
                        eprintln!("  크기: {} bytes", data.len());
                        match Dat64Parser::load(data) {
                            Ok(parser) => {
                                eprintln!("  행 수: {}", parser.row_count());
                                eprintln!("  추정 행 크기: {} bytes", parser.estimated_row_size());
                            }
                            Err(e) => eprintln!("  DAT64 파싱 실패: {}", e),
                        }
                    }
                    Err(e) => eprintln!("  추출 실패: {}", e),
                }
            }
        }
        Err(e) => {
            eprintln!("GGPK 열기 실패: {}", e);
        }
    }
}
