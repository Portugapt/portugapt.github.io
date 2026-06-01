# Rich content & interactive assets — design exploration

**Status:** Deferred. No real need yet. This is a design note so the idea can be
picked up quickly when an actual problem appears. **Do not build any of this
pre-emptively.**

This captures two related explorations:

1. A WYSIWYG authoring backend with SQLite as the content store.
2. Per-post opt-in loading of extra render assets (diagrams, charts, wasm).

---

## TL;DR / decisions reached

- **Markdown stays the source of truth.** Obsidian is a perfectly good editor
  for it today. A WYSIWYG editor + SQLite store buys *authoring ergonomics*, not
  *content capability* — everything renderable from a WYSIWYG is renderable from
  a markdown fence + a build-time renderer. Revisit only if/when authoring
  bespoke **interactive components** (with their own editing UI) becomes a real
  need. See [SQLite / WYSIWYG backend](#sqlite--wysiwyg-backend-deferred).
- **Expressiveness lives in the generator, not the editor.** Want more kinds of
  content? Add renderers to the parse/generate pipeline.
- **Two tiers of "extra asset":**
  - *Build-time* (e.g. `dot`, `mermaid`) → rendered to inline `<svg>` at build,
    ships **zero** runtime JS/wasm, stays crawlable and boost-safe.
  - *Runtime* (e.g. `chart.js`, `python-wasm`, `duckdb-wasm`) → needs JS/wasm in
    the browser; load **from CDN**, **only on pages that opt in**, and
    **lazily** (on visible/scroll, Astro-style).
- **Opt-in via frontmatter list:** `additional_assets: [dot, mermaid, chart-js]`.
  A capability registry maps each name to a handler.
- **Anything off the web baseline / any wasm → CDN.** Don't try to self-host
  Pyodide etc. in the repo (GitHub Pages file/repo size limits).

---

## The `additional_assets` mechanism

Per-page declarative manifest in frontmatter:

```yaml
---
title: "Some post"
additional_assets: [dot, mermaid, chart-js]
---
```

The generator looks each name up in a **capability registry**. Each entry
declares one of two handler kinds:

```
registry
├─ build-time  → consume fences during build, emit inline <svg>, inject nothing
│   ├─ dot      (graphviz / viz.js at build)
│   └─ mermaid  (mmdc at build)
└─ runtime     → inject loader (CDN) into THIS page only, lazy-init
    ├─ chart-js     (likely the first real use case — interactive data viz)
    ├─ python-wasm  (Pyodide; maybe, for interactive code)
    └─ duckdb-wasm  (maybe, for in-browser data querying)
```

Same frontmatter syntax abstracts over both tiers. Adding a future asset = one
registry entry mapping a name to `{ build-time transform | runtime loader tags |
boost + lazy-load behavior }`.

> Note: build-time assets (`dot`, `mermaid`) *could* be auto-detected by scanning
> for the relevant fenced code blocks instead of requiring the frontmatter flag.
> Decided against for now — an explicit uniform list is the cleaner contract, and
> it's the only option for runtime assets that aren't inferable from a fence.

---

## Build-time renderers (dot, mermaid)

Render fences to inline SVG **at build**, so even pages that *use* a diagram ship
no runtime library:

- No JS/wasm download, no flash-of-unrendered-diagram.
- Crawlable, works with JS off, fully compatible with `hx-boost` navigation.
- On-brand with the site's inline-CSS / no-CDN / static ethos.

Wiring sketch:

- `dot`: pipe ` ```dot ` block contents through Graphviz (`dot -Tsvg`) or
  `viz.js`/`@hpcc-js/wasm` at build time; replace the fence with the SVG.
- `mermaid`: `@mermaid-js/mermaid-cli` (`mmdc`) fence → SVG at build.
- Hook point: the parse/render stage in `src/electric_toolbox/parsing/` (where
  markdown is turned into rendered HTML). Theme the SVG to match the site.

For Mermaid/Dot, "only load when needed" collapses to "never load" — the gating
is moot; you get the savings everywhere for free.

---

## Runtime assets (chart.js, python-wasm, duckdb-wasm)

These **must** run in the browser, so per-page gating + lazy loading genuinely
pay off.

### Policy
- **CDN, not self-hosted.** Anything off the web baseline / any wasm goes to a
  CDN (jsDelivr). Pyodide (~10 MB+) is impractical to keep in the repo
  (GitHub Pages ~100 MB/file, ~1 GB repo soft limits, slow clones). This is a
  conscious exception to the site's otherwise no-CDN principle, scoped to runtime
  assets only.
- **Lazy load (Astro `client:visible` style).** Don't fetch the library on page
  load; use an `IntersectionObserver` so the asset loads when its block scrolls
  into view. Keeps posts that merely *contain* a chart cheap until the reader
  reaches it.

### chart.js — the likely first real use case
Interactive way to look at data; appealing but **not needed right now**.
Wiring when the time comes:
1. Author writes a data block (e.g. a fenced ` ```chart ` JSON/config, or a
   `<canvas data-chart="…">` placeholder).
2. Registry entry for `chart-js` injects a small loader **inside the swapped
   body** (see hx-boost gotcha) that, on `IntersectionObserver` visible, dynamic-
   imports Chart.js from CDN and renders into the canvas.
3. Provide a no-JS fallback (a static image or a `<table>` of the data) so the
   page degrades gracefully and stays meaningful to crawlers.

### python-wasm (Pyodide) / duckdb-wasm — maybe, someday
Only if interactive code execution / in-browser querying becomes a real want.
Same lazy + CDN approach, plus the extra constraints below.

---

## GitHub Pages gotchas (plan around these)

### 1. No custom HTTP headers → no `SharedArrayBuffer`
GitHub Pages serves static files and can't set `Cross-Origin-Opener-Policy` /
`Cross-Origin-Embedder-Policy`. The **threaded** builds of Pyodide and
DuckDB-Wasm need `SharedArrayBuffer`, which requires those isolation headers.
Options:
- Use the **single-threaded / non-SAB builds** (slower but work). Preferred
  starting point.
- Or the `coi-serviceworker` hack (a service worker re-serving responses with the
  isolation headers) — fiddly, adds a SW where there is none today, interacts
  awkwardly with caching. Avoid unless necessary.

### 2. `hx-boost` + live runtime don't mix cleanly
Boosted navigation swaps only `#body-content`; it does **not** re-evaluate
`<head>` or tear down page state. A Chart.js instance, or worse a Pyodide/DuckDB
interpreter with web workers, can fail to initialize (its `<head>` script never
runs) or leak across "navigations."

- **Loader scripts must live inside the swapped body**, not `<head>` — otherwise
  they never execute on boosted navigation.
- **Pages with a heavy runtime asset (pyodide/duckdb) should opt out of boost**
  — emit `hx-boost="false"` (or a `data-no-boost` flag) so they do a full
  navigation with clean init/teardown. Chart.js is lighter and may be fine inside
  the body without disabling boost — verify.

---

## SQLite / WYSIWYG backend (deferred)

Original idea: a standalone authoring backend (Go/Rust, run locally or in the
cluster) that owns a SQLite content store + the git/GitHub commit workflow, with
a WYSIWYG editor, while CI keeps building static HTML.

Findings:
- **Viable**, and the clean separation is: backend = authoring + commit; existing
  GitHub Action = build + deploy. They only meet at a commit on the branch.
- **No persistent server on GitHub Pages**, so "backend" = a local/cluster app
  that pushes to the repo (git push with deploy key/PAT, or the GitHub Git Data
  API with a GitHub App token for stateless pods). Make the **repo the source of
  truth** and the app stateless (fetch DB/content on start, push on save).
- **The phiresky `sql.js-httpvfs` trick** (reading SQLite via HTTP Range requests
  in the browser) is real and works on repo hosting, but is a **mismatch** here:
  it kills SEO/static-first (the whole point of this site) and only pays off for
  large queryable datasets, not a small blog. Reserve it for a future
  large-dataset feature (e.g. search over thousands of posts), not post serving.
- **Gotcha:** a committed SQLite blob is opaque to git diffs (whole file rewritten
  per save). Either keep markdown-as-source (best — clean diffs, no pipeline
  change) or emit a text mirror alongside the DB for review.

**Recommendation:** don't build the backend or switch to SQLite for content. Keep
markdown + Obsidian. SQLite-as-source is "just wiring" in the parse stage if ever
wanted, but it earns its complexity only alongside authored **interactive
components** that need a custom editing UI.

---

## When to pick each of these up (triggers)

| Trigger | Pick up |
| --- | --- |
| A post would genuinely benefit from a diagram | Build-time `dot` / `mermaid` → inline SVG |
| You want to show interactive data in a post | `chart-js` runtime asset (lazy + CDN + no-JS fallback) |
| You want readers to run/edit code in the browser | `python-wasm` (Pyodide) — mind COOP/COEP + boost |
| You want in-browser data querying over a dataset | `duckdb-wasm` — same constraints |
| Authoring markdown gets painful for **interactive components** with parameters | Reconsider WYSIWYG editor + (maybe) SQLite source |
| You ship a large queryable dataset (search, explorer) | Reconsider `sql.js-httpvfs` Range-request reading for *that* feature only |

## First concrete step when a trigger fires

1. Add the `additional_assets` frontmatter field + a capability registry to the
   parse/generate stage (`src/electric_toolbox/`).
2. Implement just the one handler you need (build-time transform or lazy CDN
   loader), with a no-JS fallback and the hx-boost handling above.
3. Add one demo post exercising it to measure real cost/behavior before rolling
   it out.
