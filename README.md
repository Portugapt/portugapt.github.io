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

Every page is emitted in three shapes so the same URL works with or without JS:

- **full** (`/posts.html`) — the complete document, used on first load/refresh.
- **fragment** (`/posts_hx.html`, `/posts/<slug>.html`'s `_hx` sibling) — the
  inner content only, swapped into `#body-content` by htmx during navigation.
- **query sub-partials** (`/posts_hx/tag/<slug>.html`) — filtered list fragments
  swapped into `#post-list`. The filter survives a refresh: loading
  `/posts.html?tag=<slug>` re-hydrates the matching fragment.

Navigation, breadcrumbs and post links are real `<a href>` (crawlable, keyboard
friendly) that htmx progressively enhances.

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
description, Open Graph and Twitter Card tags automatically.

## Adding a new section or list

1. Add a `[sections.<name>]` table to `compile.config.toml` pointing at a
   markdown file (`type = "singular"`) or folder (`type = "plural"`).
2. Reuse the blog as the template for list pages: the `ViewModelTag` +
   `_post_items.html` + per-tag fragment pattern in `generate.py` is the
   blueprint for any query-param-filtered list (e.g. a CV-by-target-position
   page or a reading-notes list filtered by topic).

## Deploy

Pushing any branch runs `.github/workflows/personalblog.yml`, which builds with
uv + bun and publishes `website/` to GitHub Pages.
