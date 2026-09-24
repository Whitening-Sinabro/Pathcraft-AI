"""Render the bounded mechanics report and link it from the existing guides."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
import ast, hashlib, json, re, subprocess
import markdown

HERE = Path(__file__).resolve().parent
VOD = HERE.parent
ROOT = HERE.parents[2]
TITLE = '빌드핵심_추가확인'

def main():
    # Reuse presentation constants without executing the older publisher.
    constants = {}
    for node in ast.parse((VOD / 'publish_review.py').read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('style', 'script'):
            constants[node.targets[0].id] = ast.literal_eval(node.value)
    body = markdown.markdown((HERE / (TITLE + '.md')).read_text(encoding='utf-8'), extensions=['tables', 'fenced_code'])
    clips = []
    for label in re.findall(r'<!-- replay:([a-z_]+) -->', body):
        meta = json.loads((VOD / 'clips' / (label + '.json')).read_text(encoding='utf-8'))
        path = VOD / 'clips' / (label + '.mp4')
        probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height', '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout)
        duration = float(probe['format']['duration'])
        assert abs(duration - (meta['requested_end'] - meta['requested_start'])) < .2
        assert any(s.get('width') == 1280 for s in probe['streams'])
        poster = f'frames/{label}_{meta["requested_start"] + 15}.jpg'
        body = body.replace('<!-- replay:' + label + ' -->', f'<figure class="replay" data-origin="{meta["requested_start"]}"><video controls preload="none" poster="{poster}" src="../clips/{label}.mp4"></video><figcaption><button data-seek="-0.5">−0.5초</button><button data-seek="0.5">+0.5초</button><label>속도 <select><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label><output></output><a href="https://www.twitch.tv/videos/2868822161?t={meta["requested_start"]}s">원본 위치</a></figcaption></figure>')
        clips.append({'label': label, 'interval': [meta['requested_start'], meta['requested_end']], 'duration': duration, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    style = constants['style'] + 'img{display:block;max-width:100%;height:auto;margin:20px auto}p,li{overflow-wrap:anywhere}'
    document = f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Skadoosh 빌드 핵심 추가 확인</title><style>{style}</style><main>{body}</main><script>{constants["script"]}</script></html>'
    (HERE / (TITLE + '.html')).write_text(document, encoding='utf-8')
    notice = '**9월 9일 핵심 추가 확인:** [회복·순수함 정신력·토템 명중률·방어도 파괴 조건](../deliverables/skadoosh_new_broadcast_2026-09-09/mechanics_followup/빌드핵심_추가확인.html). 05/06/07 플래너의 정신력 설명을 수정하고 설치본·ZIP에 반영했다.'
    marker = '<!-- mechanics-followup-20260909 -->'
    for name in ['2026-09-08_SKADOOSH_SESSION_CHECKPOINT.md', '2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_RESEARCH.md']:
        p = ROOT / 'Docs' / name
        s = p.read_text(encoding='utf-8')
        if marker not in s:
            title, rest = s.split('\n', 1)
            p.write_text(title + '\n\n' + marker + '\n' + notice + '\n' + rest, encoding='utf-8')
    for name in ['2026-09-08_SKADOOSH_SESSION_CHECKPOINT.html', '2026-09-05_SKADOOSH_CORRUPTING_CRY_TOTEM_WARBRINGER_0_5_5_GUIDE_DOC.html']:
        p = ROOT / 'Docs' / name
        s = p.read_text(encoding='utf-8')
        if marker not in s:
            assert re.search(r'<main\b[^>]*>', s)
            p.write_text(re.sub(r'(<main\b[^>]*>)', lambda m: m.group(1) + marker + markdown.markdown(notice), s, count=1), encoding='utf-8')
    missing = []
    for target in re.findall(r'(?:href|src|poster)="([^"]+)"', document):
        u = urlparse(target)
        if u.scheme or target.startswith('#'):
            continue
        p = (HERE / unquote(u.path)).resolve()
        if p.name == 'report_validation.json':
            continue
        if not p.exists():
            missing.append(str(p))
    assert not missing, missing
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'report': TITLE + '.html', 'new_clips': clips, 'new_clip_seconds': sum(c['duration'] for c in clips), 'accuracy_frames_extracted': len(list((HERE / 'frames').glob('accuracy_[ab]_[0-9]*.jpg'))), 'missing_local_links': missing, 'asr_labels_automatic': True, 'continuous_full_video_viewing': False, 'native_validation': 'planner_note_validation.json', 'uncertainties': ['Echo / Urgent Call interaction and net recovery', 'Live totem accuracy after swap, beyond the G-panel display', 'Scavenged Plating uptime after the final armour-break investment']}
    (HERE / 'report_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
