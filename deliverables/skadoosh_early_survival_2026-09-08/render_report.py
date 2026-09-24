"""Render the Korean report and verify references and evidence integrity."""
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from html.parser import HTMLParser
import base64
import hashlib
import json
import re

import markdown

HERE = Path(__file__).resolve().parent
SOURCE = HERE / '초반생존_방송상세분석.md'
TARGET = SOURCE.with_suffix('.html')
text = SOURCE.read_text(encoding='utf-8')
engine = markdown.Markdown(extensions=['tables', 'toc', 'fenced_code'])
body = engine.convert(text)


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a' and d.get('href'):
            self.links.append(d['href'])
        if tag == 'img' and d.get('src'):
            self.images.append(d['src'])


refs = References()
refs.feed(body)
local = []
vod_links = []
durations = {'2865212551': 16953, '2866065347': 20678}
for link in refs.links + refs.images:
    u = urlparse(link)
    if not u.scheme and not link.startswith('#'):
        p = (HERE / unquote(u.path)).resolve()
        assert p.is_file(), f'Missing local reference: {link}'
        local.append(link)
    if u.netloc == 'www.twitch.tv':
        vod = u.path.rsplit('/', 1)[-1]
        ts = parse_qs(u.query).get('t', [])
        if ts:
            m = re.fullmatch(r'(\d+)h(\d+)m(\d+)s', ts[0])
            assert m, link
            h, minutes, s = map(int, m.groups())
            at = h * 3600 + minutes * 60 + s
            assert at < durations[vod], link
            vod_links.append({'video': vod, 'seconds': at})

coverage = json.loads((HERE / 'focus_coverage.json').read_text(encoding='utf-8'))
merged = {}
for scene in coverage['scenes']:
    p = HERE / (scene['name'] + '.json')
    assert hashlib.sha256(p.read_bytes()).hexdigest() == scene['sha256']
    data = json.loads(p.read_text(encoding='utf-8'))
    assert data['interval'] == scene['interval']
    assert data['human_audio_listened'] is False
    assert scene['interval'][1] <= durations[scene['video']]
    merged.setdefault(scene['video'], []).append(scene['interval'])
unique_seconds = 0
for intervals in merged.values():
    end = -1
    for a, b in sorted(intervals):
        unique_seconds += max(0, b - max(a, end))
        end = max(end, b)
assert unique_seconds == 3785
assert coverage['audio_seconds_processed'] == 3820

equipment = json.loads((HERE / 'equipment_evidence.json').read_text(encoding='utf-8'))
for record in equipment:
    p = Path(record['source'])
    assert hashlib.sha256(p.read_bytes()).hexdigest() == record['source_sha256']
assert [r['level_observed'] for r in equipment] == [24, 34, 43]

# Embed the three already inspected source frames without changing them.
for link in refs.images:
    p = (HERE / unquote(link)).resolve()
    encoded = base64.b64encode(p.read_bytes()).decode('ascii')
    body = body.replace(f'src="{link}"', f'src="data:image/jpeg;base64,{encoded}" loading="lazy"')
body = body.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')

style = '''
:root{color-scheme:light;--ink:#1d2933;--muted:#586777;--accent:#175b54;--line:#dbe3e7}
*{box-sizing:border-box}body{margin:0;background:#f1f4f4;color:var(--ink);font-family:"Malgun Gothic","Noto Sans KR",system-ui,sans-serif;font-size:16px;line-height:1.85}
main{max-width:1140px;margin:32px auto;padding:42px 52px;background:white;border:1px solid var(--line);border-radius:14px}
h1{font-size:2rem;line-height:1.45;letter-spacing:-.035em}h2{font-size:1.5rem;margin-top:3rem;padding-top:1rem;border-top:2px solid var(--line)}h3{font-size:1.1rem;margin-top:2rem}
p,li{word-break:keep-all;overflow-wrap:anywhere}li{margin:.4rem 0}strong{color:#123d38}a{color:var(--accent);text-underline-offset:3px}a:hover{color:#092d27}
.meta{color:var(--muted);font-size:.88rem}.table-scroll{overflow-x:auto;margin:1.25rem 0;border:1px solid var(--line);border-radius:8px}table{border-collapse:collapse;min-width:680px;width:100%;font-size:.92rem}th,td{padding:13px 15px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}th{background:#e9f2f0;color:#143e39}tr:last-child td{border-bottom:0}td:first-child{min-width:115px}tbody tr:nth-child(even){background:#f8fafb}
img{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:8px;margin-top:1.5rem}details{background:#f1f6f5;border:1px solid #d4e3df;border-radius:8px;padding:12px 20px;margin:24px 0}summary{cursor:pointer;font-weight:700;color:var(--accent)}.toc ul{margin-top:.4rem}.toc>ul{padding-left:20px}
@media(max-width:700px){body{font-size:15px}main{margin:0;padding:24px 18px;border:0;border-radius:0}h1{font-size:1.6rem}h2{font-size:1.3rem}th,td{padding:10px}.table-scroll{margin-left:-4px;margin-right:-4px}}
@media print{body{background:white;font-size:10pt}main{margin:0;padding:0;border:0;max-width:none}details{display:none}.table-scroll{overflow:visible}table{min-width:0;font-size:8pt}h2,h3{break-after:avoid}img{max-height:95mm;object-fit:contain}a{color:inherit}}
'''
page = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Skadoosh 초반 생존 · 방송 상세 분석</title><style>' + style + '</style></head><body><main>'
        '<p class="meta">초반 진행 중심 · 관련 13구간 재전사 · 24·34·43레벨 장비 대조</p>'
        '<details><summary>목차 열기</summary>' + engine.toc + '</details>' + body + '</main></body></html>')
TARGET.write_text(page, encoding='utf-8')
result = {
    'status': 'passed',
    'checks': 'Local references exist; Twitch timestamps fit preserved VOD lengths; ASR and source snapshot hashes match; HTML source frames embedded unchanged.',
    'local_reference_count': len(local),
    'timestamped_twitch_links': len(vod_links),
    'asr_clips': len(coverage['scenes']),
    'asr_seconds_processed': 3820,
    'asr_unique_seconds': unique_seconds,
    'equipment_levels': [r['level_observed'] for r in equipment],
    'images_embedded': len(refs.images),
    'outputs': {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in [SOURCE, TARGET]},
    'limits': ['ASR is not human listening.', 'No browser visual rendering check.',
               'Link syntax/range validation is not a guarantee of Twitch playback availability.',
               'No character-specific death diagnosis or in-game testing.'],
}
(HERE / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
