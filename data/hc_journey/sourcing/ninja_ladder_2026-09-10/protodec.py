import sys

def varint(b, i):
    s = 0
    r = 0
    while i < len(b):
        c = b[i]
        r |= (c & 0x7f) << s
        i += 1
        if not c & 0x80:
            return r, i
        s += 7
    raise ValueError("truncated varint")

def parse(b):
    out = []
    i = 0
    while i < len(b):
        key, i = varint(b, i)
        f, wt = key >> 3, key & 7
        if wt == 0:
            v, i = varint(b, i)
            out.append((f, 0, v))
        elif wt == 1:
            out.append((f, 1, b[i:i+8])); i += 8
        elif wt == 5:
            out.append((f, 5, b[i:i+4])); i += 4
        elif wt == 2:
            ln, i = varint(b, i)
            if i + ln > len(b):
                raise ValueError("length-delimited overrun")
            out.append((f, 2, b[i:i+ln])); i += ln
        else:
            raise ValueError("unknown wire type %d" % wt)
    return out

def unpack_varints(b):
    """Decode a packed-varint byte string (protobuf packed repeated field) into a list of ints."""
    vals = []
    i = 0
    while i < len(b):
        v, i = varint(b, i)
        vals.append(v)
    return vals

def decode_ladder(raw):
    """Decode a poe.ninja POE2 builds-search protobuf response.
    Returns (total, rows) where rows is a list of dicts with rank/name/account/level.
    class is left as a raw enum id (int) since no id->name table is available locally.
    """
    top = parse(raw)
    result_msg = None
    for f, wt, v in top:
        if f == 1 and wt == 2:
            result_msg = v
    if result_msg is None:
        result_msg = raw
    fields = parse(result_msg)
    total = None
    for f, wt, v in fields:
        if f == 1 and wt == 0:
            total = v

    names, accounts, levels, classes = [], [], [], []
    for f, wt, v in fields:
        if f != 12 or wt != 2:
            continue
        col = parse(v)
        key = None
        for cf, cwt, cv in col:
            if cf == 1 and cwt == 2:
                key = cv.decode('utf-8', errors='replace')
                break
        if key == 'name':
            names = [cv.decode('utf-8', errors='replace') for cf, cwt, cv in col if cf == 7 and cwt == 2]
        elif key == 'account':
            accounts = [cv.decode('utf-8', errors='replace') for cf, cwt, cv in col if cf == 7 and cwt == 2]
        elif key == 'level':
            for cf, cwt, cv in col:
                if cf == 6 and cwt == 2:
                    levels = unpack_varints(cv)
        elif key == 'class':
            for cf, cwt, cv in col:
                if cf == 6 and cwt == 2:
                    classes = unpack_varints(cv)

    n = max(len(names), len(accounts))
    rows = []
    for idx in range(n):
        rows.append({
            'rank': idx + 1,
            'name': names[idx] if idx < len(names) else None,
            'account': accounts[idx] if idx < len(accounts) else None,
            'level': levels[idx] if idx < len(levels) else None,
            'class_id': classes[idx] if idx < len(classes) else None,
        })
    return total, rows

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'rb') as fh:
        raw = fh.read()
    total, rows = decode_ladder(raw)
    print('total=', total, 'rows=', len(rows))
    for r in rows[:10]:
        print(r)
