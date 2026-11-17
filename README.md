# Blog

Static blog. Essays live in `posts/*.md`; `python build.py` renders them into `docs/`, which GitHub Pages serves as-is. No dependencies beyond Python 3.8+.

## Write a post

Add `posts/21-my-slug.md`:

```
---
title: My title
summary: One sentence for the index and meta description.
tags: inference, verification
---

Paragraphs...
```

The number prefix sets the order and the `No.` label; the rest of the filename is the URL slug.

## Build and preview

```
python build.py
python -m http.server -d docs 8000
```

## Publish on GitHub Pages

1. Push this folder to a GitHub repo (e.g. `roro2006/blog`), including `docs/`.
2. Repo Settings → Pages → Source: "Deploy from a branch", Branch: `main`, folder `/docs`.
3. The site appears at `https://roro2006.github.io/<repo>/`. Rebuild and push to update.

All links are relative, so the site works at any path. Edit the site title and author in the `SITE` dict at the top of `build.py`.
