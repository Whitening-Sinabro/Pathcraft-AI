# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import base64
import zlib
import xml.etree.ElementTree as ET
import json
import sys
import os
import re
import logging

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("pob_parser")
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

# Stats는 POB XML의 <PlayerStat> 요소를 직접 파싱하여 추출한다 (parse_pob_xml 내부).
# 이전에 pobapi 패키지 기반 "정확 계산" 경로가 존재했으나 pobapi 0.5.0 API
# 호환성 문제로 항상 fallback 되는 dead code였다. XML 경로는 Phase B/D/E 및
# 17건 E2E 테스트로 검증됨 → pobapi 통합 제거, XML이 유일한 production path.

try:
    from src.utils import resource_path
except ImportError:
    def resource_path(relative_path):
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

TEST_POB_URL = "https://pobb.in/wXVStDuZrqHX"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_pob_code_from_url(pob_url):
    logger.info(f"1. POB URL에서 데이터 추출 중: {pob_url}")
    try:
        # file:// 프로토콜 처리 (로컬 POB XML 파일)
        if pob_url.startswith('file://'):
            file_path = pob_url[7:]  # file:// 제거
            # Windows 경로 처리 (file:///D:/path 또는 file://D:/path)
            if file_path.startswith('/') and len(file_path) > 2 and file_path[2] == ':':
                file_path = file_path[1:]  # 앞의 / 제거
            logger.info(f"   > Local file detected: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # XML 파일인 경우 직접 반환 (decode_pob_code 건너뛰기 위해 특수 마커 사용)
            if '<PathOfBuilding' in content or '<Build' in content:
                return f"__XML_DIRECT__{content}"
            else:
                # POB 코드일 수 있음
                return content.strip()

        # pastebin.com/raw/ URL 처리
        if 'pastebin.com' in pob_url and '/raw/' not in pob_url:
            # pastebin.com/xxxxxxxx -> pastebin.com/raw/xxxxxxxx
            pob_url = pob_url.replace('pastebin.com/', 'pastebin.com/raw/')
            logger.info(f"   > Pastebin URL detected, using raw: {pob_url}")

        # pobb.in은 간헐적으로 느림 — 30초 타임아웃 + 타임아웃 시 1회 재시도.
        # 커넥션 에러/4xx/5xx는 재시도하지 않음 (서버 문제는 반복해도 소용 없음).
        response = None
        last_timeout: requests.exceptions.Timeout | None = None
        for attempt in range(2):
            try:
                response = requests.get(pob_url, headers=HEADERS, timeout=30)
                break
            except requests.exceptions.Timeout as e:
                last_timeout = e
                if attempt == 0:
                    logger.warning(f"   > 타임아웃 (30s), 재시도 중...")
                    continue
                raise
        if response is None:
            # 루프 끝났는데 response 없음 = 모든 시도 타임아웃 (raise 이후 못 옴, 방어적)
            raise last_timeout if last_timeout else RuntimeError("요청 실패")
        response.raise_for_status()

        # pastebin.com/raw는 직접 텍스트 반환
        if 'pastebin.com/raw/' in pob_url:
            return response.text.strip()

        # pobb.in은 HTML 파싱 필요
        soup = BeautifulSoup(response.content, 'html.parser')
        code_element = soup.find('textarea')
        return code_element.text.strip() if code_element else None
    except requests.exceptions.Timeout as e:
        logger.error(f"   > POB URL 타임아웃 (30s × 2회): {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"   > POB URL 네트워크 에러: {e}")
        return None
    except (OSError, IOError) as e:
        logger.error(f"   > POB URL 파일/IO 에러: {e}")
        return None

def decode_pob_code(encoded_code):
    logger.info("2. 데이터 디코딩 및 압축 해제 중...")
    try:
        corrected_code = encoded_code.replace('-', '+').replace('_', '/')
        decoded_bytes = base64.b64decode(corrected_code)
        return zlib.decompress(decoded_bytes).decode('utf-8')
    except Exception as e:
        logger.error(f"   > 코드 디코딩 실패: {e}")
        return None

def parse_pob_xml(xml_string, pob_url):
    logger.info("3. XML 데이터 파싱 및 최종 JSON으로 가공 중...")
    try:
        root = ET.fromstring(xml_string)
        build = root.find('Build')
        skills_element = root.find('Skills')
        tree_element = root.find('Tree')
        items_element = root.find('Items')
        notes_element = root.find('Notes')

        if build is None: return None
        build_notes = notes_element.text.strip() if notes_element is not None and notes_element.text else ""

        # 스킬 젬 정보 추출 — active SkillSet은 primary(엔드게임), 나머지는 alternate(레벨링/전환용)
        def _extract_gems_from_skills(skill_nodes):
            """Skill 노드 리스트 → {label: {links, reasoning}} 딕셔너리."""
            result = {}
            for skill_set in skill_nodes:
                if skill_set.get('enabled', 'false').lower() != 'true':
                    continue
                gems = skill_set.findall('Gem')
                if not gems:
                    continue
                label = (skill_set.get('label') or gems[0].get('nameSpec', 'Unnamed')).strip()
                gem_links = " - ".join([gem.get('nameSpec') for gem in gems])
                if label:
                    result[label] = {"links": gem_links, "reasoning": None}
            return result

        gem_setups = {}
        alternate_gem_sets: dict[str, dict] = {}  # 비활성 SkillSet (레벨링 등)

        if skills_element is not None:
            active_skill_set_id = skills_element.get('activeSkillSet')
            all_skill_sets = skills_element.findall('./SkillSet')

            if all_skill_sets:
                for ss in all_skill_sets:
                    ss_id = ss.get('id', '')
                    ss_title = (ss.get('title') or f'SkillSet {ss_id}').strip()
                    ss_skills = ss.findall('Skill')
                    extracted = _extract_gems_from_skills(ss_skills)
                    if not extracted:
                        continue
                    if ss_id == active_skill_set_id:
                        gem_setups = extracted
                        logger.info("활성 SkillSet id=%s 제목=%r — %d개 스킬 그룹",
                                    ss_id, ss_title, len(extracted))
                    else:
                        alternate_gem_sets[ss_title] = extracted
                        logger.info("보조 SkillSet id=%s 제목=%r — %d개 스킬 그룹",
                                    ss_id, ss_title, len(extracted))
            else:
                # SkillSet 구조 없는 구 POB — 직계 Skill만
                gem_setups = _extract_gems_from_skills(skills_element.findall('./Skill'))
        
        # [최종 수정] 슬롯 중심의 장비 정보 추출 로직
        gear = {}
        if items_element is not None:
            item_map = {item.get('id'): item.text.strip() for item in items_element.findall('.//Item') if item.text and item.get('id')}
            active_set_id = items_element.get('activeItemSet', '1')
            item_set = items_element.find(f".//ItemSet[@id='{active_set_id}']")
            if item_set is None: item_set = items_element.find(".//ItemSet")

            if item_set is not None:
                # <Slot name="Weapon 1" itemId="1"/> 와 같은 태그를 찾음
                for slot in item_set.findall('Slot'):
                    slot_name = slot.get('name')
                    item_id = slot.get('itemId')

                    item_raw_text = item_map.get(item_id)
                    if slot_name and item_raw_text:
                        lines = item_raw_text.split('\n')
                        if len(lines) > 1:
                            item_name = lines[1].strip()
                            rarity = "Unknown"
                            base_type = ""
                            mods = []
                            sockets = ""

                            # Rarity 추출
                            if "Rarity: UNIQUE" in lines[0]:
                                rarity = "Unique"
                                if len(lines) > 2:
                                    base_type = lines[2].strip()
                            elif "Rarity: RARE" in lines[0] or "Rarity: Rare" in lines[0]:
                                rarity = "Rare"
                                if len(lines) > 2:
                                    base_type = lines[2].strip()
                                    item_name = f"{lines[1].strip()} ({base_type})"
                            elif "Rarity: MAGIC" in lines[0] or "Rarity: Magic" in lines[0]:
                                rarity = "Magic"
                                if len(lines) > 2: item_name = f"{lines[1].strip()} ({lines[2].strip()})"
                            elif "Rarity: NORMAL" in lines[0]:
                                rarity = "Normal"

                            # 모드 및 소켓 추출
                            for line in lines[2:]:
                                line = line.strip()
                                if not line:
                                    continue
                                # 소켓 정보
                                if line.startswith("Sockets:"):
                                    sockets = line.replace("Sockets:", "").strip()
                                # Unique ID 등 메타 정보 스킵
                                elif line.startswith("Unique ID:") or line.startswith("Item Level:") or line.startswith("LevelReq:") or line.startswith("Quality:"):
                                    continue
                                # 암묵 모드 카운터 스킵
                                elif line.startswith("Implicits:"):
                                    continue
                                # 기타 메타 정보 스킵
                                elif line in ["Corrupted", "Mirrored", "Split"]:
                                    continue
                                # BasePercentile 등 내부 데이터 스킵
                                elif "BasePercentile" in line:
                                    continue
                                else:
                                    # {mutated}, {crafted}, {fractured} 등의 태그 제거
                                    mod_line = line
                                    if line.startswith("{"):
                                        # {tag}content 형식에서 content만 추출
                                        close_brace = line.find("}")
                                        if close_brace != -1:
                                            mod_line = line[close_brace + 1:]

                                    # 주요 모드 키워드
                                    important_keywords = [
                                        "resistance", "life", "energy shield", "armour", "evasion",
                                        "damage", "attack", "spell", "critical", "increased", "added",
                                        "grants", "has", "socketed", "level", "gems",
                                        "elemental", "chaos", "physical", "fire", "cold", "lightning",
                                        "leech", "regen", "block", "dodge", "suppress",
                                        "cannot", "only", "corrupted"
                                    ]

                                    # 키스톤 이름들 (Skin of the Lords 등에서 사용)
                                    keystones = [
                                        "iron will", "iron grip", "resolute technique", "ancestral bond",
                                        "avatar of fire", "blood magic", "conduit", "eldritch battery",
                                        "elemental equilibrium", "elemental overload", "ghost reaver",
                                        "mind over matter", "mortal conviction", "necromantic aegis",
                                        "pain attunement", "phase acrobatics", "point blank",
                                        "unwavering stance", "vaal pact", "zealot's oath",
                                        "chaos inoculation", "arrow dancing", "acrobatics"
                                    ]

                                    # 모드 또는 키스톤인지 확인
                                    mod_lower = mod_line.lower()
                                    if len(mod_line) > 2:
                                        if any(kw in mod_lower for kw in important_keywords) or mod_lower in keystones:
                                            mods.append(mod_line)

                            gear[slot_name] = {
                                "name": item_name,
                                "rarity": rarity,
                                "base_type": base_type,
                                "sockets": sockets,
                                "mods": mods[:10],  # 최대 10개 모드만 저장
                                "reasoning": None
                            }
                            
        # 패시브 트리 URL 추출 (변경 없음)
        passive_tree_url = ""
        if tree_element is not None:
            # activeSpec 속성 우선 (1차/2차/3차 다중 트리 대응) → 레거시 active='true' → 첫 Spec
            active_spec_id = tree_element.get('activeSpec')
            active_spec = None
            if active_spec_id:
                active_spec = tree_element.find(f"./Spec[@id='{active_spec_id}']")
            if active_spec is None:
                active_spec = tree_element.find("./Spec[@active='true']") or tree_element.find('Spec')
            if active_spec is not None:
                url_element = active_spec.find('URL')
                if url_element is not None and url_element.text:
                    passive_tree_url = url_element.text.strip()
                logger.info("활성 Tree Spec id=%s 제목=%r",
                            active_spec.get('id', '?'),
                            active_spec.get('title', ''))

        # 최종 JSON 데이터 조립
        asc_name = build.get('ascendClassName', 'Unknown')
        class_name = build.get('className', 'Unknown')
        level = build.get('level', 'N/A')
        build_name = f"{class_name} {asc_name} Lvl {level}"

        # XML의 <PlayerStat> 요소에서 직접 추출 (production stats path)
        xml_stats = {}
        for stat in root.findall('.//PlayerStat'):
            stat_name = stat.get('stat')
            stat_value = stat.get('value')
            if stat_name and stat_value:
                try:
                    xml_stats[stat_name] = float(stat_value)
                except ValueError:
                    xml_stats[stat_name] = 0

        # DPS 계산 (CombinedDPS > FullDPS > TotalDPS 순으로 사용)
        extracted_dps = (
            xml_stats.get('CombinedDPS', 0) or
            xml_stats.get('FullDPS', 0) or
            xml_stats.get('TotalDPS', 0) or
            xml_stats.get('TotalDotDPS', 0)
        )

        # Life/ES 추출
        extracted_life = xml_stats.get('Life', 0)
        extracted_es = xml_stats.get('EnergyShield', 0)
        extracted_ehp = extracted_life + extracted_es

        # 저항 추출
        extracted_resists = {
            "fire": int(xml_stats.get('FireResist', 0)),
            "cold": int(xml_stats.get('ColdResist', 0)),
            "lightning": int(xml_stats.get('LightningResist', 0)),
            "chaos": int(xml_stats.get('ChaosResist', 0))
        }

        # 방어 스탯 추출
        extracted_armour = xml_stats.get('Armour', 0)
        extracted_evasion = xml_stats.get('Evasion', 0)
        extracted_block = xml_stats.get('BlockChance', 0)
        extracted_spell_block = xml_stats.get('SpellBlockChance', 0)

        final_stats = {
            "dps": int(extracted_dps),
            "life": int(extracted_life),
            "energy_shield": int(extracted_es),
            "ehp": int(extracted_ehp),
            "resistances": extracted_resists,
            "armour": int(extracted_armour),
            "evasion": int(extracted_evasion),
            "block": int(extracted_block),
            "spell_block": int(extracted_spell_block)
        }

        final_guide = {
            "meta": {
                "build_name": build_name,
                "class": class_name,
                "ascendancy": asc_name,
                "pob_link": pob_url,
                "version": build.get('targetVersion'),
                "has_xml_stats": bool(xml_stats)
            },
            "build_notes": build_notes,
            "stats": final_stats,
            "overview": {"summary": "", "pros": [], "cons": []},
            "leveling": {"summary": "", "early_skills": [], "vendor_regex": {}},
            "progression_stages": [{
                "stage_name": "Final Build",
                "pob_link": pob_url,
                "passive_tree_url": passive_tree_url,
                "ascendancy_order": [],
                "gem_setups": gem_setups,
                "alternate_gem_sets": alternate_gem_sets,  # 레벨링/전환 SkillSet (비활성)
                "gear_recommendation": gear,
                "bandit": build.get('bandit'),
                "pantheon": {"major": build.get('pantheonMajorGod'), "minor": build.get('pantheonMinorGod')}
            }]
        }

        stats_source = "XML PlayerStat" if xml_stats else "empty (no PlayerStat found)"
        logger.info("   > POB 데이터 변환 완료 (stats source: %s)", stats_source)
        return final_guide
    except Exception as e:
        logger.error(f"   > XML 파싱 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import argparse, json, sys, os
    ap = argparse.ArgumentParser(description="POB 빌드 파서")
    ap.add_argument("url", nargs="?", help="POB URL (pobb.in, pastebin, etc.)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--export", type=str, help="export JSON path")
    # POE2 통합 D0 (backlog) — Rust Tauri 측이 --game poe1|poe2 전달. 현재는 POE1 전용 로직만
    # 동작하고 POE2 값은 warning 후 POE1 처리. POE2 POB 포맷 분기는 D1 별도.
    ap.add_argument("--game", choices=["poe1", "poe2"], default="poe1",
                    help="대상 게임 (POE2 POB 파싱 분기는 D1 에서 구현 예정)")
    args, _ = ap.parse_known_args()

    if args.game == "poe2":
        logger.warning("--game poe2 는 D0 단계에서 플래그만 수용 — POE1 POB 파서로 처리 (D1 미완)")

    if args.selftest:
        print("SELFTEST OK")
        sys.exit(0)

    if args.url:
        code = get_pob_code_from_url(args.url)
        if not code:
            print(json.dumps({"error": "POB 코드를 가져올 수 없습니다"}, ensure_ascii=False))
            sys.exit(1)
        xml_string = decode_pob_code(code)
        if not xml_string:
            print(json.dumps({"error": "POB 코드 디코딩 실패"}, ensure_ascii=False))
            sys.exit(1)
        result = parse_pob_xml(xml_string, args.url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    print(json.dumps({"error": "URL을 입력하세요. 예: python pob_parser.py https://pobb.in/..."}, ensure_ascii=False))
