import sys, re
# Lists painted paths of the main content stream: clip rect, stroke and fill colours, bbox and centre.
txt = open(sys.argv[1], encoding='latin1').read()
start = txt.index('=== obj 9 dict')
end = txt.index('=== obj', start + 10)
toks = txt[start:end].split('\n', 1)[1].split()
stack = []; st = {'clip': None, 'RG': None, 'rg': None}
nums = []; pts = []; out = []
paint = {'S', 's', 'f', 'F', 'f*', 'B', 'B*', 'b', 'b*', 'n'}
i = 0
while i < len(toks):
    t = toks[i]
    try:
        float(t); nums.append(t); i += 1; continue
    except ValueError:
        pass
    if t == 'q': stack.append(dict(st))
    elif t == 'Q': st = stack.pop() if stack else st
    elif t == 'RG': st['RG'] = tuple(round(float(x), 4) for x in nums[-3:])
    elif t == 'rg': st['rg'] = tuple(round(float(x), 4) for x in nums[-3:])
    elif t == 'G': st['RG'] = ('gray', float(nums[-1]))
    elif t == 'g': st['rg'] = ('gray', float(nums[-1]))
    elif t == 're':
        pts.append(('re', [float(x) for x in nums[-4:]]))
    elif t in ('m', 'l'): pts.append((t, [float(x) for x in nums[-2:]]))
    elif t == 'c': pts.append((t, [float(x) for x in nums[-6:]]))
    elif t == 'W':
        r = [p for p in pts if p[0] == 're']
        if r: st['clip'] = tuple(round(x, 2) for x in r[-1][1])
    elif t in paint:
        if t != 'n':
            xs = []; ys = []
            for k, v in pts:
                if k == 're': continue
                xs += v[0::2]; ys += v[1::2]
            if xs:
                out.append((st['clip'], st['RG'], st['rg'], t, min(xs), max(xs), min(ys), max(ys), len(pts)))
        pts = []
    nums = [] if t not in ('cs', 'CS', 'gs', 'd', '[', ']') else nums
    i += 1
for o in out:
    print(o[0], o[1], o[2], o[3], 'x[%.4f,%.4f] y[%.4f,%.4f] n=%d' % o[4:])
