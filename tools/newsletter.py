#!/usr/bin/env python3
"""Draft the monthly bAIW newsletter from the site's own data.

Run from the repo root:  python3 tools/newsletter.py [YYYY-MM]
Writes newsletter/YYYY-MM.txt and newsletter/YYYY-MM.html. Sending is a manual Gmail step: see JOIN_FORM.md.
Upcoming events come from UPCOMING in tools/reorg.py; the featured recording from NEW_RECORDINGS.
"""
import datetime as dt
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reorg  # noqa: E402  (data lists only; the site build runs under __main__)

SITE = "https://blockchainbywomen.com"
POSTAL = "[postal address]"          # required on bulk email (CAN-SPAM); fill in once
month = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().strftime("%Y-%m")
label = dt.datetime.strptime(month, "%Y-%m").strftime("%B %Y")

events = reorg.UPCOMING
recs = list(reorg.NEW_RECORDINGS.items())
latest = recs[-1] if recs else None

subject = f"bAIW in {label}: " + (events[0][1] if events else "upcoming events and what is new")
opener = ("Hello from blockchAIn by women. Once a month we send the events coming up and what is new on the "
          "site, so you can build and use blockchain and AI safely.")

# ---- plain text
lines = [subject, "", opener, "", "Upcoming events"]
for d, t, n in events:
    lines.append(f"- {d}: {t}" + (f" ({n})" if n else ""))
lines.append(f"  Details and registration: {SITE}/events/")
if latest:
    yt, (title, _) = latest
    lines += ["", "New on the site", f"- Recording: {title}  https://youtu.be/{yt}", f"- Programs: {SITE}/programs/"]
lines += ["", f"Website: {SITE}", f"Reply to this email with questions, or write to {reorg.EMAIL}.", "",
          "Blockchain by Women (bAIW) is a 501(c)(3) not-for-profit, EIN 83-1984602. " + POSTAL,
          "You are receiving this because you joined bAIW. Reply with 'unsubscribe' to stop receiving it."]
text = "\n".join(lines)

# ---- html (inline styles only, so Gmail keeps them)
P = 'style="margin:0 0 16px;font:17px/1.6 Jost,Futura,\'Century Gothic\',Arial,sans-serif;color:#141414"'
H = 'style="margin:32px 0 12px;font:500 24px/1.2 Jost,Futura,\'Century Gothic\',Arial,sans-serif;color:#141414;text-transform:lowercase"'
A = 'style="color:#7848e8"'
ev = "".join(f'<li {P}><strong>{html.escape(d)}</strong> · {html.escape(t)}' + (f'<br><span style="color:#5a5a5a">{html.escape(n)}</span>' if n else "") + '</li>' for d, t, n in events)
rec = ""
if latest:
    yt, (title, _) = latest
    rec = f'''<h2 {H}>new on the site</h2>
<p {P}><a {A} href="https://youtu.be/{yt}">{html.escape(title)}</a> (recording)<br>
<a {A} href="{SITE}/programs/">Our programs</a>: events, detect, track, report and prevent loss.</p>'''
doc = f'''<!doctype html><html><body style="margin:0;padding:24px;background:#ffffff">
<div style="max-width:600px;margin:0 auto">
<p style="margin:0 0 24px;font:500 28px/1.1 Jost,Futura,'Century Gothic',Arial,sans-serif;color:#141414">blockch<span style="color:#9163ff">[<b>AI</b>]</span>n by women</p>
<p {P}>{html.escape(opener)}</p>
<h2 {H}>upcoming events</h2>
<ul style="padding-left:20px;margin:0">{ev}</ul>
<p {P}><a {A} href="{SITE}/events/">Details and registration</a></p>
{rec}
<p {P}><a {A} href="{SITE}">{SITE.replace("https://", "")}</a> · reply to this email with questions, or write to <a {A} href="mailto:{reorg.EMAIL}">{reorg.EMAIL}</a>.</p>
<hr style="border:0;border-top:1px solid #d9d9d9;margin:32px 0 16px">
<p style="margin:0;font:13px/1.5 Jost,Futura,'Century Gothic',Arial,sans-serif;color:#5a5a5a">Blockchain by Women (bAIW) is a 501(c)(3) not-for-profit, EIN 83-1984602. {html.escape(POSTAL)}<br>
You are receiving this because you joined bAIW. Reply with "unsubscribe" to stop receiving it.</p>
</div></body></html>'''

os.makedirs("newsletter", exist_ok=True)
for ext, body in (("txt", text), ("html", doc)):
    with open(f"newsletter/{month}.{ext}", "w", encoding="utf-8") as f:
        f.write(body)
print(f"subject: {subject}\nwrote newsletter/{month}.txt and newsletter/{month}.html")
