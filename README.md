# Electric Toolbox

A small, typed static-site generator (`electric_toolbox`) that powers
[portugapt.github.io](https://portugapt.github.io). Markdown content in, a fast
static site out — with first-class SEO/structured data, htmx navigation and a
Tailwind v4 theme.

## How it works

The pipeline is three pure-ish stages (`src/electric_toolbox/`):

1. **parse** (`parsing/`) — read `compile.config.toml` and the markdown in
   `content/`, validate it into frozen pydantic domain models, and build the
   SEO/Open Graph/JSON-LD metadata.
2. **view** (`*/view.py`) — turn domain models into view models (pre-rendered
   strings, merged Open Graph parts, breadcrumb items, …).
3. **generate** (`generate.py`) — render Jinja templates (`templates/`) to
   `website/`.

There is **one document per page**. Navigation uses htmx **`hx-boost`**: links
are plain crawlable `<a href>`, and htmx fetches the target page, extracts
`#body-content` and swaps it in (updating history). On refresh, direct load or
for a crawler it's just a normal static page — which is exactly why this works
unchanged on GitHub Pages. Links are also prefetched on hover (the htmx
`preload` extension).

Tag filtering is **client-side**: every post is in the list, and the `?tag=`
query (set by the filter links, preserved on refresh) hides the rest. Pages
ignore the query string and serve `posts.html`, so `/posts.html?tag=<slug>`
renders filtered on both navigation and refresh.

Icons are inline SVG loaded from `resources/icons/*.svg` (no icon-font CDNs),
the Tailwind CSS is inlined into each page (no render-blocking stylesheet
request), and every generated page is minified. The CSS must therefore be
built *before* the site is generated — `just gen` and CI do this in order.

## Develop

Requires [uv](https://docs.astral.sh/uv/) (Python) and
[bun](https://bun.sh/) (CSS/Tailwind v4).

```sh
uv sync --all-groups   # Python deps
bun install            # Tailwind v4 toolchain
just gen               # build the site into website/
just local-server      # serve + live-reload at :8080
just watch-tailwind     # rebuild CSS on change
uv run pytest          # tests
```

## Configuration — `compile.config.toml`

Site-wide identity and SEO defaults, plus the section list, live in
`compile.config.toml` (documented inline). The `[website]` block feeds the
`WebSite` / `Person` / `Organization` structured data and the social-share
defaults; per-page values from frontmatter always take precedence.

## Content & frontmatter

Posts live in `content/posts/*.md` with YAML frontmatter. Semantic fields map
straight onto Open Graph / schema.org:

```yaml
---
title: "My Post"
description: "One-line summary (used for meta description, og/twitter, summary)."
image: https://…/cover.png        # og:image / twitter:image / BlogPosting image
publication_time: 2025-02-01 15:30:00
modified_time: 2025-02-02 09:00:00 # optional
section: "Functional Programming"
authors:                            # optional; falls back to the config author
  - first_name: João
    last_name: Monteiro
    username: Portugapt
    url: https://github.com/Portugapt
tags: [Functional Programming]      # become filterable tag sub-partials
---
```

Each post page emits `BlogPosting` + `BreadcrumbList` JSON-LD, canonical,
description, Open Graph and Twitter Card tags automatically. Dates are emitted
with a timezone offset (naive frontmatter datetimes are treated as UTC; write
`2025-02-01 15:30:00+01:00` to pin a specific offset).

## Adding a new section or list

1. Add a `[sections.<name>]` table to `compile.config.toml` pointing at a
   markdown file (`type = "singular"`) or folder (`type = "plural"`).
2. Reuse the blog as the template for list pages: the `ViewModelTag` +
   `_post_items.html` + `data-tags` + client-side `?tag=` filter pattern is the
   blueprint for any filterable list (e.g. a CV-by-target-position page or a
   reading-notes list filtered by topic).

## Deploy

Pushing any branch runs `.github/workflows/personalblog.yml`, which builds with
uv + bun and publishes `website/` to GitHub Pages.
