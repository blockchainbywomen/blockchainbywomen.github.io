#!/usr/bin/env python3
"""Reorganise the static site around Education, Events and Programs.

Run from the repo root:  python3 tools/reorg.py
Reads the pre-reorganisation pages from git (commit SRC) so it can be re-run safely,
and writes: site/index.html, site/education/, site/events/, site/programs/,
redirect stubs at the old addresses, and a new header/footer on About and Join.
"""
import html
import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
SRC = "fdeeeb4"  # last commit before the reorganisation
TAGLINE = "Building and Using Blockchain and AI Safely"
EMAIL = "blockchainbywomen@gmail.com"
# "join today" button on the Join page. Paste the Google Form link here (see JOIN_FORM.md); until
# then the button opens an email with the same three questions.
JOIN_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdrRIKoa96bWPIbpA5pLjKxndTlqwZeYOyyrrdgHL0gI5GufQ/viewform"
SOCIAL = [
    ("LinkedIn", "https://www.linkedin.com/company/blockchain-by-women-official/"),
    ("Facebook", "https://www.facebook.com/BlockchainByWomen"),
    ("Twitter", "https://twitter.com/blockchainbywo2"),
]
NAV = [("Education", "education/"), ("Events", "events/"), ("Programs", "programs/"), ("About", "about-1/")]


def old(path):
    return subprocess.run(["git", "show", f"{SRC}:site/{path}"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")


def write(path, text):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", path, f"{len(text) / 1024:.0f} KB")


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- shell

def header(rel, active=None):
    links = "".join(
        f'<a href="{rel}{href}"{" aria-current=\"page\"" if name == active else ""}>{name.lower()}</a>' for name, href in NAV
    )
    return f"""<header class="bw-header">
  <div class="bw-wrap bw-header-in">
    <a class="bw-logo" href="{rel or './'}"><img src="{rel}assets/brand/baiw-wordmark-reverse.svg" alt="blockch[AI]n by women" width="300" height="50"></a>
    <button class="bw-menu" aria-expanded="false" aria-controls="bw-nav">menu</button>
    <nav id="bw-nav" class="bw-nav" aria-label="Main">{links}<a class="bw-join" href="{rel}donate/"{' aria-current="page"' if active == "Join" else ""}>join</a></nav>
  </div>
</header>"""


def footer(rel):
    social = "".join(f'<a href="{u}">{n}</a>' for n, u in SOCIAL)
    links = "".join(f'<a href="{rel}{href}">{name}</a>' for name, href in NAV + [("Join / donate", "donate/")])
    return f"""<footer class="bw-footer" id="connect">
  <div class="bw-wrap bw-footer-in">
    <div>
      <img src="{rel}assets/brand/baiw-mark-reverse.svg" alt="b[AI]w" width="120" height="45">
      <p class="bw-tag">{TAGLINE}</p>
    </div>
    <div>
      <h2>connect</h2>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="bw-links">{social}</p>
    </div>
    <div>
      <h2>site</h2>
      <p class="bw-links">{links}</p>
    </div>
  </div>
  <div class="bw-wrap bw-legal">Blockchain by Women is a 501(c)(3) not-for-profit organization, EIN 83-1984602.</div>
</footer>"""


HEAD_LINKS = """<link rel="icon" type="image/svg+xml" href="{rel}assets/brand/baiw-icon-ink.svg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="{rel}assets/baiw.css">"""


def page(path, title, desc, main, active=None):
    rel = "../" * path.count("/")
    full_title = "blockchAIn by women" if not title else f"{title} — blockchAIn by women"
    write(path, f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:site_name" content="blockchAIn by women">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{rel}assets/brand/baiw-icon-ink-1024.png">
{HEAD_LINKS.format(rel=rel)}
</head>
<body class="bw">
<a class="bw-skip" href="#main">Skip to content</a>
{header(rel, active)}
<main id="main">
{main}
</main>
{footer(rel)}
<script src="{rel}assets/baiw.js" defer></script>
</body>
</html>
""")


def redirect(path, target, label):
    rel = "../" * path.count("/")
    write(path, f"""<!doctype html>
<html lang="en-US"><head><meta charset="utf-8">
<title>Moved — blockchAIn by women</title>
<link rel="canonical" href="{rel}{target}">
<meta http-equiv="refresh" content="0; url={rel}{target}">
<meta name="robots" content="noindex">
</head><body><p>This page has moved to <a href="{rel}{target}">{label}</a>.</p></body></html>
""")


def video_card(rel, yt, title, img=None, hid=True):
    src = f"{rel}assets/img/{img}" if img else f"https://i.ytimg.com/vi/{yt}/hqdefault.jpg"
    return f"""<figure class="bw-video"{f' id="v-{yt}"' if hid else ''}>
  <button class="bw-play" data-yt="{yt}" aria-label="Play video: {esc(title)}"><img src="{src}" alt="" loading="lazy"><span></span></button>
  <figcaption>{esc(title)}</figcaption>
</figure>"""


# ---------------------------------------------------------------- content data

SCAM_VIDEOS = [  # titles and descriptions as written in the scam-risk quiz
    ("CCasje15UwU", "Pig Butchering Scam: How Romance Leads to Financial Ruin", "The scam that combines romance fraud with investment theft."),
    ("P1i3rd8p5VI", "Fake Job Offer Scam: How to Spot Employment Fraud", "Fake job offers and employment scams that steal your personal information."),
    ("j0oszwI_Gjk", "Zelle and Payment App Scams: Protect Your Money", "How scammers exploit payment apps like Zelle and how to keep your money safe."),
    ("4jZNwKyjPtw", "Tech Support Scam: Don't Fall for Fake Computer Help", "Fake tech support calls that try to access your computer and steal your information."),
    ("yXbNx9hZ-RU", "QR Code Phishing: The Hidden Danger in Plain Sight", "How malicious QR codes can compromise your security and how to scan safely."),
    ("56p6OcvfKtI", "Fake Rental Scam: How to Spot Housing Fraud", "Fake rental listings and housing scams that steal your deposit."),
    ("LnR40qP07Hw", "Deepfake Voice Scam: When Scammers Clone Your Loved Ones", "Scams that use AI to clone voices, and how to protect yourself."),
]

NEW_RECORDINGS = {  # recordings added after the Squarespace page: video id -> (title, thumbnail in site/assets/img)
    "cdhwCGAiMTc": ("Investing Safely with AI Agents, Human Advisors, and Online Platforms", "cdhwCGAiMTc.jpg"),
}
TOPICS = [  # recordings grouped under the topics the "find videos" quiz uses
    ("AI in finance", ["cdhwCGAiMTc", "x4zN1LkyELo"]),
    ("Security, privacy and risk", ["yPQ7pcfhbVQ", "Yx1QI5mBLMQ", "_22q2qYGsP4", "75IhGp0PPQA", "oFBLrZGBQ2I"]),
    ("Trading and investments", ["qNAY0aJMwws", "5ccGsciST9E", "mFJ9Bm51CrY"]),
    ("Digital currencies and stablecoins", ["go_-De5p3Ts", "pH2EM0cE3jg"]),
    ("Blockchain applications", ["cwyD0zjNyWc", "s0uLGGoKtWQ", "n1CCQ33zvvU", "ojxdiXKKArs", "ZPg8hQyNnqI"]),
]

# Events: (title, date, [block numbers on the old Events page], video id, extra link)
UPCOMING = [  # (date, title, place/note)
    ("December 10, 2026", "Digital Finance Roundtable: Collision of Digital Assets, Fintech, Trad-Fi, Agentic Finance", "In partnership with Blockchain Foundation · Washington, D.C. · details to come"),
    ("January 14, 2027", "7th Annual Congressional Briefing of Women in Blockchain", "In partnership with Blockchain Foundation · Delegation to Capitol Hill · Washington, D.C. · save the date"),
]
PAST = [
    ("Investing with Human Advisors, Online Platforms & AI Agents", "March 26, 2026 · live webcast", [0], "cdhwCGAiMTc", None),
    ("6th Annual Congressional Briefing: Women of Color in Blockchain", "December 10, 2025 · Washington, D.C.", [2], None, None),
    ("Blockchain Futurist Conference / ETHWOMEN — Building Together: The Power of Women-Led Communities", "November 2025", [3], None, None),
    ("Fintech & Cybersecurity: Perspectives and Best Practices", "September 23, 2025 · Redwood City", [5], None, None),
    ("Online Safety for Women in the Age of AI", "May 8, 2025 · San Francisco", [4], None, None),
    ("Role of AI in Finance in 2025", "December 4, 2024", [6, 7], "x4zN1LkyELo", None),
    ("Mobile Privacy Unveiled: Fortifying Your Mobile Frontiers", "May 2024 · webinar", [9], "yPQ7pcfhbVQ", None),
    ("2024 Web3, Crypto and Blockchain Projects and Investments", "2024", [10], "qNAY0aJMwws", None),
    ("Aprio LLP's Inaugural Blockchain & Crypto Meetup: Investing in Change", "", [8], None, None),
    ("Data Driven Investments: Blockchain Companies and Protocols", "", [14, 16], None, None),
    ("Data Driven Investments and Execution", "", [15, 17], "5ccGsciST9E", None),
    ("Fireside chat: CBDC Technology and Retail Use Cases", "", [19], "dzan4-jV-FE", None),
    ("Weighing the Risks and Opportunities of DeFi and Crypto", "2020", [22], None, None),
    ("Lending, Derivatives and Reducing Credit and Regulatory Risk", "2020", [25], "2om3MQVGclE", None),
    ("Mitigating Liquidity and Regulatory Risk", "May 20, 2020", [29], "75IhGp0PPQA", None),
    ("Reduce Risk in the Exchange of Digital Assets and Securities", "May 6, 2020", [31], "oFBLrZGBQ2I", None),
    ("Stimulus, Regulation and Digital Assets/Currencies", "April 22, 2020", [34], "pH2EM0cE3jg", None),
    ("Protecting Yourself On and Off Chain", "April 16, 2020", [36], "ywyQITtGP0A", None),
    ("Blockchain Use Cases: Stablecoins in 2020", "February 18, 2020", [39, 41, 43], "go_-De5p3Ts", None),
]
ARCHIVE = [
    ("Protocol Battle: Enabling Rapid Application Development & Adoption", "October 30, 2019", [48, 49, 50], "n1CCQ33zvvU", None),
    ("From Blockchain Pilot to Production: Real Estate, Health, Media", "August 28, 2019", [52, 53, 55], "cwyD0zjNyWc", None),
    ("From Blockchain Pilot to Production: A Financial Services Perspective", "June 27, 2019", [57, 58, 59], "ojxdiXKKArs", None),
    ("Proof of Happy Hour", "May 14, 2019 · New York", [61, 62, 66], None, None),
    ("What's Working? What's Not?", "March 2019", [67, 68, 69, 70, 71, 72, 73, 74, 75], "ZPg8hQyNnqI", None),
    ("Blockchain in Energy: Use Cases and Projects", "February 2019", [77, 79, 80, 81, 84, 85], "s0uLGGoKtWQ", None),
    ("Why Blockchain in 2019", "January 2019", [86, 87, 88, 92, 93, 96], None, None),
]

SPONSORS = [
    ("Silvergate Bank", "2e996515-Silvergate_Bank.png"), ("BlockchainIntel", "38df261b-blockchain_intel_grid.png"),
    ("K&L Gates", "60ae74e9-K_L_Gates.png"), ("GE", "b72a5fdf-GE_logo.png"), ("Blockchain Capital", "967937ae-BCapital.png"),
    ("Target", "fa3fcd36-Target.png"), ("Protocol Labs", "37a6c3a7-Protocol_Labs_copy.jpg"), ("Celo", "0aabfb86-CeloLogo.png"),
    ("Kadena", "ac99c4d7-Kadena.png"), ("OKCoin", "51eeaf39-OkCoin.jpg"), ("Stellar", "26067722-Stellar.png"), ("Dash", "fe5b94b8-Dash.png"),
]


# ---------------------------------------------------------------- pull content out of the old pages

def recordings():
    s = old("recordings/index.html")
    out = {}
    for m in re.finditer(r'data-yt="([^"]+)"><img src="\.\./assets/img/([^"]+)" alt="([^"]*)"', s):
        out[m.group(1)] = (html.unescape(m.group(3)), m.group(2))
    out.update(NEW_RECORDINGS)
    return out


def clean(fragment):
    """Keep the author's words and links; drop Squarespace attributes and headings (titles are set above)."""
    f = re.sub(r"<(script|style)\b.*?</\1>", "", fragment, flags=re.S)
    f = re.sub(r"<h[1-4]\b.*?</h[1-4]>", "", f, flags=re.S)

    def tag(m):
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if name not in ("p", "ul", "ol", "li", "a", "strong", "em", "br"):
            return ""
        if name == "a" and not close:
            href = re.search(r'href="([^"]*)"', attrs)
            return f'<a href="{href.group(1)}">' if href else "<a>"
        return f"<{close}{name}>"

    f = re.sub(r"<(/?)([a-zA-Z0-9]+)([^>]*)>", tag, f)
    f = re.sub(r"<p>(\s|&nbsp;|<br>)*</p>", "", f)
    f = re.sub(r"<li>\s*<p>(.*?)</p>\s*</li>", r"<li>\1</li>", f, flags=re.S)
    f = f.replace("https://studio.youtube.com/video/dzan4-jV-FE/edit", "https://youtu.be/dzan4-jV-FE")
    f = re.sub(r"</?em>", "", f)
    f = re.sub(r"<p>\s*<strong>([^<]*)</strong>\s*</p>", r"<p>\1</p>", f)  # whole-paragraph bold was a heading style
    f = re.sub(r"<p>[^<]*Register here[^<]*(<a[^>]*>[^<]*</a>)?[^<]*</p>", "", f)  # sign-up lines for events now past
    # make bare web addresses clickable
    f = re.sub(r'(?<![">])(https?://[^\s<]+[^\s<.,)])(?![^<]*</a>)', r'<a href="\1">\1</a>', f)
    # Karen, 2026-11-10: the Telegram group is no longer used; drop old invitations to it
    f = re.sub(r"\s*Please let us know questions[^<]*telegram group\s*<a [^>]*>[^<]*</a>", "", f, flags=re.I)
    return re.sub(r"\n\s*\n+", "\n", f).strip()


def event_blocks():
    s = old("membership/index.html")
    main = s[s.index("<main"):s.index("</main>")]
    pos = [m.start() for m in re.finditer(r'<div class="sqs-block ', main)] + [len(main)]
    blocks = []
    for a, b in zip(pos, pos[1:]):
        chunk = main[a:b]
        texts = re.findall(r'<div class="sqs-html-content"[^>]*>(.*?)</div>', chunk, re.S)
        texts += re.findall(r'<div class="image-caption">(.*?)</div>', chunk, re.S)
        imgs = [i for i in re.findall(r'<img[^>]+src="\.\./assets/img/([^"]+)"', chunk) if "." in i and "logomark" not in i]
        blocks.append((clean("\n".join(texts)), imgs))
    return blocks


def event_card(ev, blocks, recs, rel="../"):
    title, date, idx, yt, link = ev
    body = "\n".join(blocks[i][0] for i in idx if blocks[i][0])
    imgs = [im for i in idx for im in blocks[i][1]]
    body = re.sub(r"<p>\s*" + re.escape(esc(title)) + r"\s*</p>", "", body)  # the title is already the heading
    paras = re.findall(r"<(?:p|ul|ol)>.*?</(?:p|ul|ol)>", body, re.S)
    first = paras[0] if paras and paras[0].startswith("<p>") else ""
    rest = body.replace(first, "", 1).strip() if first else body
    photos = "".join(f'<a href="{rel}assets/img/{im}"><img src="{rel}assets/img/{im}" alt="" loading="lazy"></a>' for im in imgs[1:])
    more = ""
    if rest or photos:
        more = f'<details><summary>read more</summary>{rest}{f"<div class=bw-photos>{photos}</div>" if photos else ""}</details>'
    actions = ""
    if yt:
        href = f"{rel}education/#v-{yt}" if yt in recs else f"https://youtu.be/{yt}"
        actions += f'<a class="bw-btn bw-btn-line" href="{href}">watch the recording</a>'
    if link:
        actions += f'<a class="bw-btn bw-btn-line" href="{link[1]}">{link[0].lower()}</a>'
    pic = f'<a class="bw-event-pic" href="{rel}assets/img/{imgs[0]}"><img src="{rel}assets/img/{imgs[0]}" alt="" loading="lazy"></a>' if imgs else '<div class="bw-event-pic bw-event-nopic"></div>'
    return f"""<article class="bw-event">
  {pic}
  <div>
    {f'<p class="bw-kicker">{esc(date)}</p>' if date else ''}
    <h3>{esc(title)}</h3>
    {first}
    {more}
    {f'<p class="bw-actions">{actions}</p>' if actions else ''}
  </div>
</article>"""


def quiz_doc(path):
    """The quizzes are complete little pages pasted into a code block: lift them out unchanged."""
    s = old(path)
    i = s.index("<!DOCTYPE html>", s.index('data-definition-name="website.components.code"'))
    j = s.index("</html>", i) + len("</html>")
    doc = s[i:j]
    if "tailor-learning" in path:            # add recordings made after the Squarespace quiz was written
        entry = """'investing_ai_agents': {
                title: "Investing Safely with AI Agents, Human Advisors, and Online Platforms",
                description: "A March 2026 panel on how to invest safely when advice comes from AI agents, online platforms and human advisors: what each is good for, where the risks are, and how to check before money moves.",
                url: "https://youtu.be/cdhwCGAiMTc",
                speakers: "Blockchain by Women panel, March 26, 2026",
                topics: ["AI", "Investing", "Safety"]
            },
            """
        assert doc.count("'ai_fintech': {") == 1 and doc.count("videos: ['ai_fintech']") == 1
        doc = doc.replace("'ai_fintech': {", entry + "'ai_fintech': {", 1)
        doc = doc.replace("videos: ['ai_fintech']", "videos: ['investing_ai_agents', 'ai_fintech']")
        doc = doc.replace("videos: ['investments', 'stablecoins', 'web3_projects']", "videos: ['investing_ai_agents', 'investments', 'stablecoins', 'web3_projects']")
    return doc


# ---------------------------------------------------------------- pages

def build_home(recs):
    latest = "cdhwCGAiMTc"
    sponsors = "".join(f'<img src="assets/img/{f}" alt="{esc(n)}" loading="lazy">' for n, f in SPONSORS)
    main = f"""<section class="bw-hero">
  <div class="bw-wrap bw-hero-in">
    <div>
      <h1>{TAGLINE}</h1>
      <p class="bw-lead">bAIW helps consumers protect themselves and everyone build safely in blockchain and AI.</p>
      <p class="bw-actions"><a class="bw-btn bw-btn-light" href="programs/">check out our programs</a></p>
    </div>
    <svg class="bw-blocks" viewBox="0 0 384 288" aria-hidden="true">
      <rect class="l" x="96" y="0" width="48" height="48"/><rect class="l" x="48" y="48" width="48" height="48"/><rect class="l" x="144" y="48" width="48" height="48"/>
      <rect class="l" x="0" y="96" width="48" height="48"/><rect class="l" x="192" y="192" width="48" height="48"/><rect class="l" x="288" y="192" width="48" height="48"/>
      <rect class="l" x="240" y="240" width="48" height="48"/><rect class="l" x="336" y="240" width="48" height="48"/><rect class="l" x="48" y="240" width="48" height="48"/>
      <rect class="w" x="192" y="0" width="192" height="192"/><rect class="s" x="48" y="96" width="144" height="144"/>
    </svg>
  </div>
</section>

<section class="bw-wrap bw-three">
  <article>
    <p class="bw-kicker">01</p>
    <h2><a href="education/">education</a></h2>
    <p>Watch past panels and videos on new blockchain and AI innovation and how to protect yourself.</p>
    {video_card('', latest, recs[latest][0], recs[latest][1], hid=False)}
    <p><a class="bw-more" href="education/">all videos</a></p>
  </article>
  <article>
    <p class="bw-kicker">02</p>
    <h2><a href="events/">events</a></h2>
    <p>Blockchain by Women events and events with our partners.</p>
    <ul class="bw-upcoming bw-upcoming-home">{upcoming_html()}</ul>
    <p><a class="bw-more" href="events/">all events</a></p>
  </article>
  <article>
    <p class="bw-kicker">03</p>
    <h2><a href="programs/">programs</a></h2>
    <p>Engage with the community on current challenges. We also help you check, report and protect against loss and fraud.</p>
    <ul class="bw-steps">
      <li><a href="programs/#events"><strong>Events</strong> Curated discussions with ecosystem leaders</a></li>
      <li><a href="programs/#detect"><strong>Detect</strong> Check a message, offer or wallet address</a></li>
      <li><a href="programs/#track"><strong>Track</strong> Monitor ongoing digital fraud</a></li>
      <li><a href="programs/#report"><strong>Report</strong> What to save and where to file</a></li>
      <li><a href="programs/#prevent"><strong>Prevent loss</strong> AI loss prevention, built safely</a></li>
    </ul>
    <p><a class="bw-btn" href="programs/#quiz">assess your scam risk</a></p>
  </article>
</section>

<section class="bw-band">
  <div class="bw-wrap bw-join-strip">
    <img src="assets/img/d14eb685-IMG_0187.jpg" alt="People talking at a Blockchain by Women meetup" loading="lazy">
    <div>
      <h2>get involved</h2>
      <p>Become part of our community: expert insights, a network of people building in this space, and tools to assess and reduce your own risk.</p>
      <p class="bw-actions"><a class="bw-btn" href="donate/">join or donate</a><a class="bw-btn bw-btn-line" href="about-1/">about us</a></p>
    </div>
  </div>
</section>

<section class="bw-wrap bw-sponsors">
  <h2>our sponsors</h2>
  <div>{sponsors}</div>
</section>"""
    page("index.html", "", f"{TAGLINE}. Education, events and digital asset fraud programs from bAIW, a 501(c)(3) not-for-profit.", main)


def build_education(recs):
    scams = "".join(video_card("../", yt, t) for yt, t, _ in SCAM_VIDEOS)
    groups = ""
    seen = set()
    for name, ids in TOPICS:
        cards = "".join(video_card("../", i, recs[i][0], recs[i][1]) for i in ids)
        seen.update(ids)
        groups += f'<h3>{name}</h3><div class="bw-grid">{cards}</div>'
    missing = set(recs) - seen
    assert not missing, f"recordings not placed in a topic: {missing}"
    main = f"""<section class="bw-wrap bw-pagehead">
  <h1>education</h1>
  <p class="bw-lead">Short videos on how scams work, and recordings of every panel we have hosted.</p>
  <p class="bw-jump"><a href="#scams">scam explainers</a><a href="#recordings">event recordings</a><a href="#find">find videos for me</a></p>
</section>

<section class="bw-wrap" id="scams">
  <h2>scam explainers</h2>
  <p>Short videos on the most common scams and what you can do about each.</p>
  <div class="bw-grid">{scams}</div>
  <p><a class="bw-more" href="../programs/#quiz">not sure which applies to you? take the scam-risk quiz</a></p>
</section>

<section class="bw-wrap" id="recordings">
  <h2>past event recordings</h2>
  {groups}
</section>

<section class="bw-band" id="find">
  <div class="bw-wrap">
    <h2>find videos for me</h2>
    <p>Pick what you work on and your role, and get a short list of recordings.</p>
    <iframe class="bw-embed" src="find-videos.html" title="Find videos for me" loading="lazy"></iframe>
  </div>
</section>"""
    page("education/index.html", "Education", "Short videos on scam risks, plus recordings of past Blockchain by Women panels.", main, "Education")
    write("education/find-videos.html", quiz_doc("tailor-learning/index.html"))


def upcoming_html():
    return "".join(f'<li><p class="bw-kicker">{esc(d)}</p><h3>{esc(t)}</h3><p>{esc(n)}</p></li>' for d, t, n in UPCOMING)


def build_events(recs):
    blocks = event_blocks()
    past = "".join(event_card(e, blocks, recs) for e in PAST)
    archive = "".join(event_card(e, blocks, recs) for e in ARCHIVE)
    main = f"""<section class="bw-wrap bw-pagehead">
  <h1>events</h1>
  <p class="bw-lead">Blockchain by Women events and events with our partners.</p>
  <p class="bw-jump"><a href="#upcoming">upcoming</a><a href="#past">past events</a><a href="#archive">2019 archive</a></p>
</section>

<section class="bw-band" id="upcoming">
  <div class="bw-wrap">
    <h2>upcoming</h2>
    <ul class="bw-upcoming">{upcoming_html()}</ul>
    <p><a href="mailto:{EMAIL}">Email us</a> for details as they are confirmed.</p>
  </div>
</section>

<section class="bw-wrap" id="past">
  <h2>past events</h2>
  {past}
</section>

<section class="bw-wrap" id="archive">
  <h2>2019 archive</h2>
  <details class="bw-archive"><summary>show our 2019 meetups ({len(ARCHIVE)})</summary>{archive}</details>
</section>"""
    page("events/index.html", "Events", "Blockchain by Women events and partner events, with links to recordings.", main, "Events")


def build_services():
    main = f"""<section class="bw-wrap bw-pagehead">
  <h1>programs</h1>
  <p class="bw-lead">Events, digital fraud detection, tracking and reporting, and loss prevention.</p>
  <p class="bw-jump"><a href="#events">events</a><a href="#detect">detect</a><a href="#track">track</a><a href="#report">report</a><a href="#prevent">prevent loss</a><a href="#quiz">scam-risk quiz</a></p>
</section>

<section class="bw-wrap bw-service" id="events">
  <p class="bw-kicker">01</p>
  <div>
    <h2>events</h2>
    <p>Curated discussions with leaders from the ecosystem on a particular use case or emerging topic. Work with like-minded people working towards safely developing AI and blockchain tech.</p>
    <p>Panels and briefings are online and in person, and most are recorded so you can catch up on the <a href="../education/#recordings">recordings</a>.</p>
    <p class="bw-actions"><a class="bw-btn" href="../events/">see upcoming events</a><a class="bw-btn bw-btn-line" href="mailto:{EMAIL}?subject=Speaking%20or%20partnering">speak or partner with us</a></p>
  </div>
</section>

<section class="bw-wrap bw-service" id="detect">
  <p class="bw-kicker">02</p>
  <div>
    <h2>detect</h2>
    <p>Detect scams and fraud before money moves.</p>
    <p>Learn how to safely use digital assets and how to evaluate the risk associated with them.</p>
    <p>Got an email, text, job offer or investment pitch you are not sure about?</p>
    <p class="bw-actions"><a class="bw-btn" href="#quiz">assess your scam risk</a></p>
  </div>
</section>

<section class="bw-wrap bw-service" id="track">
  <p class="bw-kicker">03</p>
  <div>
    <h2>track</h2>
    <p>Monitor ongoing digital fraud.</p>
    <p>Scams rarely stop at one message or one transfer. If you are being targeted, or funds have already moved, we help you keep watch on the wallet addresses, accounts and websites involved so that new activity is noticed while it can still be acted on, and so the record is complete when you report.</p>
    <p class="bw-actions"><a class="bw-btn" href="mailto:{EMAIL}?subject=Tracking%20ongoing%20fraud">email us about ongoing fraud</a></p>
  </div>
</section>

<section class="bw-wrap bw-service" id="report">
  <p class="bw-kicker">04</p>
  <div>
    <h2>report</h2>
    <p>Report to law enforcement, with the help of bAIW if needed. If you think you have been scammed, act quickly and keep the evidence.</p>
    <ul>
      <li><strong>Save</strong> wallet addresses, transaction IDs, dates and amounts, and screenshots of every message, profile and website involved.</li>
      <li><strong>Tell</strong> your bank, exchange or payment app straight away.</li>
      <li><strong>File</strong> a report with the FBI's Internet Crime Complaint Center at <a href="https://www.ic3.gov/">ic3.gov</a> and with the FTC at <a href="https://reportfraud.ftc.gov/">reportfraud.ftc.gov</a>.</li>
      <li><strong>Be careful</strong> with anyone who contacts you offering to recover lost funds for a fee. That is often a second scam.</li>
    </ul>
    <p>We investigate and assess potential fraud. If you are looking for help, email us at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    <p class="bw-actions"><a class="bw-btn" href="mailto:{EMAIL}?subject=Help%20with%20a%20possible%20scam">email us for help</a></p>
  </div>
</section>

<section class="bw-wrap bw-service" id="prevent">
  <p class="bw-kicker">05</p>
  <div>
    <h2>prevent loss</h2>
    <p>We use AI to find the gaps between what happened and what was recorded, and hand the evidence to a person.</p>
    <h3>Loss prevention, built safely</h3>
    <p>Most loss is not a dramatic theft. It is a small gap between what happened and what was recorded. Those gaps hide in plain sight because nobody has time to check every record against reality.</p>
    <p>This is our applied security work: AI that compares what was seen with what the system of record says, and surfaces the differences for a person to verify.</p>
    <p>We built it the way we inform: transparent about what it checks and careful with data. No one is identified. Results are verified.</p>
    <p class="bw-actions"><a class="bw-btn" href="mailto:{EMAIL}?subject=Loss%20prevention">email us about your loss prevention need</a></p>
  </div>
</section>

<section class="bw-band" id="quiz">
  <div class="bw-wrap">
    <h2>assess your scam risk</h2>
    <p>Two questions. You get the videos that match what you are most likely to face.</p>
    <iframe class="bw-embed" src="scam-quiz.html" title="Assess your scam risk" loading="lazy"></iframe>
  </div>
</section>"""
    page("programs/index.html", "Programs", "Events, digital fraud detection, tracking and reporting, and loss prevention from bAIW.", main, "Programs")
    write("programs/scam-quiz.html", quiz_doc("assessment/index.html"))


OLD_LINKS = [
    ("assessment/", "programs/#quiz"), ("tailor-learning/", "education/#find"), ("recordings/", "education/#recordings"),
    ("membership/", "events/"), ("connect/", "about-1/#connect"), ("new-page-1/", "about-1/#connect"), ("new-page-26/", "donate/"),
]


def reshell(path, active):
    """About and Join keep their content; only the header, mobile menu and footer are replaced."""
    s = old(path)
    s = re.sub(r'<div id="sidecarNav">.*?(?=<div id="siteWrapper")', "", s, flags=re.S)
    s = re.sub(r"<header id=\"header\".*?</header>", lambda m: header("../", active), s, flags=re.S)
    s = re.sub(r"<footer id=\"footer\".*?</footer>", lambda m: footer("../"), s, flags=re.S)
    s = re.sub(r'<link rel="icon"[^>]*>', "", s)
    s = s.replace("</head>", HEAD_LINKS.format(rel="../") + "\n</head>")
    s = s.replace('<script src="../assets/site.js" defer></script>', '<script src="../assets/site.js" defer></script>\n<script src="../assets/baiw.js" defer></script>')
    s = s.replace("<body ", '<body data-bw-old ', 1)
    s = re.sub(r"<title>(.*?) &mdash; Blockchain by Women</title>", r"<title>\1 — blockchAIn by women</title>", s)
    for a, b in OLD_LINKS:
        s = s.replace(f'href="../{a}"', f'href="../{b}"')
    assert "bw-header" in s and "bw-footer" in s and "baiw.js" in s, path
    write(path, s)


ABOUT_HTML = """<section class="bw-wrap bw-pagehead">
  <h1>about</h1>
  <p class="bw-lead">bAIW (Blockchain and AI by Women) helps consumers understand how to protect themselves and their assets, and helps builders create systems people can trust.</p>
</section>

<section class="bw-wrap bw-prose">
  <p>We started as Blockchain by Women, created to raise awareness, educate and connect people in a fast-growing space. As blockchain matured, awareness was no longer enough. People needed practical ways to stay safe, and the teams shipping products needed to build them securely. AI now raises the same questions of security, risk and trust, and we bring the same approach to it.</p>
  <p>We are a community for everyone that leads and empowers, including:</p>
  <ul>
    <li>Helping consumers understand the risks and how to protect themselves and their assets</li>
    <li>Educating on AI agent integrity and trust in systems built using AI</li>
    <li>Providing technology-based loss prevention services</li>
    <li>Investigating and assessing potential fraud</li>
    <li>Showcasing the work and expertise of builders through curated panels, online and in person</li>
  </ul>
</section>

<section class="bw-wrap bw-bio" id="karen-hsu">
  <img src="../assets/img/karen-hsu-headshot.jpg" alt="Karen Hsu" width="500" height="500" loading="lazy">
  <div>
    <h2>Karen Hsu</h2>
    <p class="bw-kicker">Founder, bAIW</p>
    <p>With 30 years in technology companies, Karen is co-inventor of 5 patents and for over 25 years has built and taken to market software for financial institutions and fintechs to better manage and serve their customers. She worked with financial standards organizations including SWIFT and ACORD to create global standards for exchanging data on financial transactions among financial institutions, companies, agents and other stakeholders.</p>
    <p>Karen co-founded BlockchainIntel to prevent fraud in blockchain, ACH and credit card transactions and transitioned the company to become part of Appdome to expand the mission of protecting everyone using mobile apps. At Appdome, Karen led go-to-market teams protecting against AI-driven fraud, and worked with DevOps vendors and with fintechs that process trillions of dollars in payments annually to secure their mobile apps.</p>
    <p>Karen started Blocksteer to protect against AI-driven fraud and ensure the integrity of AI infrastructure.</p>
    <p>She partners with law enforcement agencies around the world such as the FBI to identify and stop bad actors who have stolen digital assets from individuals. Partnering with professional organizations such as ACAMS, she has shared the work she and her teams have done so they can better combat money laundering and terrorist financing.</p>
    <p>Karen co-founded and has been on the advisory board of BASES (Business Association for Stanford Entrepreneurial Students), one of the largest student-run organizations, which hosts an annual business plan contest, educational series and workshops for students. BASES students and alumni have founded fintechs and other companies.</p>
    <p>Karen co-founded Blockchain by Women, now bAIW, to help consumers protect themselves and help everyone build safely in blockchain and AI. She has since extended bAIW to provide technology-based loss prevention services, with education focused on AI agent integrity and trust in systems built using AI.</p>
    <p><a class="bw-more" href="https://www.linkedin.com/in/karen-hsu/">Karen on LinkedIn</a></p>
  </div>
</section>
"""


def build_about():
    page("about-1/index.html", "About", "bAIW (Blockchain and AI by Women) helps consumers protect themselves and their assets, and helps builders create systems people can trust.", ABOUT_HTML, "About")


JOIN_HTML = """<section class="bw-wrap bw-pagehead">
  <h1>join</h1>
  <p class="bw-lead">Unlock Exclusive Content and Join a Supportive Community</p>
</section>

<section class="bw-wrap bw-prose">
  <p>By joining, you'll gain access to:</p>
  <ul>
    <li><strong>Risk assessments and recommendations:</strong> <a href="../programs/#quiz">Assess your personal risk</a> and learn how to protect yourself. Assess the risk in the blockchain and AI applications you use and learn what you can do.</li>
    <li><strong>Expert insights:</strong> Learn from leading figures through interviews, webinars and exclusive Q&amp;A sessions on the latest in blockchain and AI, from new projects to AI agent integrity and AI-driven fraud.</li>
    <li><strong>Collaborative community:</strong> Network with others building and using blockchain and AI, exchange ideas, forge partnerships and build lasting connections.</li>
  </ul>
  <p>More than just a membership, we are building a vibrant ecosystem where people can:</p>
  <ul>
    <li><strong>Protect themselves:</strong> Gain the knowledge and confidence to use blockchain and AI safely.</li>
    <li><strong>Decide with confidence:</strong> Evaluate projects, tools and opportunities with the collective knowledge of industry veterans and experts.</li>
    <li><strong>Shape the future:</strong> Be a driving force in making blockchain and AI safer and more trustworthy.</li>
  </ul>
  <p>Join us and become part of a movement:</p>
  <ul>
    <li>Empowering people to lead in blockchain and AI.</li>
    <li>Creating a safer, more inclusive and equitable future for all.</li>
    <li>Investing in yourself and your future.</li>
  </ul>
  <p class="bw-actions"><a class="bw-btn" href="{join_url}"{join_target}>join today</a></p>
</section>

<section class="bw-wrap bw-donate" id="donate">
  <div>
    <h2>donate</h2>
    <p>Blockchain by Women is a 501(c)(3) not-for-profit organization, EIN 83-1984602. Charitable gifts are <strong>tax deductible</strong> contributions. Upon donation, either in crypto or through PayPal, you will receive a thank-you letter for your tax purposes.</p>
    <p class="bw-actions"><a class="bw-btn" href="https://www.paypal.com/donate/?hosted_button_id=B5D8ZJTSUYV3J" target="_blank" rel="noopener">donate through paypal</a></p>
  </div>
  <figure>
    <img src="../assets/img/e11327b0-ETH_QR_code_BCBW_donation.png" alt="QR code for the Blockchain by Women ETH donation address" width="235" height="235" loading="lazy">
    <figcaption>Donate in ETH</figcaption>
  </figure>
</section>
"""


def build_join():
    url = JOIN_FORM_URL or f"mailto:{EMAIL}?subject=Join%20bAIW&body=Name:%0AEmail:%0AWhy%20I%20am%20joining:%0A"
    target = ' target="_blank" rel="noopener"' if JOIN_FORM_URL else ""
    page("donate/index.html", "Join", "Join bAIW: risk assessments, expert insights and a community building and using blockchain and AI safely. Donations are tax deductible.",
         JOIN_HTML.replace("{join_url}", url).replace("{join_target}", target), "Join")


def assets():
    brand = os.path.join(SITE, "assets", "brand")
    os.makedirs(brand, exist_ok=True)
    for f in ("baiw-wordmark-reverse.svg", "baiw-wordmark-color.svg", "baiw-mark-reverse.svg", "baiw-icon-ink.svg"):
        shutil.copy(os.path.join(ROOT, "brand", "logo", "svg", f), brand)
    shutil.copy(os.path.join(ROOT, "brand", "logo", "png", "baiw-icon-ink-1024.png"), brand)


if __name__ == "__main__":
    recs = recordings()
    assets()
    build_home(recs)
    build_education(recs)
    build_events(recs)
    build_services()
    build_about()
    build_join()
    redirect("recordings/index.html", "education/#recordings", "Education")
    redirect("tailor-learning/index.html", "education/#find", "Education")
    redirect("membership/index.html", "events/", "Events")
    redirect("assessment/index.html", "programs/#quiz", "Programs")
    redirect("services/index.html", "programs/", "Programs")
    redirect("connect/index.html", "about-1/#connect", "About")
    redirect("new-page-1/index.html", "about-1/#connect", "About")
    redirect("new-page-26/index.html", "donate/", "Join")
