# -*- coding: utf-8 -*-
"""Verify candidate logins against Twitch (yt-dlp) and, for Korean-signal names, chzzk.
Metadata only: uses --flat-playlist and --skip-download semantics (yt-dlp never
downloads media here, it only prints video listing metadata).
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

def yt_dlp_videos(login, playlist_end=5):
    """Return list of dicts: id, upload_date, duration, title. Empty list if 0 VODs.
    None if channel doesn't exist / error."""
    cmd = [
        sys.executable, '-X', 'utf8', '-m', 'yt_dlp',
        '--flat-playlist', '--playlist-end', str(playlist_end), '--no-warnings',
        '--print', '%(id)s|%(upload_date)s|%(duration)s|%(title)s',
        '--', f'https://www.twitch.tv/{login}/videos',
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=30)
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    out = p.stdout.strip()
    err = p.stderr.strip()
    if p.returncode != 0:
        return None, err[:300]
    if not out:
        return [], err[:300]
    rows = []
    for line in out.splitlines():
        parts = line.split('|', 3)
        if len(parts) == 4:
            rows.append({'id': parts[0], 'upload_date': parts[1], 'duration': parts[2], 'title': parts[3]})
    return rows, None

def twitch_channel_exists(login):
    """Fallback check: does the channel page itself resolve (distinguishes no-channel vs no-VODs)."""
    cmd = [
        sys.executable, '-X', 'utf8', '-m', 'yt_dlp', '-j', '--skip-download', '--no-warnings',
        '--playlist-end', '1',
        '--', f'https://www.twitch.tv/{login}',
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=30)
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    if p.returncode != 0:
        return False, p.stderr.strip()[:300]
    return True, None

def chzzk_search(name):
    url = f'https://api.chzzk.naver.com/service/v1/search/channels?keyword={urllib.parse.quote(name)}&offset=0&size=5'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data, None
    except Exception as e:
        return None, str(e)

def chzzk_videos(channel_id):
    url = f'https://api.chzzk.naver.com/service/v1/channels/{channel_id}/videos?sortType=LATEST&pagination=&size=5'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data, None
    except Exception as e:
        return None, str(e)

import urllib.parse

if __name__ == '__main__':
    # single-login test mode
    login = sys.argv[1]
    rows, err = yt_dlp_videos(login)
    print('videos:', rows, 'err:', err)
