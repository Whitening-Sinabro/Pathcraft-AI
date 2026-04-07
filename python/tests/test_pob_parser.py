# -*- coding: utf-8 -*-
"""pob_parser 핵심 함수 스모크 테스트"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pob_parser import decode_pob_code, parse_pob_xml, get_pob_code_from_url


class TestDecodePobCode:
    """decode_pob_code: base64+zlib 디코딩"""

    def test_valid_code_returns_xml(self):
        """유효한 POB 코드 → XML 문자열 반환"""
        import base64
        import zlib

        xml = '<?xml version="1.0"?><PathOfBuilding><Build></Build></PathOfBuilding>'
        compressed = zlib.compress(xml.encode("utf-8"))
        encoded = base64.b64encode(compressed).decode("ascii")
        # POB URL-safe 인코딩
        encoded = encoded.replace("+", "-").replace("/", "_")

        result = decode_pob_code(encoded)
        assert result is not None
        assert "<PathOfBuilding>" in result

    def test_invalid_code_returns_none(self):
        """잘못된 코드 → None 반환 (크래시 안 남)"""
        result = decode_pob_code("this-is-not-valid-base64!!!")
        assert result is None

    def test_empty_code_returns_none(self):
        """빈 문자열 → None"""
        result = decode_pob_code("")
        assert result is None


class TestParsePobXml:
    """parse_pob_xml: XML → JSON 구조 변환"""

    def _minimal_xml(self):
        return """<?xml version="1.0"?>
<PathOfBuilding>
  <Build level="95" className="Witch" ascendClassName="Occultist" mainSocketGroup="1">
    <PlayerStat stat="Life" value="5200"/>
    <PlayerStat stat="EnergyShield" value="1000"/>
    <PlayerStat stat="CombinedDPS" value="150000"/>
  </Build>
  <Skills>
    <Skill mainActiveSkill="1" label="Main">
      <Gem nameSpec="Essence Drain" level="20" quality="20" enabled="true" skillId="EssenceDrain"/>
    </Skill>
  </Skills>
  <Items/>
  <Tree activeSpec="1">
    <Spec treeVersion="3_25">
      <URL>https://www.pathofexile.com/passive-skill-tree/AAAA</URL>
    </Spec>
  </Tree>
</PathOfBuilding>"""

    def test_extracts_meta(self):
        """메타 정보 추출 (클래스, 승천)"""
        result = parse_pob_xml(self._minimal_xml(), "https://pobb.in/test")
        assert result is not None
        assert result["meta"]["class"] == "Witch"
        assert result["meta"]["ascendancy"] == "Occultist"

    def test_extracts_stats(self):
        """스탯 추출 (life, dps, es)"""
        result = parse_pob_xml(self._minimal_xml(), "https://pobb.in/test")
        assert result["stats"]["life"] == 5200
        assert result["stats"]["dps"] == 150000

    def test_malformed_xml_returns_error(self):
        """잘못된 XML → 에러 dict 반환 (크래시 아님)"""
        result = parse_pob_xml("<not><valid>xml", "https://pobb.in/test")
        assert result is None or "error" in str(result).lower() or result == {}


class TestGetPobCodeFromUrl:
    """get_pob_code_from_url: URL → POB 코드 추출 (네트워크 의존)"""

    def test_invalid_url_returns_none(self):
        """존재하지 않는 URL → None (크래시 아님)"""
        result = get_pob_code_from_url("https://pobb.in/nonexistent-build-12345xyz")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
