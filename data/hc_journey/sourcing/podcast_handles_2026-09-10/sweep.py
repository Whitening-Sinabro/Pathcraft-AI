import json, re, subprocess, sys, time, pathlib
OUT = pathlib.Path(__file__).parent
handles = [h.strip() for h in (OUT/'handles.txt').read_text(encoding='utf-8').splitlines() if h.strip()]
POE2 = re.compile(r'(?i)poe ?2|path of exile 2|0\.[3-5](\.5)?\b|forbidden rites|varashta|kitava|gemling|witchhunter|lich\b|chronomancer|warbringer|invoker|titan|amazon|ritualist|tactician|acolyte|deadeye|pathfinder|stormweaver|infernalist|blood mage|smith of')
HC = re.compile(r'(?i)hardcore|hcssf|\bhc\b|하드코어|하코|forbiddenriteshc|runesofaldurhc|hc-forbidden|hc-ssf|/hc|abysshcssf|vaalhcssf')
def run(args, timeout=120):
    p = subprocess.run([sys.executable, '-m', 'yt_dlp', '--no-warnings'] + args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
    return p.returncode, p.stdout, p.stderr
results = []
for h in handles:
    url = f'https://www.youtube.com/{h}/videos'
    rc, out, err = run(['--flat-playlist', '--playlist-end', '40', '--print', '%(id)s|%(upload_date)s|%(duration)s|%(title)s', '--', url])
    rows = [l for l in out.splitlines() if '|' in l]
    rec = {'handle': h, 'ok': rc == 0, 'n_videos_listed': len(rows), 'err': (err.strip()[-160:] if rc else ''), 'poe2_titles': 0, 'hc_titles': 0, 'checked': []}
    if rows:
        poe2 = [r for r in rows if POE2.search(r.split('|', 3)[-1])]
        rec['poe2_titles'] = len(poe2); rec['hc_titles'] = sum(1 for r in rows if HC.search(r.split('|', 3)[-1]))
        rec['sample_titles'] = [r.split('|', 3)[-1][:90] for r in rows[:5]]
        for r in poe2[:4]:
            vid = r.split('|', 1)[0]
            rc2, out2, _ = run(['--skip-download', '--no-playlist', '-j', '--', vid])
            if rc2 == 0 and out2.strip():
                try:
                    d = json.loads(out2)
                except Exception:
                    d = {}
                desc = d.get('description') or ''
                links = sorted(set(re.findall(r'https?://(?:poe\.ninja|mobalytics\.gg|maxroll\.gg|pobb\.in|poe-vault\.com|twitch\.tv)[^\s)\]>"\']*', desc)))
                rec['checked'].append({'id': vid, 'title': (d.get('title') or '')[:90], 'upload_date': d.get('upload_date'), 'channel_id': d.get('channel_id'), 'channel': d.get('channel'), 'hc_in_desc': bool(HC.search(desc)), 'hc_links': [l for l in links if HC.search(l)], 'links': links[:8]})
                rec['channel_id'] = d.get('channel_id'); rec['channel'] = d.get('channel'); rec['followers'] = d.get('channel_follower_count')
            time.sleep(1)
    results.append(rec)
    (OUT/'sweep.json').write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf-8')
    print(h, rec['n_videos_listed'], 'poe2', rec['poe2_titles'], 'hc', rec['hc_titles'], 'hc_desc', sum(1 for c in rec['checked'] if c['hc_in_desc'] or c['hc_links']), flush=True)
    time.sleep(1)
print('DONE', len(results))
