import sys
def sec(s):
    h,m,ss = map(int, s[1:9].split(':')); return h*3600+m*60+ss
f, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
buf = [l.rstrip()[11:] for l in open(f, encoding='utf-8') if a <= sec(l) <= b]
print(' '.join(buf))
