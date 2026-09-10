# -*- coding: utf-8 -*-
import json
import re
import time
import sys

from verify import yt_dlp_videos, twitch_channel_exists, chzzk_search, chzzk_videos

KOREAN_RE = re.compile(r'[가-힣]')

def verify_twitch(login):
    rows, err = yt_dlp_videos(login)
    time.sleep(1)
    if rows is None:
        return {'platform': 'twitch', 'login': login, 'exists': None, 'verified': False,
                'video_count': 0, 'videos': [], 'evidence': f'flat-playlist error: {err}'}
    if rows:
        return {'platform': 'twitch', 'login': login, 'exists': True, 'verified': True,
                'video_count': len(rows), 'videos': rows,
                'evidence': f'yt-dlp --flat-playlist videos: https://www.twitch.tv/{login}/videos -> {len(rows)} VODs'}
    # rows == [] -> ambiguous, disambiguate via channel page
    exists, cerr = twitch_channel_exists(login)
    time.sleep(1)
    if cerr and 'does not exist' in (cerr or ''):
        return {'platform': 'twitch', 'login': login, 'exists': False, 'verified': False,
                'video_count': 0, 'videos': [], 'evidence': f'channel page: {cerr}'}
    # exists but currently offline / 0 vods, or some other transient state
    return {'platform': 'twitch', 'login': login, 'exists': True, 'verified': True,
            'video_count': 0, 'videos': [],
            'evidence': f'channel exists, 0 VODs (channel page check: {cerr or "ok"})'}

def verify_chzzk(name):
    data, err = chzzk_search(name)
    time.sleep(1)
    if err or not data:
        return {'platform': 'chzzk', 'query': name, 'exists': None, 'verified': False,
                'video_count': 0, 'videos': [], 'evidence': f'search error: {err}'}
    channels = (data.get('content') or {}).get('data') or []
    match = None
    for ch in channels:
        cname = ch.get('channelName', '')
        desc = (ch.get('channelDescription') or '')
        if cname.lower() == name.lower():
            match = ch
            break
        if 'poe' in desc.lower() or '패스 오브 엑자일' in desc or '패스오브엑자일' in desc:
            match = ch
            break
    if not match:
        return {'platform': 'chzzk', 'query': name, 'exists': False, 'verified': False,
                'video_count': 0, 'videos': [],
                'evidence': f'search returned {len(channels)} channels, none matched name or POE description'}
    cid = match.get('channelId')
    vdata, verr = chzzk_videos(cid) if cid else (None, 'no channelId')
    time.sleep(1)
    videos = []
    if vdata:
        vlist = (vdata.get('content') or {}).get('data') or []
        for v in vlist:
            videos.append({'id': v.get('videoNo'), 'title': v.get('videoTitle'),
                            'upload_date': v.get('publishDate'), 'duration': v.get('duration')})
    return {'platform': 'chzzk', 'query': name, 'exists': True, 'verified': True,
            'channel_id': cid, 'channel_name': match.get('channelName'),
            'video_count': len(videos), 'videos': videos[:5],
            'evidence': f'chzzk search matched channelName={match.get("channelName")!r}, videos endpoint -> {len(videos)}'}

def main():
    with open('candidates.json', encoding='utf-8') as fh:
        candidates = json.load(fh)
    with open('ladder_all.json', encoding='utf-8') as fh:
        ladder_all = json.load(fh)
    base_accounts = set((r['league'], r['account']) for r in ladder_all if 'base' in r['filters_matched'])

    # priority: explicit marker signal first, then known creators, then bare-login-only
    # (restricted to accounts seen in the unfiltered top-100 base pulls, to keep runtime bounded
    # per task instruction: "prioritize the two unfiltered top-100 lists first")
    items = list(candidates.items())
    def has_marker(c):
        return c.get('has_marker_signal', False)
    def top_level(c):
        return max((r.get('level') or 0) for r in c['rows'])
    def in_base(c):
        return any((r['league'], r['account']) in base_accounts for r in c['rows'])
    marker_items = [it for it in items if has_marker(it[1])]
    known_items = [it for it in items if it[1].get('known_creator') and not has_marker(it[1])]
    bare_items = [it for it in items if not has_marker(it[1]) and not it[1].get('known_creator') and in_base(it[1])]
    bare_items.sort(key=lambda it: -top_level(it[1]))

    limit_bare = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    ordered = marker_items + known_items + bare_items[:limit_bare]

    print(f'verifying {len(ordered)} logins ({len(marker_items)} marker-signal, '
          f'{len(known_items)} known-creator, {min(limit_bare,len(bare_items))} bare-only of {len(bare_items)})')

    results = {}
    for i, (login_l, c) in enumerate(ordered):
        login = c['login_candidate']
        has_kr = any(KOREAN_RE.search(r.get('name') or '') or KOREAN_RE.search(r.get('account') or '') for r in c['rows'])
        res = {'candidate': c, 'twitch': None, 'chzzk': None}
        res['twitch'] = verify_twitch(login)
        if not res['twitch']['verified'] and has_kr:
            # try chzzk against the raw character name(s)
            for r in c['rows']:
                nm = r.get('name')
                if nm and KOREAN_RE.search(nm):
                    res['chzzk'] = verify_chzzk(nm)
                    break
        results[login_l] = res
        status = 'OK' if res['twitch']['verified'] else ('CHZZK' if res['chzzk'] and res['chzzk']['verified'] else 'no')
        print(f"[{i+1}/{len(ordered)}] {login!r} twitch={res['twitch']['verified']} vids={res['twitch']['video_count']} chzzk={status}", flush=True)
        # incremental save every 10
        if (i + 1) % 10 == 0:
            with open('verify_results.json', 'w', encoding='utf-8') as fh:
                json.dump(results, fh, ensure_ascii=False, indent=2)

    with open('verify_results.json', 'w', encoding='utf-8') as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print('DONE')

if __name__ == '__main__':
    main()
