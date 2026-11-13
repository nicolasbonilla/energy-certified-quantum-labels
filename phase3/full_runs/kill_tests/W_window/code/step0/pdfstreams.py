import sys, re, zlib
data = open(sys.argv[1], 'rb').read()
out = open(sys.argv[2], 'w')
for m in re.finditer(rb'(\d+) 0 obj(.*?)endobj', data, re.S):
    num, body = m.group(1).decode(), m.group(2)
    d = body.split(b'stream', 1)[0]
    out.write('=== obj %s dict: %s\n' % (num, d[:300].decode('latin1').replace('\n', ' ')))
    sm = re.search(rb'stream\r?\n(.*?)\r?\nendstream', body, re.S)
    if sm:
        raw = sm.group(1)
        try:
            txt = zlib.decompress(raw) if b'FlateDecode' in d else raw
            out.write(txt.decode('latin1')[:200000] + '\n')
        except Exception as e:
            out.write('decompress error %s\n' % e)
out.close()
