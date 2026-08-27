# -*- coding: utf-8 -*-
"""Resolve external build source URLs into PoB and/or passive tree URLs."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0"}

POB_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:(?:pobb\.in|pastebin\.com(?:/raw)?|poe\.ninja/poe1/pob/raw|planners\.maxroll\.gg/profiles/load/poe)/[A-Za-z0-9/_-]+|poedb\.tw/(?:[a-z]{2}/)?pob/[A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
PASSIVE_URL_RE = re.compile(
    r"https?://(?:www\.)?pathofexile\.com/(?:fullscreen-)?passive-skill-tree/[A-Za-z0-9_-]+",
    re.IGNORECASE,
)
RELATIVE_TOOL_RE = re.compile(r"^/poe/(?:planner|pob)(?:[/?#][^\s\"'<>]*)?$", re.IGNORECASE)


def _http_get(url: str, *, timeout: int) -> requests.Response:
    try:
        return requests.get(url, timeout=timeout, headers=HEADERS)
    except requests.exceptions.ProxyError:
        session = requests.Session()
        session.trust_env = False
        return session.get(url, timeout=timeout, headers=HEADERS)


def _source_type_for_host(url: str) -> str:
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if "pobb.in" in host:
        return "pobb"
    if "pastebin.com" in host:
        return "pastebin"
    if "pathofexile.com" in host and "passive-skill-tree" in path:
        return "passive_tree"
    if "planners.maxroll.gg" in host and path.startswith("/profiles/load/poe/"):
        return "maxroll_profile_api"
    if "maxroll.gg" in host:
        if path.startswith("/poe/pob/"):
            return "maxroll_pob_page"
        if path.startswith("/poe/planner/"):
            return "maxroll_planner_page"
        return "maxroll"
    if "poe.ninja" in host:
        if path.startswith("/poe1/pob/raw/"):
            return "poe_ninja_pob_raw"
        if path.startswith("/poe1/pob/"):
            return "poe_ninja_pob_page"
    if "poedb.tw" in host:
        if re.fullmatch(r"/(?:[a-z]{2}/)?pob/[A-Za-z0-9_-]+/raw/?", path, re.IGNORECASE):
            return "poedb_pob_raw"
        if re.fullmatch(r"/(?:[a-z]{2}/)?pob/[A-Za-z0-9_-]+/?", path, re.IGNORECASE):
            return "poedb_pob_page"
        return "poedb"
    if url.startswith("file://"):
        return "file"
    return "webpage"


def _poedb_raw_url(url: str) -> str:
    parsed = urlparse(url)
    match = re.fullmatch(
        r"/(?:[a-z]{2}/)?pob/([A-Za-z0-9_-]+)(?:/raw)?/?",
        parsed.path,
        re.IGNORECASE,
    )
    if not match:
        return url
    return f"https://poedb.tw/pob/{match.group(1)}/raw"


def _normalize_pob_url(url: str) -> str:
    parsed = urlparse(url)
    if "pastebin.com" in parsed.netloc.lower() and "/raw/" not in parsed.path:
        path = parsed.path
        if path and path != "/":
            return f"{parsed.scheme}://{parsed.netloc}/raw{path}"
    if "poedb.tw" in parsed.netloc.lower():
        return _poedb_raw_url(url)
    return url


def _poe_ninja_raw_url(url: str) -> str:
    parsed = urlparse(url)
    code_id = parsed.path.strip("/").split("/")[-1]
    return f"{parsed.scheme}://{parsed.netloc}/poe1/pob/raw/{code_id}"


def _maxroll_profile_api_url(url: str) -> str:
    parsed = urlparse(url)
    code_id = parsed.path.strip("/").split("/")[-1]
    return f"https://planners.maxroll.gg/profiles/load/poe/{code_id}"


def _extract_title(soup: BeautifulSoup) -> str | None:
    og = soup.find("meta", attrs={"property": "og:title"})
    if og and og.get("content"):
        return og["content"].strip()
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None


def _looks_like_specific_maxroll_tool(url: str) -> bool:
    parsed = urlparse(url)
    if "maxroll.gg" not in parsed.netloc.lower():
        return False
    path = parsed.path.rstrip("/")
    return path.startswith("/poe/planner/") or path.startswith("/poe/pob/")


def _candidate_urls_from_html(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[str] = []
    seen: set[str] = set()

    def _push(raw_url: str | None) -> None:
        if not raw_url:
            return
        raw_url = unescape(raw_url.strip())
        if not raw_url:
            return
        if raw_url.startswith("//"):
            raw_url = "https:" + raw_url
        if raw_url.startswith("/"):
            raw_url = urljoin(base_url, raw_url)
        if raw_url in seen:
            return
        seen.add(raw_url)
        candidates.append(raw_url)

    for tag in soup.find_all(True):
        for attr in ("href", "src", "content", "data-href"):
            _push(tag.get(attr))

    for match in POB_URL_RE.finditer(html):
        _push(match.group(0))
    for match in PASSIVE_URL_RE.finditer(html):
        _push(match.group(0))

    for match in RELATIVE_TOOL_RE.finditer(html):
        _push(urljoin(base_url, match.group(0)))

    return candidates


def resolve_from_html(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = _extract_title(soup)
    canonical_tag = soup.find("link", rel="canonical")
    canonical_url = canonical_tag.get("href", url).strip() if canonical_tag else url

    candidates = _candidate_urls_from_html(url, html)
    pob_candidates = [_normalize_pob_url(u) for u in candidates if POB_URL_RE.match(u)]
    passive_candidates = [u for u in candidates if PASSIVE_URL_RE.match(u)]
    specific_maxroll_tools = [u for u in candidates if _looks_like_specific_maxroll_tool(u)]

    warnings: list[str] = []
    source_type = _source_type_for_host(url)

    if source_type == "maxroll" and not pob_candidates and not passive_candidates:
        warnings.append("Maxroll guide page did not expose a build-specific PoB or passive tree URL.")
        if specific_maxroll_tools:
            warnings.append("Only generic Maxroll tool links were found; build-specific planner data may be client-side.")
    if source_type == "poe_ninja_pob_page" and not pob_candidates and not passive_candidates:
        warnings.append("poe.ninja build page detected, but it did not expose a direct pobb.in export or official passive tree URL.")
        warnings.append("A site-specific poe.ninja extractor is required for full parsing.")
    if source_type == "poedb" and not pob_candidates and not passive_candidates:
        warnings.append("PoEDB page did not expose a direct PoB or passive tree URL.")

    return {
        "dataset_kind": "poe1_build_source_resolution",
        "input_url": url,
        "source_type": source_type,
        "canonical_url": canonical_url,
        "title": title,
        "pob_url": pob_candidates[0] if pob_candidates else None,
        "passive_tree_url": passive_candidates[0] if passive_candidates else None,
        "maxroll_tool_url": specific_maxroll_tools[0] if specific_maxroll_tools else None,
        "warnings": warnings,
        "all_candidates": {
            "pob_urls": pob_candidates[:5],
            "passive_tree_urls": passive_candidates[:5],
            "tool_urls": specific_maxroll_tools[:5],
        },
    }


def resolve_source(url: str) -> dict:
    url = url.strip()
    source_type = _source_type_for_host(url)

    if source_type in {
        "pobb",
        "pastebin",
        "file",
        "poe_ninja_pob_raw",
        "poedb_pob_raw",
        "maxroll_profile_api",
    }:
        normalized = _normalize_pob_url(url)
        return {
            "dataset_kind": "poe1_build_source_resolution",
            "input_url": url,
            "source_type": source_type,
            "canonical_url": normalized,
            "title": None,
            "pob_url": normalized,
            "passive_tree_url": None,
            "maxroll_tool_url": None,
            "warnings": [],
            "all_candidates": {"pob_urls": [normalized], "passive_tree_urls": [], "tool_urls": []},
        }

    if source_type == "poedb_pob_page":
        raw_url = _poedb_raw_url(url)
        return {
            "dataset_kind": "poe1_build_source_resolution",
            "input_url": url,
            "source_type": source_type,
            "canonical_url": url,
            "title": None,
            "pob_url": raw_url,
            "passive_tree_url": None,
            "maxroll_tool_url": None,
            "warnings": ["PoEDB build page resolved to its raw Path of Building export endpoint."],
            "all_candidates": {"pob_urls": [raw_url], "passive_tree_urls": [], "tool_urls": []},
        }

    if source_type in {"maxroll_pob_page", "maxroll_planner_page"}:
        profile_url = _maxroll_profile_api_url(url)
        return {
            "dataset_kind": "poe1_build_source_resolution",
            "input_url": url,
            "source_type": source_type,
            "canonical_url": url,
            "title": None,
            "pob_url": profile_url,
            "passive_tree_url": None,
            "maxroll_tool_url": url,
            "warnings": ["Maxroll build page resolved to its planner profile endpoint."],
            "all_candidates": {"pob_urls": [profile_url], "passive_tree_urls": [], "tool_urls": [url]},
        }

    if source_type == "poe_ninja_pob_page":
        raw_url = _poe_ninja_raw_url(url)
        return {
            "dataset_kind": "poe1_build_source_resolution",
            "input_url": url,
            "source_type": source_type,
            "canonical_url": url,
            "title": None,
            "pob_url": raw_url,
            "passive_tree_url": None,
            "maxroll_tool_url": None,
            "warnings": ["poe.ninja build page resolved to its raw Path of Building export endpoint."],
            "all_candidates": {"pob_urls": [raw_url], "passive_tree_urls": [], "tool_urls": []},
        }

    if source_type == "passive_tree":
        return {
            "dataset_kind": "poe1_build_source_resolution",
            "input_url": url,
            "source_type": source_type,
            "canonical_url": url,
            "title": None,
            "pob_url": None,
            "passive_tree_url": url,
            "maxroll_tool_url": None,
            "warnings": [],
            "all_candidates": {"pob_urls": [], "passive_tree_urls": [url], "tool_urls": []},
        }

    response = _http_get(url, timeout=20)
    response.raise_for_status()
    return resolve_from_html(url, response.text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: python build_source_resolver.py <url>"}, ensure_ascii=False))
        sys.exit(1)
    try:
        print(json.dumps(resolve_source(sys.argv[1]), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

