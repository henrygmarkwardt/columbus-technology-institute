# Columbus Technology Institute (CIT) — Design Doc

_Office-hours session · 2026-06-17 · Builder mode · design-reviewed (gaps filled)_

## Concept

A deadpan parody of a frontier AI research lab. CIT presents toy/joke projects with
the gravity, restraint, and visual polish of Anthropic or Thinking Machines Lab. The
comedic payload lives entirely in the **content**; the **design never winks**.

**Comedic thesis:** The funnier the substance, the more serious the presentation must
be. A site that looks like a real $1B lab announcing it builds "the only frontier AI
for cobblers" is funnier than any joke design. Restraint is the punchline.

## Goal & posture

- For fun, held to a real quality bar.
- **Intentionally few features.** Two pages, executed flawlessly, beats a sprawling
  half-built site. Scope discipline is the quality strategy.
- Success = a stranger can't tell at a glance whether it's real.

## Audience

People the builder shows it to. The "whoa" is the rotating hook: calm, mechanical
word-roll delivering absurd payloads.

---

## Visual system

### Color (locked)
| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#FFF8E8` | Primary page background (warm cream). The whole site lives here. |
| `--bg-alt` | `#FFEDC2` | Secondary background — footer band and full-width section bands ONLY. Never behind accent-colored text (see contrast note). |
| `--accent` | `#912F56` | The rotating word, links, hairline rules, small marks. A spice, used sparingly. |
| `--text` | `#1F2932` | All headings and body text. |
| `--text-muted` | `rgba(31,41,50,0.66)` | Sub-lines, footer secondary text, captions. |

**Contrast notes (verified intent):**
- `--text` on `--bg` and on `--bg-alt`: very high contrast, passes AAA. Safe everywhere.
- `--accent` on `--bg` (cream): passes WCAG AA for the large hook text and for links. This
  is the only place accent text appears.
- Do NOT put `--accent` text on `--bg-alt` (`#FFEDC2` is darker; contrast drops below AA).
  In the footer band, body text is `--text`/`--text-muted`; links use `--text` with an
  underline on hover, not accent.

### Typography
Anthropic's real fonts (Copernicus serif, Styrene grotesque) are proprietary. We match
the *feel* with free fonts loaded from Google Fonts:

- **Display + body serif:** `Newsreader` (warm, literary old-style serif — closest free
  analog to Copernicus). Single fallback to swap if it reads wrong: `Source Serif 4`.
- **Small UI / nav / labels:** `Inter` (clean grotesque, stands in for Styrene).
- System fallback stack: `Newsreader, Georgia, 'Times New Roman', serif` and
  `Inter, -apple-system, system-ui, sans-serif`.

**Type scale** (all use `clamp()` so they're responsive without breakpoints):
| Role | Font / weight | Size | Line-height | Notes |
|------|---------------|------|-------------|-------|
| Hook (h1) | Newsreader 500 | `clamp(2.25rem, 6vw, 4rem)` | 1.08 | letter-spacing `-0.01em` |
| Page title (Research) | Newsreader 500 | `clamp(1.75rem, 4vw, 2.5rem)` | 1.1 | |
| Sub-line | Newsreader 400 | `clamp(1rem, 2.2vw, 1.25rem)` | 1.5 | color `--text-muted` |
| Body (research) | Newsreader 400 | `1.125rem` | 1.6 | measure max `65ch` |
| Wordmark | Inter 600 | `1rem` | 1 | tracked `+0.02em` |
| Nav link | Inter 500 | `0.95rem` | 1 | |
| Footer text | Inter 400 | `0.875rem` | 1.5 | |

### Spacing scale (4px base)
`0.5rem · 1rem · 1.5rem · 2rem · 3rem · 5rem · 8rem`. Expose as `--space-1..7` or use directly.
Page side margins: `clamp(1.5rem, 8vw, 8rem)`. Generous by default, never cramped.

### Layout principles
- One column. Generous whitespace. Lab-grade restraint; every element earns its place.
- **Left-aligned, editorial.** Not centered. Reads more like a serious institute.
- Hero text constrained to a narrow measure (`max-width: ~820px`).
- No drop shadows, no gradients, no rounded-everything, **no cards.** Thin `--accent`
  hairlines are the only ornament.
- Everything plays it straight.

---

## The hook (centerpiece)

Visible line (left-aligned):

> **The Only Frontier AI built for `[rotating word]`**

### Markup & accessibility (this is the part that breaks if done wrong)
- The hook is the page `<h1>`. For screen readers and SEO, the `<h1>` carries a **static,
  complete** phrase: `The Only Frontier AI built for everyone.` (or similar deadpan line).
- The animated rotating word is **decorative**: its container is `aria-hidden="true"`, so
  assistive tech reads the static h1 once and is not spammed every 2 seconds.
- Visible structure: the static words `The Only Frontier AI built for ` then a rotating
  slot as the **last token on the line**.

### Width / motion behavior
- Because the line is **left-aligned**, the rotating word being last means the preceding
  words never shift. Only trailing whitespace changes when the word width changes. No jump.
- The rotating slot is an `inline-block` with `overflow: hidden` and height = one line.
  The candidate words are stacked vertically inside; a timer animates `transform: translateY`
  to slide the next word up into view (the slot-machine roll).
- Rotating word color: `--accent`.
- Cadence: hold each word **2.0s**, slide transition **~450ms** `cubic-bezier(.22,.61,.36,1)`.
- Word list (one editable array, easy to extend per the assignment):
  `frogs`, `Canadians`, `pizza-making robots`, `cobblers`, `Columbites`.
- **Longest word governs nothing structural** because of left-alignment, but confirm
  `pizza-making robots` wraps gracefully on narrow screens (it may break to its own line;
  that's fine and still reads).

### Reduced motion
- Under `@media (prefers-reduced-motion: reduce)`: disable the vertical slide. Replace with
  a quiet **opacity cross-fade** (no transform), slower cadence (~3.5s). Content still
  rotates; nothing slides. This keeps the joke without triggering motion sensitivity.

---

## Pages

### 1. Home
Read order (first → third):
1. **The hook** (h1), vertically centered in the viewport, left-aligned on the narrow measure.
2. **One deadpan sub-line** in `--text-muted` directly beneath. Placeholder structure:
   a single straight-faced institutional sentence (e.g. "An independent frontier research
   institute. Columbus, Ohio." — final copy TBD by builder). One line, no more.
3. **A single quiet text link** to Research (e.g. "Read our research →"), `--accent`,
   understated. No buttons, no hero image, nothing else above the fold.

Top of page: persistent nav (see Global chrome). Bottom: footer band. Between hook and
footer, the home page is intentionally near-empty — that restraint is the look.

### 2. Research (empty-state-as-feature)
Designed like a real publications index that is currently empty, never a blank page.
- Same nav.
- Page title "Research" (Newsreader display size).
- One deadpan line in `--text-muted`: e.g. "Publications from the Columbus Technology
  Institute." followed by a dignified empty note: "No papers yet. Our researchers are
  hard at work." (final copy TBD).
- A single thin `--accent` hairline rule under the title to give the page structure and
  signal "this is a real section, just empty."
- No fake spinner, no "coming soon" badge — those read as unfinished. The empty state is
  styled with the same care as a full one.

---

## Global chrome

### Nav (persistent, both pages)
- Wordmark left: full **"Columbus Technology Institute"** in Inter 600 (`--text`). Below
  ~480px, abbreviate to **"CIT"** to avoid wrapping.
- Right: one nav link, **"Research"** (Inter 500). On the Research page it gets a subtle
  current-state indicator (a thin `--accent` underline). Tap target min 44px tall.
- Thin `--accent` (or 1px `--text` at low opacity) hairline under the nav, optional.
- No hamburger — one link never needs a menu.

### Footer (`--bg-alt` band, both pages)
- Deadpan institutional footer: "© 2026 Columbus Technology Institute" + "Columbus, Ohio."
- Optional quiet placeholder links (Inter, `--text`, underline on hover). No accent text
  on this band (contrast).

### Document head / trust details (sell the illusion)
- `<title>`: "Columbus Technology Institute" (home) / "Research — Columbus Technology
  Institute" (research).
- Favicon: simple monogram mark — "CIT" or a single glyph in `--accent` on `--bg`. A
  default favicon instantly breaks the "real lab" illusion, so this ships in v1.
- Meta description + Open Graph tags written in the same straight-faced institutional
  voice, so link previews carry the bit.

---

## Responsive

- One fluid column at every width; the design is inherently responsive via `clamp()`.
- One soft breakpoint at **~640px**: side margins shrink toward `1.5rem`, hook type scales
  down via its `clamp()` floor, wordmark may abbreviate to "CIT" (~480px).
- The hook sentence wraps naturally; the rotating word stays the last token and is allowed
  to fall to its own line on narrow screens.
- Touch targets ≥ 44px. No hover-dependent affordances (mobile has no hover): links are
  visibly links (color + underline-on-hover, but discoverable without hover via color).

---

## Tech & structure (Approach A — plain static)

```
index.html        # home + hook (static h1 + decorative animated slot)
research.html     # research empty state
styles.css        # tokens (CSS custom properties), type scale, layout, reduced-motion
script.js         # slot-machine word rotation (single editable word array)
favicon.svg       # monogram mark
```

No framework, no build step, no dependencies. Loads instantly.

## Distribution

`git init`, push to GitHub, deploy free via **GitHub Pages** (or Netlify/Vercel). Static = trivial hosting.

## Out of scope (deferred on purpose)

- Real project/research content (builder fills in later).
- Any backend, CMS, analytics, or build tooling.
- Astro migration — revisit only if Research grows into a real multi-post blog.

## The assignment

Collect **8–12 rotating words** that are each individually absurd but delivered straight-faced.
The funniest lists have rhythm: mix short punchy nouns with one oddly specific long one. Drop
them into the word array and we tune cadence against the real animation.

---

## GSTACK REVIEW REPORT

**Skill:** plan-design-review · **Date:** 2026-06-17 · **Plan:** CIT DESIGN.md

| Run | Status | Findings |
|-----|--------|----------|
| design-review (text) | issues_found → resolved | 6 gaps identified and fixed in-plan |

**Dimension scores (after fixes):** IA/hierarchy 9 · hook/interaction 9 · empty states 9 ·
responsive 8 · accessibility 9 · AI-slop 9 · specificity 9. **Overall ~9/10** (5/10 before).

**Gaps closed:** home-page hierarchy; hook width/motion/cadence; reduced-motion + screen-reader
path for the animation; Research empty state; responsive (clamp + 640px breakpoint); trust
details (favicon, title/OG, footer); fixed the "cards" contradiction and the accent-on-`--bg-alt`
contrast risk.

**VERDICT:** Plan is build-ready for Approach A. Remaining items are deferred content
(final copy, favicon glyph), to be decided at build time.

NO UNRESOLVED DECISIONS

```
