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
    """Render a ```chart block as a table of reported values.

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
    signed = any(value < 0 for _, value in rows)
    entries = []
    for label, value in rows:
        number = f"{value:,.0f}" if value.is_integer() and abs(value) >= 100 else f"{value:g}"
        if signed and value > 0:
            number = "+" + number
        entries.append(
            f'<tr><th scope="row">{html.escape(label)}</th><td>{html.escape(number + unit)}</td></tr>')
    caption = inline(meta.get("title", "Reported values"))
    notes = " ".join(inline(meta[key]) if key == "note" else "Source: " + inline(meta[key])
                     for key in ("note", "source") if meta.get(key))
    note_html = f'<p class="media-note">{notes}</p>' if notes else ""
    return (f'<table class="data-table"><caption>{caption}</caption><tbody>'
            + "".join(entries) + "</tbody></table>" + note_html)


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


def diagram(block):
    """Keep a diagram's caption and source as text."""
    meta, _ = _meta_and_rest(block, "<svg")
    parts = []
    if meta.get("title"):
        parts.append(f'<strong>{inline(meta["title"])}</strong>')
    if meta.get("caption"):
        parts.append(inline(meta["caption"]))
    if meta.get("source"):
        parts.append("Source: " + inline(meta["source"]))
    return '<p class="media-note">' + " ".join(parts) + "</p>" if parts else ""


def video(block):
    """Link to the video without loading an embedded thumbnail."""
    meta, _ = _meta_and_rest(block, "\x00")
    vid = meta.get("youtube", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
        return ""
    title = html.escape(meta.get("title", "Video"))
    caption = f' {inline(meta["caption"])}' if meta.get("caption") else ""
    return f'<p class="media-note"><a href="https://www.youtube.com/watch?v={vid}">{title}</a>{caption}</p>'


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
        "minutes": max(1, round(words / 230)),
        "html": markdown(body.strip()),
    }


# ---------- templates ----------

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
<link rel="stylesheet" href="{up}style.css?v=text-only">
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
</body>
</html>
"""


def kind_label(p):
    return f'<span class="kind">{html.escape(p["kind"])}</span> · ' if p["kind"] else ""


def tag_list(tags):
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)


def build():
    OUT.mkdir(exist_ok=True)
    # Empty in place: a preview server or shell may hold these folders open.
    for f in sorted(OUT.rglob("*"), reverse=True):
        if f.is_file():
            f.unlink()
        else:
            shutil.rmtree(f, ignore_errors=True)
    (OUT / "posts").mkdir(exist_ok=True)
    shutil.copy(STATIC / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")

    posts = sorted((parse(p) for p in POSTS.glob("*.md")), key=lambda p: p["date"], reverse=True)
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
