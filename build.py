"""Build the blog into docs/ for GitHub Pages.

Usage:  python build.py
No dependencies. Posts live in posts/*.md with a small front-matter block:

    ---
    title: Post title
    summary: One sentence.
    tags: inference, verification
    date: 2026-11-17        (optional; defaults to SITE["date"])
    ---
"""
import html
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
POSTS = ROOT / "posts"
OUT = ROOT / "docs"
STATIC = ROOT / "static"

SITE = {
    "title": "All will be Rohan",
    "author": "Rohan Reddy",
    "tagline": "Notes from the Hunter Maze",
    "github": "https://github.com/roro2006",
    "date": "2026-11-17",
}


def display_date(value):
    """Format ISO front-matter dates consistently across the site."""
    return date.fromisoformat(value).strftime("%b %d, %Y").replace(" 0", " ")


# ---------- tiny markdown ----------

def inline(text):
    codes = []

    def stash(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)

    def estimate(m):  # {{est: ...}} marks a placeholder guess; build() refuses to publish a post with any left
        codes.append('<span class="est" title="Estimate: replace before publishing">' + html.escape(m.group(1)) + "</span>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"\{\{est:\s*(.*?)\}\}", estimate, text)
    text = html.escape(text, quote=False)
    def link(m):
        codes.append(f'<a href="{m.group(2)}">{m.group(1)}</a>')
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"(https?://[^\s<]+[^\s<.,;:)])", r'<a href="\1">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def chart(block):
    """Render a ```chart block as an inline horizontal bar chart (SVG).

    title: Chart title
    unit: x            (optional suffix for values)
    source: Who reported it
    Label one: 2.5
    Label two: 3.1
    """
    meta, rows = {}, []
    for line in block:
        if ":" not in line:
            continue
        head, rest = line.split(":", 1)
        if head.strip().lower() in ("title", "unit", "source", "note"):
            meta[head.strip().lower()] = rest.strip()
            continue
        k, v = line.rsplit(":", 1)
        k, v = k.strip(), v.strip()
        try:
            rows.append((k, float(v.replace(",", ""))))
        except ValueError:
            meta[k.lower()] = v
    if not rows:
        return ""
    unit = meta.get("unit", "")
    if unit[:1].isalpha() and len(unit) > 1:
        unit = " " + unit  # "5,272 recordings", but "2.5x" and "40%"
    vmax = max(0, max(v for _, v in rows))
    vmin = min(0, min(v for _, v in rows))
    span = (vmax - vmin) or 1
    label_w, bar_w, row_h, w = 230, 280, 34, 640
    zero = label_w + bar_w * (-vmin) / span
    h = row_h * len(rows) + 8
    parts = []
    for n, (label, v) in enumerate(rows):
        y = n * row_h + 4
        bw = max(2, bar_w * abs(v) / span)
        x = zero if v >= 0 else zero - bw
        shown = (f"{v:,.0f}" if v == int(v) and abs(v) >= 100 else f"{v:g}") + unit
        if v > 0 and not vmin:
            shown = shown
        elif v > 0:
            shown = "+" + shown
        tx = zero + bw + 8 if v >= 0 else zero + 8
        cls = "cb" if v >= 0 else "cb neg"
        parts.append(
            f'<text x="{label_w - 10}" y="{y + 20}" text-anchor="end" class="cl">{html.escape(label)}</text>'
            f'<rect x="{x:.1f}" y="{y + 6}" width="{bw:.1f}" height="20" rx="3" class="{cls}"/>'
            f'<text x="{tx:.1f}" y="{y + 20}" class="cv">{html.escape(shown)}</text>')
    if vmin < 0:
        parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="2" y2="{h - 2}" class="axis"/>')
    svg = (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(meta.get("title", "chart"))}">'
           + "".join(parts) + "</svg>")
    cap = f'<figcaption><strong>{inline(meta.get("title", ""))}</strong>'
    if meta.get("note"):
        cap += f' {inline(meta["note"])}'
    if meta.get("source"):
        cap += f'<span class="src">Source: {inline(meta["source"])}</span>'
    return f'<figure class="chart">{svg}{cap}</figcaption></figure>'


ARROW_DEFS = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
              'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>')


def _meta_and_rest(block, stop):
    meta, rest = {}, []
    for n, line in enumerate(block):
        if line.lstrip().startswith(stop):
            rest = block[n:]
            break
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta, "\n".join(rest)


def _caption(meta):
    cap = ""
    if meta.get("title"):
        cap += f'<strong>{inline(meta["title"])}</strong> '
    if meta.get("caption"):
        cap += inline(meta["caption"])
    if meta.get("source"):
        cap += f'<span class="src">Source: {inline(meta["source"])}</span>'
    return f"<figcaption>{cap}</figcaption>" if cap else ""


def diagram(block):
    """```diagram block: title/caption/source lines, then an inline <svg>.

    Style hooks (see style.css): .box .box.hi .box.good .box.bad .lbl .sub .edge .edge.flow
    .edge.bad .pulse .dim; marker-end="url(#arr)" draws an arrowhead.
    """
    meta, svg = _meta_and_rest(block, "<svg")
    svg = re.sub(r"<script.*?</script>", "", svg, flags=re.S | re.I)
    svg = re.sub(r"\son\w+=\"[^\"]*\"", "", svg)
    svg = re.sub(r"<svg\b", '<svg role="img" aria-label="' + html.escape(meta.get("title", "diagram")) + '"', svg, count=1)
    if "url(#arr)" in svg and "<defs>" not in svg:
        svg = re.sub(r"(<svg[^>]*>)", r"\1" + ARROW_DEFS, svg, count=1)
    cls = "diagram manim" if meta.get("style", "").lower() == "manim" else "diagram"
    return f'<figure class="{cls}">{svg}{_caption(meta)}</figure>'


def image(block):
    """```image block: src: file in static/img, alt:, title:, caption:, source:"""
    meta, _ = _meta_and_rest(block, "\x00")
    src = meta.get("src", "")
    if not re.fullmatch(r"[\w.-]+\.(jpg|jpeg|png|webp)", src):
        return ""
    alt = html.escape(meta.get("alt", meta.get("title", "")))
    return (f'<figure class="image"><img src="../img/{src}" alt="{alt}" loading="lazy" decoding="async">'
            f'{_caption(meta)}</figure>')


def video(block):
    """```video block: youtube: ID, start: seconds (optional), title:, caption:"""
    meta, _ = _meta_and_rest(block, "\x00")
    vid = meta.get("youtube", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
        return ""
    start = meta.get("start", "")
    query = f"?start={int(start)}" if start.isdigit() else ""
    title = html.escape(meta.get("title", "Video"))
    frame = (f'<div class="vwrap"><iframe src="https://www.youtube-nocookie.com/embed/{vid}{query}" title="{title}" '
             'loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" '
             'allowfullscreen></iframe></div>')
    return f'<figure class="video">{frame}{_caption(meta)}</figure>'


def markdown(src):
    out, para, lines = [], [], src.replace("\r\n", "\n").split("\n")
    i = 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            lang = line[3:].strip()
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            if lang == "chart":
                out.append(chart(block))
            elif lang == "diagram":
                out.append(diagram(block))
            elif lang == "video":
                out.append(video(block))
            elif lang == "image":
                out.append(image(block))
            else:
                out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
        elif re.match(r"(\d+\.|[-*])\s+", line):
            flush()
            ordered = bool(re.match(r"\d+\.", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"(\d+\.|[-*])\s+", lines[i]):
                items.append(re.sub(r"^(\d+\.|[-*])\s+", "", lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue
        elif m := re.match(r"(#{2,4})\s+(.*)", line):
            flush()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
        elif line.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> "))
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
            continue
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out)


def parse(path):
    raw = path.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---"):
        _, head, body = raw.split("---", 2)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    slug = re.sub(r"^\d+-", "", path.stem)
    words = len(re.findall(r"\w+", body))
    return {
        "slug": slug,
        "num": int(m.group(1)) if (m := re.match(r"(\d+)", path.stem)) else 0,
        "title": meta.get("title", slug),
        "summary": meta.get("summary", ""),
        "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "date": meta.get("date", SITE["date"]),
        "kind": meta.get("kind", "").strip().lower(),
        "draft": meta.get("draft", "").strip().lower() == "true",
        "estimates": len(re.findall(r"\{\{est:", body)),
        "minutes": max(1, round(words / 230)),
        "html": markdown(body.strip()),
    }


# ---------- templates ----------

# Manim-style figures start hidden only when this script runs, then draw in once on screen.
MANIM_JS = """<script>
(function () {
  var figs = document.querySelectorAll('figure.manim');
  if (!figs.length) return;
  document.documentElement.classList.add('mjs');
  if (!('IntersectionObserver' in window)) { figs.forEach(function (f) { f.classList.add('play'); }); return; }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('play'); io.unobserve(e.target); } });
  }, { threshold: 0.35 });
  figs.forEach(function (f) { io.observe(f); });
})();
</script>"""

def page(title, body, depth=0, description=""):
    up = "../" * depth
    desc = html.escape(description or SITE["tagline"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{up}style.css?v=manim-1">
</head>
<body>
<header class="site">
  <a class="name" href="{up}index.html">{SITE["title"]}</a>
  <nav><a href="{up}index.html">Essays</a><a href="{up}about.html">About</a><a href="{SITE["github"]}">GitHub</a></nav>
</header>
<main>
{body}
</main>
<footer class="site">
  <span>{SITE["author"]} · <a href="{SITE["github"]}">github.com/roro2006</a></span>
</footer>
{MANIM_JS}
</body>
</html>
"""


def kind_label(p):
    return f'<span class="kind">{html.escape(p["kind"])}</span> · ' if p["kind"] else ""


def tag_list(tags):
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)


def build():
    # Posts with "draft: true" are left out of docs/ (the published site). "python build.py --drafts"
    # builds everything into preview/ instead, which is git-ignored, so a draft can't go live by accident.
    global OUT
    drafts = "--drafts" in sys.argv
    if drafts:
        OUT = ROOT / "preview"
    OUT.mkdir(exist_ok=True)
    # Empty in place: a preview server or shell may hold these folders open.
    for f in sorted(OUT.rglob("*"), reverse=True):
        if f.is_file():
            f.unlink()
        else:
            shutil.rmtree(f, ignore_errors=True)
    (OUT / "posts").mkdir(exist_ok=True)
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    if (STATIC / "img").is_dir():
        shutil.copytree(STATIC / "img", OUT / "img", dirs_exist_ok=True)
    (OUT / ".nojekyll").write_text("")

    posts = sorted((parse(p) for p in POSTS.glob("*.md")), key=lambda p: p["date"], reverse=True)
    if not drafts:
        posts = [p for p in posts if not p["draft"]]
        unfinished = [f'{p["slug"]} ({p["estimates"]} estimates)' for p in posts if p["estimates"]]
        if unfinished:
            raise SystemExit("Refusing to publish posts with {{est: ...}} placeholders left: " + ", ".join(unfinished))
    all_tags = sorted({t for p in posts for t in p["tags"]})

    for idx, p in enumerate(posts):
        prev_p = posts[idx - 1] if idx > 0 else None
        next_p = posts[idx + 1] if idx + 1 < len(posts) else None
        pager = '<nav class="pager">'
        pager += f'<a href="{prev_p["slug"]}.html">← {html.escape(prev_p["title"])}</a>' if prev_p else "<span></span>"
        pager += f'<a href="{next_p["slug"]}.html">{html.escape(next_p["title"])} →</a>' if next_p else "<span></span>"
        pager += "</nav>"
        body = f"""<article>
<p class="meta">No. {p["num"]:02d} · {display_date(p["date"])} · {kind_label(p)}{p["minutes"]} min read · {tag_list(p["tags"])}</p>
<h1>{html.escape(p["title"])}</h1>
<p class="lede">{html.escape(p["summary"])}</p>
<div class="prose">
{p["html"]}
</div>
</article>
{pager}"""
        (OUT / "posts" / f"{p['slug']}.html").write_text(
            page(f'{p["title"]} · {SITE["title"]}', body, depth=1, description=p["summary"]),
            encoding="utf-8")

    items = "\n".join(
        f"""<li data-tags="{' '.join(p['tags'])}">
  <a href="posts/{p['slug']}.html"><span class="num">{p['num']:02d}</span><span class="t">{html.escape(p['title'])}</span></a>
  <p>{html.escape(p['summary'])}</p>
  <p class="meta">{display_date(p['date'])} · {kind_label(p)}{p['minutes']} min · {tag_list(p['tags'])}</p>
</li>""" for p in posts)
    filters = '<button class="on" data-tag="" onclick="filterPosts(this)">all</button>' + "".join(
        f'<button data-tag="{t}" onclick="filterPosts(this)">{t}</button>' for t in all_tags)
    index = f"""<section class="intro">
<h1>{SITE["tagline"]}</h1>
<p>Essays on how models get served, how agents get built, and how anyone knows the output is right. Each one cites its sources, and the numbers come from the papers.</p>
</section>
<div class="filters">{filters}</div>
<ol class="posts">
{items}
</ol>
<script>
function filterPosts(b) {{
  document.querySelectorAll('.filters button').forEach(x => x.classList.toggle('on', x === b));
  const t = b.dataset.tag;
  document.querySelectorAll('.posts li').forEach(li =>
    li.hidden = t && !li.dataset.tags.split(' ').includes(t));
}}
</script>"""
    (OUT / "index.html").write_text(
        page(SITE["title"], index), encoding="utf-8")

    about_src = (ROOT / "about.md").read_text(encoding="utf-8")
    about = f'<article><h1>About</h1><div class="prose">{markdown(about_src)}</div></article>'
    (OUT / "about.html").write_text(page(f'About · {SITE["title"]}', about), encoding="utf-8")
    print(f"Built {len(posts)} posts into {OUT}")


if __name__ == "__main__":
    build()
