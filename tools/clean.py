#!/usr/bin/env python3
"""Convert raw Squarespace pages in raw/ into standalone static pages in site/."""
import re, html, json, os, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, SITE = os.path.join(ROOT, 'raw'), os.path.join(ROOT, 'site')
AMAP = json.load(open(os.path.join(ROOT, 'tools', 'asset-map.json')))
CONTACT_EMAIL = 'blockchainbywomen@gmail.com'
PAGES = {'index': '', 'about-1': 'about-1', 'assessment': 'assessment', 'connect': 'connect', 'donate': 'donate',
         'membership': 'membership', 'recordings': 'recordings', 'tailor-learning': 'tailor-learning',
         'new-page-26': 'new-page-26', 'new-page-1': 'new-page-1'}
COMPONENT_CSS = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SITE, 'assets', 'css', '*.css')))
FONTS = 'https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Montserrat:wght@400;500;600;700&family=Nunito+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap'

def balanced_end(s, start):
    """Index just past the closing tag of the element whose opening '<div' begins at `start`."""
    depth = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', s[start:]):
        depth += 1 if m.group(0).startswith('<div') else -1
        if depth == 0:
            return start + m.end()
    raise ValueError('unbalanced div at %d' % start)

def remove_blocks(s, open_pat, replacer=lambda blk: ''):
    out, pos = [], 0
    while True:
        m = re.compile(open_pat, re.S).search(s, pos)
        if not m: break
        end = balanced_end(s, m.start())
        out.append(s[pos:m.start()]); out.append(replacer(s[m.start():end])); pos = end
    out.append(s[pos:]); return ''.join(out)

def extract_code_containers(s, replacer):
    """Squarespace code blocks hold user-authored HTML (often a whole <html> document with
    unbalanced tags), so find their end by the closing </html> plus the container's own </div>."""
    out, pos = [], 0
    open_pat = re.compile(r'<div\s+class="sqs-code-container"', re.S)
    while True:
        m = open_pat.search(s, pos)
        if not m: break
        h = s.find('</html>', m.start())
        if h != -1:
            m2 = re.compile(r'</html>\s*</div>', re.S).match(s, h)
            end = m2.end() if m2 else balanced_end(s, m.start())
        else:
            end = balanced_end(s, m.start())
        out.append(s[pos:m.start()]); out.append(replacer(s[m.start():end])); pos = end
    out.append(s[pos:]); return ''.join(out)

def local_asset(url, prefix):
    b = url.split('?')[0]
    if b.startswith('http:'): b = 'https:' + b[5:]
    if b.startswith('//'): b = 'https:' + b
    for key in (b, b.replace('https:', '', 1), b.replace('https:', 'http:', 1)):
        if key in AMAP: return prefix + AMAP[key]
    return None

def rewrite_asset_urls(s, prefix):
    def rep(m):
        u = html.unescape(m.group(0)); loc = local_asset(u, prefix)
        return loc if loc else m.group(0)
    return re.sub(r'(?:https?:)?//(?:images\.squarespace-cdn\.com|static1\.squarespace\.com)/[^\s"\'<>)\]]+', rep, s)

def youtube_iframe(data_html):
    frag = html.unescape(data_html)
    m = re.search(r'youtube\.com(?:%2F|/)embed(?:%2F|/)([A-Za-z0-9_-]{6,})', frag)
    if not m:
        m = re.search(r'youtube\.com%2Fwatch%3Fv%3D([A-Za-z0-9_-]{6,})', frag)
    if not m: return frag  # unknown provider: keep original markup
    vid = m.group(1)
    start = re.search(r'[?&;]start=(\d+)', frag)
    src = 'https://www.youtube.com/embed/%s?rel=0%s' % (vid, ('&start=' + start.group(1)) if start else '')
    return ('<iframe src="%s" loading="lazy" title="YouTube video" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe>') % src

def fix_img(tag, prefix, lazy=True):
    attrs = dict(re.findall(r'([a-zA-Z-]+)="([^"]*)"', tag))
    src = attrs.get('data-src') or attrs.get('src') or attrs.get('data-image')
    if not src: return tag
    loc = local_asset(html.unescape(src), prefix)
    if not loc: return tag
    for k in ('srcset', 'sizes', 'data-load', 'data-loader', 'data-licensed-asset-preview', 'elementtiming'):
        attrs.pop(k, None)
    attrs['src'] = loc
    attrs.pop('data-src', None); attrs.pop('data-image', None)
    if 'style' in attrs:  # Squarespace inline sizing/positioning for lazy images
        attrs['style'] = re.sub(r'(?<![a-z-])(width|height|left|top|position)\s*:[^;]*;?', '', attrs['style']).strip()
        if not attrs['style']: del attrs['style']
    if lazy and 'loading' not in attrs: attrs['loading'] = 'lazy'
    return '<img ' + ' '.join('%s="%s"' % (k, v) for k, v in attrs.items()) + '>'

def build_video_grid(gallery, prefix):
    items = []
    for slide in re.findall(r'<div class="slide".*?(?=<!--SLIDE-->|<!--THUMBNAILS-->|$)', gallery, re.S):
        m = re.search(r'data-html="([^"]*)"', slide); frame = youtube_iframe(m.group(1)) if m else ''
        items.append(frame)
    titles = re.findall(r'<div class="thumbnail">\s*<img[^>]*alt="([^"]*)"', gallery)
    thumbs = re.findall(r'<div class="thumbnail">\s*<img[^>]*data-src="([^"]*)"', gallery)
    out = ['<div class="video-grid">']
    for i, frame in enumerate(items):
        vid = re.search(r'embed/([A-Za-z0-9_-]+)', frame); vid = vid.group(1) if vid else ''
        title = titles[i] if i < len(titles) else ''
        thumb = local_asset(html.unescape(thumbs[i]), prefix) if i < len(thumbs) else None
        out.append('<div class="video-card">')
        if thumb and vid:
            out.append('<div class="video-item" data-yt="%s"><img src="%s" alt="%s" loading="lazy"><div class="sqs-video-icon"></div></div>' % (vid, thumb, title))
        else:
            out.append('<div class="video-item">%s</div>' % frame)
        if title: out.append('<p class="video-title">%s</p>' % title)
        out.append('</div>')
    out.append('</div>')
    return '\n'.join(out)

def clean(name, path):
    s = open(os.path.join(RAW, name + '.html')).read()
    prefix = '' if path == '' else '../'
    # 1. protect code blocks (the assessment tools) from script stripping.
    #    Inline scripts are swapped for placeholders first so that '<div' strings inside
    #    JavaScript cannot confuse the balanced-div scan that finds the end of a code block.
    inline_scripts = []
    def stash(m):
        inline_scripts.append(m.group(0)); return '@@SCRIPT%d@@' % (len(inline_scripts) - 1)
    s = re.sub(r'<script\b(?![^>]*\ssrc=)[^>]*>.*?</script>', stash, s, flags=re.S)
    code_blocks = []
    def keep(blk):
        blk = re.sub(r'@@SCRIPT(\d+)@@', lambda m: inline_scripts[int(m.group(1))], blk)  # restore scripts inside code blocks
        code_blocks.append(blk); return '@@CODEBLOCK%d@@' % (len(code_blocks) - 1)
    s = extract_code_containers(s, keep)
    # 2. strip all remaining scripts (Squarespace runtime, analytics, external bundles)
    s = re.sub(r'@@SCRIPT\d+@@', '', s)
    s = re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<noscript>.*?</noscript>', '', s, flags=re.S)
    # 3. head: drop squarespace/typekit links and stray meta
    s = re.sub(r'<link\b[^>]*(squarespace|sqspcdn|typekit)[^>]*>\s*', '', s)
    s = re.sub(r'<link\b[^>]*rel="(alternate|image_src|preconnect)"[^>]*>\s*', '', s)
    s = re.sub(r'<link\b[^>]*rel="canonical"[^>]*>', '<link rel="canonical" href="https://blockchainbywomen.com/%s"/>' % path, s)
    s = re.sub(r'<meta\b[^>]*name="generator"[^>]*>\s*', '', s)
    s = re.sub(r'<style>@keyframes fonts-loading.*?</style>', '', s, flags=re.S)
    favicon = local_asset('https://images.squarespace-cdn.com/content/v1/5b8fb87d70e802670d0f5f75/1604358783674-9FAR1C7J1EU5NKHSOZR1/bcxw_logomark_black.png', prefix)
    head_add = ['<link rel="icon" type="image/png" href="%s">' % favicon if favicon else '',
                '<link rel="stylesheet" href="%s">' % FONTS,
                '<link rel="stylesheet" href="%sassets/site.css">' % prefix]
    head_add += ['<link rel="stylesheet" href="%sassets/css/%s">' % (prefix, c) for c in COMPONENT_CSS]
    head_add.append('<link rel="stylesheet" href="%sassets/local.css">' % prefix)
    s = s.replace('</head>', '\n'.join(head_add) + '\n</head>', 1)
    # 4. body: squarespace-only chrome
    s = remove_blocks(s, r'<div class="user-account-link">')
    s = re.sub(r'<div class="sqs-cart-dropzone"></div>', '', s)
    s = remove_blocks(s, r'<div class="sqs-announcement-bar-dropzone"')
    s = remove_blocks(s, r'<div[^>]*class="[^"]*\bsqs-block-newsletter\b[^"]*"')
    mailto = ('<div class="sqs-block html-block sqs-block-html"><div class="sqs-block-content"><div class="sqs-html-content contact-email">'
              '<a class="sqs-block-button-element--medium sqs-button-element--primary sqs-block-button-element" href="mailto:%s?subject=Blockchain%%20by%%20Women">Email Us</a>'
              '<p><a href="mailto:%s">%s</a></p></div></div></div>') % (CONTACT_EMAIL, CONTACT_EMAIL, CONTACT_EMAIL)
    s = remove_blocks(s, r'<div[^>]*class="[^"]*\bsqs-block-form\b[^"]*"', lambda blk: mailto)
    # 5. video wrappers -> direct iframes
    def video_rep(blk):
        m = re.search(r'data-html="([^"]*)"', blk)
        return '<div class="sqs-video-wrapper">%s</div>' % youtube_iframe(m.group(1)) if m else blk
    if name == 'recordings':
        s = remove_blocks(s, r'<div class="sqs-system-gallery', lambda blk: build_video_grid(blk, prefix))
    s = remove_blocks(s, r'<div class="sqs-video-wrapper"', video_rep)
    # 6. images
    s = re.sub(r'<img\b[^>]*>', lambda m: fix_img(m.group(0), prefix, lazy=('id="logoImage"' not in s[max(0, m.start()-200):m.start()])), s)
    s = re.sub(r'(<figure id="thumbnail" class=")loading ', r'\1', s)
    s = rewrite_asset_urls(s, prefix)
    # 7. attributes & links pointing at squarespace
    s = re.sub(r'\s+data-block-(css|scripts)="[^"]*"', '', s)
    s = re.sub(r'https?://(www\.)?blockchainbywomen\.com(?=["/\s])', '', s)
    s = re.sub(r'https?://caterpillar-pufferfish-k9l6\.squarespace\.com', '', s)
    # internal links: root-relative -> relative so the github.io preview also works
    def link_rep(m):
        target = m.group(2)
        if target == '/': return '%s="%s"' % (m.group(1), prefix or './')
        if target.startswith('/#'): return '%s="%s"' % (m.group(1), prefix + target[1:] if prefix else target[1:])
        if re.match(r'/[a-z0-9-]+/?$', target):
            slug = target.strip('/')
            if slug in PAGES.values(): return '%s="%s%s/"' % (m.group(1), prefix or './', slug)
        return m.group(0)
    s = re.sub(r'\b(href)="(/[^"]*)"', link_rep, s)
    s = s.replace('href="@blockchainbywo2"', 'href="https://twitter.com/blockchainbywo2"')  # broken on the live site too
    s = s.replace('xlink:href="/universal/svg/social-accounts.svg#', 'xlink:href="#')  # symbols are defined inline at the end of body
    # 8. restore code blocks, add site.js
    for i, blk in enumerate(code_blocks): s = s.replace('@@CODEBLOCK%d@@' % i, blk)
    k = s.rfind('</body>')  # the last one: embedded code blocks carry their own </body>
    s = s[:k] + '<script src="%sassets/site.js" defer></script>\n' % prefix + s[k:]
    out_dir = os.path.join(SITE, path); os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, 'index.html'), 'w').write(s)
    left = sorted(set(re.findall(r'[^\s"\'>]*(?:squarespace|sqspcdn|typekit)[^\s"\'<]*', s)))
    print('%-16s %7d bytes  leftover refs: %s' % (name, len(s), left[:6]))

for name, path in PAGES.items(): clean(name, path)
