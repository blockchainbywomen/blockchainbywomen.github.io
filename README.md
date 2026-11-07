# blockchainbywomen.com

Static copy of the Blockchain by Women website, served by GitHub Pages at https://blockchainbywomen.com.

## Layout

- `site/` — the published website. Every page is a folder with an `index.html` (for example `site/about-1/index.html` is https://blockchainbywomen.com/about-1/). Images live in `site/assets/img/`, styles in `site/assets/`.
- `raw/` — the original pages as downloaded from Squarespace on 2026-11-06, kept for reference.
- `tools/capture.py` and `tools/clean.py` — the scripts that produced `site/` from `raw/`. They are only needed if you want to rebuild from the Squarespace snapshot.

## Editing the site

1. Edit the HTML file for the page in `site/` (any text editor works; search for the text you want to change).
2. Commit and push to the `main` branch. The GitHub Actions workflow in `.github/workflows/pages.yml` publishes the `site/` folder automatically within a minute or two.

To preview locally before pushing:

```
python3 -m http.server 8080 --directory site
```

then open http://localhost:8080 in a browser.

## Differences from the Squarespace site

- The contact form on **Connect** and **Let's stay connected** is now an email link to blockchainbywomen@gmail.com.
- The newsletter sign-up boxes were removed (they posted to Squarespace's mailing list).
- Fonts: Adobe Typekit fonts were replaced with Google Fonts look-alikes (Jost for Futura, Montserrat for Proxima Nova, Nunito Sans for Europa).
- The **Videos** page shows a grid of click-to-play YouTube thumbnails instead of the Squarespace slideshow.
