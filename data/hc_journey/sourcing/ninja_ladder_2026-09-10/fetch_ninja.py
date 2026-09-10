import gzip
import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

from protodec import decode_ladder

OUTDIR = 'raw'
import os
os.makedirs(OUTDIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Encoding': 'gzip, deflate',
}

def fetch(slug, extra_params=None, max_retries=5):
    params = {'overview': slug}
    if extra_params:
        params.update(extra_params)
    qs = urllib.parse.urlencode(params)
    url = f'https://poe.ninja/poe2/api/builds/latest/search?{qs}'
    backoff = 60
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                enc = resp.headers.get('Content-Encoding', '')
                if enc == 'gzip':
                    data = gzip.decompress(data)
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                sys.stderr.write(f'429 on {url}, backing off {backoff}s\n')
                time.sleep(backoff)
                backoff = min(backoff * 2, 1800)
                continue
            raise
    raise RuntimeError(f'exceeded retries for {url}')

def safe_name(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def fetch_and_save(slug, extra_params=None, label=None):
    label = label or 'base'
    raw = fetch(slug, extra_params)
    fname = os.path.join(OUTDIR, f'{slug}__{safe_name(label)}.bin')
    with open(fname, 'wb') as fh:
        fh.write(raw)
    total, rows = decode_ladder(raw)
    return total, rows, fname

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--class-filter', default=None)
    args = ap.parse_args()
    extra = {'class': args.class_filter} if args.class_filter else None
    total, rows, fname = fetch_and_save(args.slug, extra, args.class_filter)
    print('saved', fname, 'total=', total, 'rows=', len(rows))
