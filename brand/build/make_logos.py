"""Build the Blockchain by Women (bAIw) logo set as outlined SVGs.

Run:  uv run --with fonttools --with uharfbuzz python make_logos.py
Type is Jost (SIL OFL), converted to outlines so the files need no font.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "logo", "svg")
os.makedirs(OUT, exist_ok=True)

INK, PAPER, SIGNAL, SIGNAL_ON_DARK = "#141414", "#ffffff", "#9163ff", "#9163ff"

W_MAIN, W_AI, W_SUB = 500, 700, 300   # blockch·n / AI / by women
GAP = 55                              # space between the brackets and neighbours
TRACK = 12                            # letter-spacing, font units
MARGIN = 150                          # clear space built into every file

_fonts = {}


def font(weight):
    if weight not in _fonts:
        tt = TTFont(os.path.join(HERE, "Jost-var.ttf"))
        inst = instancer.instantiateVariableFont(tt, {"wght": weight}, overlap=instancer.OverlapMode.REMOVE)
        path = os.path.join(HERE, f"Jost-{weight}.ttf")
        inst.save(path)
        blob = hb.Blob.from_file_path(path)
        _fonts[weight] = (TTFont(path), hb.Font(hb.Face(blob)))
    return _fonts[weight]


def run(text, weight, x0, track=TRACK):
    """Shape text; return (svg path data, end x). y is flipped: baseline at y=0."""
    tt, hbf = font(weight)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": False})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    x = x0
    d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        gs[order[info.codepoint]].draw(TransformPen(pen, (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)))
        d.append(pen.getCommands())
        x += pos.x_advance + track
    return "".join(d), x - track


CAP = font(W_AI)[0]["OS/2"].sCapHeight
TOP, BOT = -(CAP + 120), 190          # vertical extent of the brackets


def bracketed(x0):
    """The highlighted [AI]: brackets at the main weight, AI in bold. Returns (path, end x)."""
    d1, x = run("[", W_MAIN, x0)
    d2, x = run("AI", W_AI, x + 28, track=30)
    d3, x = run("]", W_MAIN, x + 28)
    return d1 + d2 + d3, x


def compose(before, after, sub=None, stacked=False, tagline=None):
    """Lay out  before [AI] after  (+ optional lighter `sub`). Returns parts + bbox."""
    parts = {"ink": "", "sub": ""}
    x = 0
    if before:
        d, x = run(before, W_MAIN, 0)
        parts["ink"] += d
        x += GAP
    ai, x = bracketed(x)
    if after:
        d, x = run(after, W_MAIN, x + GAP)
        parts["ink"] += d
    width, bottom = x, BOT
    if sub and not stacked:
        d, x = run(sub, W_SUB, x + 270)
        parts["sub"] = d
        width, bottom = x, max(BOT, 230)
    elif sub:
        # second line, scaled to the width of the first
        d, w = run(sub, W_SUB, 0, track=60)
        s = width / w
        y = BOT + 150 + CAP * s
        parts["sub"] = f'<g transform="translate(0 {y:.1f}) scale({s:.4f})"><path d="{d}"/></g>'
        bottom = y + 230 * s
    if tagline:
        d, w = run(tagline, 400, 0, track=45)
        s = width / w
        y = bottom + 190 + CAP * s
        parts["sub"] = f'<path d="{parts["sub"]}"/><g transform="translate(0 {y:.1f}) scale({s:.4f})"><path d="{d}"/></g>'
        parts["sub"] = "<g>" + parts["sub"] + "</g>"
        bottom = y + 230 * s
    return parts, ai, (0, TOP, width, bottom - TOP)


def svg(name, title, layout, mode, bg=None, square=False, margin=MARGIN):
    parts, ai, (bx, by, bw, bh) = layout
    vx, vy, vw, vh = bx - margin, by - margin, bw + 2 * margin, bh + 2 * margin
    if square:
        side = max(vw, vh)
        vx, vy, vw, vh = vx - (side - vw) / 2, vy - (side - vh) / 2, side, side
    text = {"color": INK, "reverse": PAPER, "black": INK, "white": PAPER}[mode]
    hi = {"color": SIGNAL, "reverse": SIGNAL_ON_DARK, "black": INK, "white": PAPER}[mode]
    body = []
    if bg:
        body.append(f'<rect x="{vx:.1f}" y="{vy:.1f}" width="{vw:.1f}" height="{vh:.1f}" fill="{bg}"/>')
    sub = parts["sub"]
    sub = sub if sub.startswith("<g") else (f'<path d="{sub}"/>' if sub else "")
    body.append(f'<g fill="{text}"><path d="{parts["ink"]}"/>{sub}</g>')
    body.append(f'<path fill="{hi}" d="{ai}"/>')
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" '
           f'width="{vw / 4:.0f}" height="{vh / 4:.0f}" role="img" aria-label="{title}">'
           f'<title>{title}</title>{"".join(body)}</svg>\n')
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(out)
    print(f"{name}.svg  {vw / vh:.2f}:1  {len(out)}")


mark = compose("b", "w")
word = compose("blockch", "n", sub="by women")
stack = compose("blockch", "n", sub="by women", stacked=True)

for mode in ("color", "reverse", "black", "white"):
    svg(f"baiw-mark-{mode}", "bAIw", mark, mode)
    svg(f"baiw-wordmark-{mode}", "blockchAIn by women", word, mode)
    svg(f"baiw-stacked-{mode}", "blockchAIn by women", stack, mode)

TAGLINE = "Building and Using Blockchain and AI Safely"
tag = compose("blockch", "n", sub="by women", tagline=TAGLINE)
for mode in ("color", "reverse"):
    svg(f"baiw-tagline-{mode}", "blockchAIn by women. " + TAGLINE, tag, mode)

# app icon / avatar / favicon: square, full-bleed ground
svg("baiw-icon-ink", "bAIw", mark, "reverse", bg=INK, square=True, margin=270)
svg("baiw-icon-paper", "bAIw", mark, "color", bg=PAPER, square=True, margin=270)
