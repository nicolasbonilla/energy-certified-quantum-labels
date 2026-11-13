"""arXiv API queries for R3 (generic User-Agent, no mailto, >= 4.5 s between calls).
Usage: python -I arxiv_q.py <outdir> <tag> <mode> <query-or-idlist> [max_results]
mode = search | ids.  Raw XML saved to <outdir>/<tag>.xml; a short parsed listing printed."""
import sys, io, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
outdir, tag, mode, q = sys.argv[1:5]
mx = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 25
if mode == 'search':
    params = {'search_query': q, 'start': 0, 'max_results': mx, 'sortBy': 'relevance'}
else:
    params = {'id_list': q, 'max_results': 100}
if mode == 'parse':
    data = open(os.path.join(outdir, tag + '.xml'), 'rb').read()
else:
    url = 'http://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research-literature-check)'})
    time.sleep(4.5)
    data = urllib.request.urlopen(req, timeout=60).read()
    open(os.path.join(outdir, tag + '.xml'), 'wb').write(data)
ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
root = ET.fromstring(data)
tot = root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults')
print('totalResults', tot.text if tot is not None else '?')
for e in root.findall('a:entry', ns):
    i = e.find('a:id', ns).text.split('/abs/')[-1]
    t = ' '.join(e.find('a:title', ns).text.split())
    pub = e.find('a:published', ns).text[:10]
    upd = e.find('a:updated', ns).text[:10]
    au = [a.find('a:name', ns).text for a in e.findall('a:author', ns)]
    jr = e.find('x:journal_ref', ns)
    ab = ' '.join(e.find('a:summary', ns).text.split())
    print(f"- {i} | {pub} (upd {upd}) | {t} | {', '.join(au[:4])}{' et al.' if len(au) > 4 else ''} | JR: {jr.text if jr is not None else '-'}")
    if mode == 'search' or '-v' in sys.argv:
        print('    ABS:', ab[:int(os.environ.get('ABL','700'))])
