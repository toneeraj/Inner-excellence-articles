#!/usr/bin/env python3
"""Render posts/*.md into build/*.html using theme/post.html + theme/post.css.

The markdown is the source. The theme is the design. This is the only thing
that turns one into the other, so the two can never drift.

Markdown conventions, all of which also read correctly on GitHub:

    front matter    title, pillar, originally_sent, re_rendered,
                    revision_shape, standfirst, sources (list)
    first paragraph becomes the lede
    last paragraph  becomes the close
    *whole para*    becomes a pivot line (set in italic serif)
    > quote         becomes the pull quote; a final line opening with an
                    em dash becomes its attribution caption
    - item          becomes an instance in the marked list

Usage:  python3 render.py [post.md ...]     (no args renders every post)
Stdlib only, no install step.
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
POSTS = ROOT / "posts"
THEME = ROOT / "theme"
BUILD = ROOT / "build"


# ---- front matter -------------------------------------------------------

def parse_front_matter(text):
    """Return (fields, body). Handles `key: value` and `key:` + `  - item`."""
    if not text.startswith("---\n"):
        raise ValueError("post is missing YAML front matter")
    closing = text.index("\n---\n", 3)
    head, body = text[4:closing], text[closing + 5:]

    fields, key = {}, None
    for line in head.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and key:
            fields.setdefault(key, []).append(line.lstrip()[2:].strip())
        elif ":" in line:
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            fields[key] = value if value else []
    return fields, body.strip()


# ---- inline typography --------------------------------------------------

def inline(text):
    """Escape, then apply typographic niceties, then emphasis."""
    out = html.escape(text, quote=False)
    out = out.replace("...", "&hellip;").replace(" -- ", " &mdash; ")
    # straight quotes -> typographic quotes, by what precedes them
    out = re.sub(r'(^|[\s(\[—-])"', r"\1&ldquo;", out)
    out = out.replace('"', "&rdquo;")
    out = re.sub(r"(^|[\s(\[])'", r"\1&lsquo;", out)
    out = out.replace("'", "&rsquo;")
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)


# ---- blocks -------------------------------------------------------------

def render_quote(chunk):
    lines = [re.sub(r"^>\s?", "", ln) for ln in chunk.splitlines()]
    paras, current = [], []
    for line in lines:
        if line.strip():
            current.append(line)
        elif current:
            paras.append(current)
            current = []
    if current:
        paras.append(current)

    parts = ["    <figure class=\"quote\">"]
    for i, para in enumerate(paras):
        is_caption = i == len(paras) - 1 and para[0].lstrip().startswith("—")
        body = ("<br>\n        ".join(inline(ln) for ln in para) if is_caption
                else inline(" ".join(para)))
        tag = "figcaption" if is_caption else "p"
        parts.append(f"      <{tag}>{body}</{tag}>")
    parts.append("    </figure>")
    return "\n".join(parts)


def render_list(chunk):
    items = [inline(ln[2:].strip()) for ln in chunk.splitlines() if ln.startswith("- ")]
    rows = "\n".join(f"      <li>{item}</li>" for item in items)
    return f"    <ul class=\"places\">\n{rows}\n    </ul>"


def render_body(body):
    chunks = [c.strip() for c in re.split(r"\n\s*\n", body) if c.strip()]

    kinds = []
    for chunk in chunks:
        if chunk.startswith(">"):
            kinds.append("quote")
        elif chunk.startswith("- "):
            kinds.append("list")
        elif re.fullmatch(r"\*[^*]+\*", chunk.replace("\n", " ")):
            kinds.append("turn")
        else:
            kinds.append("para")

    plain = [i for i, k in enumerate(kinds) if k == "para"]
    lede, close = (plain[0], plain[-1]) if plain else (None, None)

    out = []
    for i, (chunk, kind) in enumerate(zip(chunks, kinds)):
        text = chunk.replace("\n", " ")
        if kind == "quote":
            out.append(render_quote(chunk))
        elif kind == "list":
            out.append(render_list(chunk))
        elif kind == "turn":
            out.append(f"    <p class=\"turn\">{inline(text.strip('*'))}</p>")
        else:
            cls = " class=\"lede\"" if i == lede else " class=\"close\"" if i == close else ""
            out.append(f"    <p{cls}>{inline(text)}</p>")
    return "\n\n".join(out)


# ---- page ---------------------------------------------------------------

def dashed(value):
    return str(value).replace("-", "&#8211;")


def render_post(path):
    fields, body = parse_front_matter(path.read_text(encoding="utf-8"))
    for required in ("title", "pillar", "originally_sent", "standfirst"):
        if required not in fields:
            raise ValueError(f"{path.name}: front matter is missing '{required}'")

    meta = [f'      <span class="pillar">{inline(fields["pillar"])}</span>',
            f'      <span>Sent {dashed(fields["originally_sent"])}</span>']
    if fields.get("re_rendered"):
        meta.append(f'      <span>Re-rendered {dashed(fields["re_rendered"])}</span>')
    if fields.get("revision_shape"):
        meta.append(f'      <span>Revision shape {fields["revision_shape"]}</span>')

    sources = "\n".join(f"    <span>{inline(s)}</span>"
                        for s in fields.get("sources", []))

    page = (THEME / "post.html").read_text(encoding="utf-8")
    for token, value in (
        ("__CSS__", (THEME / "post.css").read_text(encoding="utf-8").rstrip()),
        ("__TITLE__", inline(fields["title"])),
        ("__STANDFIRST__", inline(fields["standfirst"])),
        ("__META__", "\n".join(meta)),
        ("__BODY__", render_body(body)),
        ("__SOURCES__", sources),
    ):
        page = page.replace(token, value)

    BUILD.mkdir(exist_ok=True)
    out = BUILD / f"{path.stem}.html"
    out.write_text(page, encoding="utf-8")
    return out


def main(argv):
    targets = [pathlib.Path(a) for a in argv] or sorted(POSTS.glob("*.md"))
    if not targets:
        print("no posts found in posts/", file=sys.stderr)
        return 1
    for path in targets:
        out = render_post(path)
        print(f"{path.relative_to(ROOT)}  ->  {out.relative_to(ROOT)}  "
              f"({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
