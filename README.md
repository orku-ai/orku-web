# orku-web

Landing page for orku: the logo centred on a sand background. Plain HTML with inline CSS, no build step.

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Hosting

Hosted on GitHub Pages from `main` (repo root). The `CNAME` file sets the custom domain `orku.ai`, and `.nojekyll` tells Pages to serve the files as they are, without running its Jekyll site builder. Every push to `main` goes live within a minute or two.

## Background contour lines

`topo.svg` (the faint lines) and `topo-glow.svg` (the same lines in warm orange, shown around the pointer) are generated, not drawn. To make a different landscape, change `SEED` (or the other settings at the top) in `tools/make-topo.py`, then run:

```bash
python3 tools/make-topo.py
```

## Link preview image

`og-image.png` (1200 × 630) is a screenshot of the page, used for link previews in Slack, iMessage, LinkedIn and others. To regenerate it after a design change, start the local preview, then run:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --window-size=800,420 --force-device-scale-factor=1.5 --virtual-time-budget=3000 --screenshot="$PWD/og-image.png" http://localhost:8000/
```
