#!/usr/bin/env python3
"""Download every image/asset referenced by the raw Squarespace pages into site/assets/img.
Writes tools/asset-map.json mapping original base URL -> local path."""
import re, html, glob, json, os, hashlib, urllib.request, urllib.parse, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw'); OUT = os.path.join(ROOT, 'site', 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
pat = r'(?:https?:)?//(?:images\.squarespace-cdn\.com|static1\.squarespace\.com)/[^\s"\'<>)\]]+'
bases = set()
for p in glob.glob(os.path.join(RAW, '*.html')):
    s = html.unescape(open(p).read())
    for u in re.findall(pat, s):
        b = u.split('?')[0].rstrip(',&')
        if b.startswith('http:'): b = 'https:' + b[5:]
        if b.startswith('//'): b = 'https:' + b
        if '/content/v1/' in b or ('/static/' in b and '/t/' in b) or re.search(r'\.(png|jpe?g|gif|webp|svg|ico)$', b, re.I):
            bases.add(b)
mapfile = os.path.join(ROOT, 'tools', 'asset-map.json')
amap = json.load(open(mapfile)) if os.path.exists(mapfile) else {}
for b in sorted(bases):
    if b in amap and os.path.exists(os.path.join(ROOT, 'site', amap[b])): continue
    url = ('https:' + b) if b.startswith('//') else b
    name = urllib.parse.unquote(b.split('/')[-1]) or 'asset'
    name = re.sub(r'[^A-Za-z0-9._-]+', '_', name)
    h = hashlib.sha1(b.encode()).hexdigest()[:8]
    local = f'assets/img/{h}-{name}'
    fetch = url + '?format=2500w' if 'images.squarespace-cdn.com' in url else url
    try:
        req = urllib.request.Request(fetch, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print('FAIL', fetch, e, file=sys.stderr); continue
    open(os.path.join(ROOT, 'site', local), 'wb').write(data)
    amap[b] = local
    print(len(data), local)
json.dump(amap, open(mapfile, 'w'), indent=1, sort_keys=True)
print('mapped', len(amap))
