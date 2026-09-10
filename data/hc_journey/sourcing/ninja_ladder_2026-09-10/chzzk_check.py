import json, re, time, urllib.request, urllib.parse, gzip, pathlib
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Accept-Encoding": "gzip"}
def get(url):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=30) as f:
        raw = f.read()
        if f.headers.get('Content-Encoding') == 'gzip': raw = gzip.decompress(raw)
        return json.loads(raw.decode('utf-8'))
rows = json.loads(pathlib.Path('korean_rows.json').read_text(encoding='utf-8'))
out = []
def cands(r):
    name = r.get('name') or ''; acc = (r.get('account') or '').rsplit('-', 1)[0]
    c = []
    for s in (name, acc):
        s = s.strip('_ ')
        s2 = re.sub(r'(이호기|_?하코|HC_?|_?ttv|_?twitch|_?live|치지직|금단의?의?식)', '', s, flags=re.I).strip('_ ')
        for x in (s, s2):
            if x and x not in c and len(x) >= 2: c.append(x)
    return c[:4]
for r in rows:
    rec = {'account': r['account'], 'name': r['name'], 'league': r['league'], 'level': r['level'], 'tried': [], 'matches': []}
    for q in cands(r):
        try:
            d = get('https://api.chzzk.naver.com/service/v1/search/channels?keyword=' + urllib.parse.quote(q) + '&offset=0&size=5')
            items = (d.get('content') or {}).get('data') or []
            rec['tried'].append(q)
            for it in items:
                ch = it.get('channel') or {}
                cname = ch.get('channelName') or ''
                desc = (ch.get('channelDescription') or '')
                exact = cname.lower() == q.lower()
                poe = bool(re.search(r'poe|패스 ?오브|엑자일|path of exile', (cname + ' ' + desc), re.I))
                if exact or (poe and q.lower() in cname.lower()):
                    cid = ch.get('channelId')
                    vids = None; latest = None; titles = []
                    try:
                        v = get(f'https://api.chzzk.naver.com/service/v1/channels/{cid}/videos?sortType=LATEST&pagination=&size=5')
                        vd = (v.get('content') or {}).get('data') or []
                        vids = (v.get('content') or {}).get('totalCount', len(vd))
                        titles = [x.get('videoTitle') for x in vd[:3]]; latest = vd[0].get('publishDate') if vd else None
                    except Exception as e:
                        titles = [f'videos ERR {e.__class__.__name__}']
                    rec['matches'].append({'query': q, 'channelName': cname, 'channelId': cid, 'followers': ch.get('followerCount'), 'exact': exact, 'poe_in_desc': poe, 'desc': desc[:120], 'videos_total': vids, 'latest': latest, 'titles': titles})
                    time.sleep(0.7)
        except Exception as e:
            rec['tried'].append(f'{q} ERR {e.__class__.__name__}')
        time.sleep(0.7)
    out.append(rec)
    pathlib.Path('chzzk_results.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(r['league'], r['level'], r['name'], '|', r['account'], '->', [(m['channelName'], m['videos_total'], m['poe_in_desc']) for m in rec['matches']], flush=True)
print('DONE', len(out))
