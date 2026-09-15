# Inner-excellence-articles

Articles related to inner excellence book and learnings.

Each piece takes a passage from a teacher and works it against a stretch of an
ordinary day. The passage is the fixed part. The writing around it gets
re-rendered as the practice changes shape, so a piece carries both the date it
was first sent and the revision shape it currently stands in.

## Index

| Pillar | Title | Sent | Shape |
|---|---|---|---|
| P3 — Attention Is a Moral Act | [Let us be free in the slow line](posts/2026-08-30-p3-attention-is-a-moral-act.md) | 2026-08-30 | 21 |

## How this repo is put together

```
posts/*.md      the source            — words only, one file per article
theme/post.css  the design            — palette, type, layout; one place
theme/post.html the page skeleton     — slots the renderer fills
render.py       the renderer          — the only thing that joins the two
build/*.html    output                — generated, gitignored, never edited
```

Source and design never mix. An article is written once, as markdown. The
design is set once, in `theme/`. `render.py` is the only path between them, so
the published page cannot drift from the words in `posts/`.

## Publishing an article

```sh
python3 render.py                      # render every post
python3 render.py posts/some-post.md   # render one
```

Stdlib only, no install step. The HTML lands in `build/`. Never hand-edit it —
it is overwritten on the next run. To change how an article *looks*, edit
`theme/`; to change what it *says*, edit `posts/`.

## Writing conventions

Front matter carries `title`, `pillar`, `originally_sent`, `re_rendered`,
`revision_shape`, `standfirst`, and `sources`. The body is prose only — no
title heading, since the title comes from front matter.

Five markdown constructs carry meaning, and each also reads correctly on
GitHub, so the source file is never a worse version of the article:

| You write | It becomes |
|---|---|
| the first paragraph | the lede, set larger |
| the last paragraph | the close, set in full ink |
| `*a whole paragraph*` | a pivot line, italic serif |
| `> quoted lines` | the pull quote; a final line opening with an em dash becomes its attribution |
| `- an item` | an instance on the marked list |

Posts are named `YYYY-MM-DD-<pillar>-<slug>.md`, dated by when the piece was
first sent rather than when it was last re-rendered.

The layout is flat on purpose. One piece is one instance, and one instance is
not yet evidence of a shape — no pillar directories, no tagging scheme, no
multi-page site until a second piece shows what actually varies between them.
The index table above is the only abstraction here.

## Re-rendering

A re-rendered piece is an edit to the existing file, not a new one. Update
`re_rendered` and `revision_shape` in the front matter, run `render.py`, and
let git hold the earlier version — the history is the record of how the
practice moved.
