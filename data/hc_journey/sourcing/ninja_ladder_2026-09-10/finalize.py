# -*- coding: utf-8 -*-
import json
import re

with open('candidates.json', encoding='utf-8') as fh:
    candidates = json.load(fh)
with open('ladder_all.json', encoding='utf-8') as fh:
    ladder_all = json.load(fh)
with open('verify_results.json', encoding='utf-8') as fh:
    verify_results = json.load(fh)

base_accounts = set((r['league'], r['account']) for r in ladder_all if 'base' in r['filters_matched'])

KNOWN_CREATORS = {
    'dtq03087-0345': '임성빈',
    'DNEL-7382': '디넬',
    'BlazeW-3944': 'Blazeworks',
    'ITheCon-2183': 'Skadoosh',
    'Oscrix-1876': 'Oscrix',
    'sdd9-5499': 'Gressoul',
    'KrisDroverson-5430': 'KrisDroverson',
    'TheMasterBlaster-2484': 'LexD',
    'Arserina-5429': 'Arserina',
    'CololadoBurger-7117': 'CololadoBurger',
}

items = list(candidates.items())
def has_marker(c): return c.get('has_marker_signal', False)
def top_level(c): return max((r.get('level') or 0) for r in c['rows'])
def in_base(c): return any((r['league'], r['account']) in base_accounts for r in c['rows'])

marker_items = [it for it in items if has_marker(it[1])]
known_items = [it for it in items if it[1].get('known_creator') and not has_marker(it[1])]
bare_items = [it for it in items if not has_marker(it[1]) and not it[1].get('known_creator') and in_base(it[1])]
bare_items.sort(key=lambda it: -top_level(it[1]))
ordered = marker_items + known_items + bare_items[:60]

def lang_guess(titles):
    txt = ' '.join(t for t in titles if t)
    if re.search(r'[가-힣]', txt):
        return 'ko'
    if re.search(r'[぀-ヿ]', txt):
        return 'ja'
    if re.search(r'[一-鿿]', txt):
        return 'zh'
    if re.search(r'[а-яА-Я]', txt):
        return 'ru'
    if not txt.strip():
        return 'unknown'
    return 'en'

verified_with_videos = []
verified_no_videos = []
unverified = []
pending = []

for login_l, c in ordered:
    login = c['login_candidate']
    accounts_seen = sorted(set(r['account'] for r in c['rows']))
    leagues_seen = sorted(set(r['league'] for r in c['rows']))
    char_names = sorted(set(r['name'] for r in c['rows']))
    known = c.get('known_creator')

    if login_l not in verify_results:
        pending.append({
            'login_candidate': login, 'accounts': accounts_seen, 'characters': char_names,
            'leagues': leagues_seen, 'known_creator': known, 'signals': c.get('signals', []),
            'status': 'pending (not reached before time budget)',
        })
        continue

    res = verify_results[login_l]
    tw = res.get('twitch') or {}
    cz = res.get('chzzk') or {}
    titles = [v.get('title') for v in (tw.get('videos') or [])] + [v.get('title') for v in (cz.get('videos') or [])]

    row = {
        'account': accounts_seen, 'character_names': char_names, 'leagues': leagues_seen,
        'known_creator': known, 'signals': c.get('signals', []),
    }
    if tw.get('verified'):
        row['platform'] = 'twitch'
        row['channel_url'] = f'https://www.twitch.tv/{login}'
        row['video_count_seen'] = tw.get('video_count', 0)
        row['latest_video_date'] = (tw.get('videos') or [{}])[0].get('upload_date')
        row['sample_title'] = (tw.get('videos') or [{}])[0].get('title')
        row['language_guess'] = lang_guess(titles) if titles else 'unknown'
        row['evidence'] = tw.get('evidence')
        if tw.get('video_count', 0) >= 1:
            verified_with_videos.append(row)
        else:
            verified_no_videos.append(row)
    elif cz.get('verified'):
        row['platform'] = 'chzzk'
        row['channel_url'] = f"https://chzzk.naver.com/{cz.get('channel_id','')}"
        row['video_count_seen'] = cz.get('video_count', 0)
        row['latest_video_date'] = (cz.get('videos') or [{}])[0].get('upload_date')
        row['sample_title'] = (cz.get('videos') or [{}])[0].get('title')
        row['language_guess'] = 'ko'
        row['evidence'] = cz.get('evidence')
        if cz.get('video_count', 0) >= 1:
            verified_with_videos.append(row)
        else:
            verified_no_videos.append(row)
    else:
        unverified.append({
            'login_candidate': login, 'accounts': accounts_seen, 'characters': char_names,
            'leagues': leagues_seen, 'known_creator': known, 'signals': c.get('signals', []),
            'twitch_evidence': tw.get('evidence'), 'chzzk_evidence': cz.get('evidence'),
        })

out = {
    'verified_with_videos': verified_with_videos,
    'verified_no_videos': verified_no_videos,
    'unverified_candidates': unverified,
    'pending': pending,
}
with open('streamers.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)

# --- markdown ---
lines = []
lines.append('# poe.ninja POE2 Hardcore Ladder — Streamer/YouTuber Scan')
lines.append('')
lines.append(f'Leagues: hc-forbidden-rites, hc-ssf-forbidden-rites. Ladder rows pulled: {len(ladder_all)} unique (name, account) rows across base top-100 + ascendancy-filter sweep.')
lines.append(f'Candidates checked so far: {len(ordered) - len(pending)} of {len(ordered)} prioritized ({len(pending)} pending).')
lines.append('')
lines.append('## Verified streamers/YouTubers — has videos (>=1 VOD seen)')
lines.append('')
if verified_with_videos:
    lines.append('| Account | Character(s) | League(s) | Platform | Channel | Videos seen | Latest date | Sample title | Lang | Known creator |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(verified_with_videos, key=lambda x: -x['video_count_seen']):
        lines.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            ', '.join(r['account']), ', '.join(r['character_names']), ', '.join(r['leagues']),
            r['platform'], r['channel_url'], r['video_count_seen'], r.get('latest_video_date') or '-',
            (r.get('sample_title') or '-').replace('|', '/'), r.get('language_guess', '-'),
            r.get('known_creator') or '-'))
else:
    lines.append('_none found among candidates checked so far_')
lines.append('')
lines.append('## Verified channels — exists, 0 VODs found')
lines.append('')
if verified_no_videos:
    lines.append('| Account | Character(s) | League(s) | Platform | Channel | Evidence |')
    lines.append('|---|---|---|---|---|---|')
    for r in verified_no_videos:
        lines.append('| {} | {} | {} | {} | {} | {} |'.format(
            ', '.join(r['account']), ', '.join(r['character_names']), ', '.join(r['leagues']),
            r['platform'], r['channel_url'], (r.get('evidence') or '-').replace('|', '/')))
else:
    lines.append('_none_')
lines.append('')
lines.append('## Unverified candidates (name/account signal, no channel confirmed)')
lines.append('')
if unverified:
    lines.append('| Login tried | Account | Character(s) | Signals | Twitch evidence | Chzzk evidence |')
    lines.append('|---|---|---|---|---|---|')
    for r in unverified:
        sig = '; '.join(f"{s['field']}={s['value']}({','.join(s['markers'])})" for s in r['signals']) or '-'
        lines.append('| {} | {} | {} | {} | {} | {} |'.format(
            r['login_candidate'], ', '.join(r['accounts']), ', '.join(r['characters']), sig,
            (r.get('twitch_evidence') or '-').replace('|', '/'), (r.get('chzzk_evidence') or '-').replace('|', '/')))
else:
    lines.append('_none_')
lines.append('')
lines.append('## Pending (not verified — time budget)')
lines.append('')
if pending:
    lines.append('| Login candidate | Account | Character(s) | Signals |')
    lines.append('|---|---|---|---|')
    for r in pending:
        sig = '; '.join(f"{s['field']}={s['value']}({','.join(s['markers'])})" for s in r['signals']) or '-'
        lines.append('| {} | {} | {} | {} |'.format(r['login_candidate'], ', '.join(r['accounts']), ', '.join(r['characters']), sig))
else:
    lines.append('_none — all prioritized candidates were checked_')
lines.append('')
lines.append('## Known-creator cross-reference')
lines.append('')
found_known = {}
for r in ladder_all:
    if r['account'] in KNOWN_CREATORS:
        found_known.setdefault(r['account'], []).append(r)
for acct, disp in KNOWN_CREATORS.items():
    rows = found_known.get(acct)
    if rows:
        leagues = ', '.join(sorted(set(r['league'] for r in rows)))
        lines.append(f"- `{acct}` ({disp}): FOUND in ladder — leagues: {leagues}, char(s): {', '.join(sorted(set(r['name'] for r in rows)))}")
    else:
        lines.append(f"- `{acct}` ({disp}): not present in pulled ladder rows")

with open('streamers.md', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))

print('verified_with_videos:', len(verified_with_videos))
print('verified_no_videos:', len(verified_no_videos))
print('unverified:', len(unverified))
print('pending:', len(pending))
