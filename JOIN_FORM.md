# Join form and monthly newsletter

## The join form (done 2026-11-11)

The "join today" button on /donate/ opens Karen's Google Form
(`JOIN_FORM_URL` at the top of `tools/reorg.py`):
https://docs.google.com/forms/d/e/1FAIpQLSdrRIKoa96bWPIbpA5pLjKxndTlqwZeYOyyrrdgHL0gI5GufQ/viewform

It asks for name, email, why they are joining, and consent to the monthly summary. Responses go to
the Google Sheet the form is linked to, which already holds everyone who asked to subscribe. That
sheet is the newsletter list.

Settings worth checking once in the Form editor (Settings -> Responses / Presentation):
- Confirmation message: "Thank you for joining bAIW. You will hear from us once a month with
  upcoming events and what is new on blockchainbywomen.com."
- "Send responders a copy of their response" = Always, if you want each person to get a thank-you
  email automatically. (Needs "Collect email addresses" = Responder input.)
- "Limit to 1 response" = off, so nobody has to sign in to Google.

## Sending the monthly newsletter (manual, about 10 minutes)

1. Add any new event to `UPCOMING` in `tools/reorg.py` (and rebuild the site).
2. `cd ~/blockchainbywomen && python3 tools/newsletter.py` writes `newsletter/YYYY-MM.html`
   and `.txt` for the current month (or pass `2026-12`). Open the .html in a browser, read it once.
   First time: put the postal address in `POSTAL` in `tools/newsletter.py` (bulk email must carry one).
3. In the members sheet, copy the email column for rows where the newsletter box is ticked.
4. Gmail -> Compose -> paste the addresses into **Bcc** (never To or Cc), subject from the draft's
   first line, select-all + copy the opened .html page and paste it into the body (Gmail keeps
   the formatting), send. Gmail allows about 500 recipients a day.
5. Anyone who replies "unsubscribe": delete their row from the sheet.

When the list passes a few hundred people, move to Mailchimp or Buttondown: both import the sheet,
handle unsubscribes, and the same draft pastes in.
