# orku-web

Landing page for orku: the logo centred on a sand background. Plain HTML with inline CSS, no build step.

## Local preview

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.


Hosted on GitHub Pages from `main` (repo root). The `CNAME` file sets the custom domain `orku.ai`, and `.nojekyll` tells Pages to serve the files as they are, without running its Jekyll site builder. Every push to `main` goes live within a minute or two.
