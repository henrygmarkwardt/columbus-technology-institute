# Design — Columbus Technology Institute

How this site looks and feels, so a new page (or a new project) can match it.

## The vibe

It looks like a real frontier AI research lab: calm, editorial, confident. Warm
paper background, dark ink, one wine-red accent used sparingly. Lots of whitespace,
everything left-aligned like a well-set document. **No cards, no drop shadows, no
gradients, no rounded boxes.** Restraint is the whole point — the writing is the
joke, the design stays completely straight.

## Color

| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#FFF8E8` | Page background (warm cream) |
| `--bg-alt` | `#FFEDC2` | Footer / quiet panels |
| `--accent` | `#912F56` | Wine red — links, the rotating word, small rules. Used rarely. |
| `--text` | `#1F2932` | Body text (near-black ink) |
| `--text-muted` | `~66% text` | Subheads, captions |
| `--hairline` | `~14% text` | Thin dividers, hover underlines |

One accent color, and only on the cream `--bg` (never on `--bg-alt` — contrast).

## Type

- **Newsreader** (serif) — headings and body. The voice of the site.
- **Inter** (sans) — small UI bits only: nav, buttons, footer, labels.
- Both from Google Fonts. Headings sit at weight 500; nothing is bold-heavy.
- Big type scales with the screen via `clamp()` — e.g. the hero hook runs
  `clamp(2.25rem, 6vw, 4rem)`. Keep line-length comfortable (`--measure: 820px`,
  or ~48–60 characters for paragraphs).

## Layout & spacing

- Single centered column, generous side padding (`--page-x`, scales with width).
- Spacing uses a small fixed scale (`--space-1`…`--space-7`) — reach for those
  instead of arbitrary pixel values.
- Sticky-footer pattern: header / main / footer stacked, main grows to fill.

## Motion

- Subtle and slow. Standard easing is `cubic-bezier(.22,.61,.36,1)` over ~460–600ms.
- Two signature touches: the hero hook's **last word rotates** through a list, and
  the **logo spins a bit on hover** (accumulates — it never snaps back).
- Always honor `prefers-reduced-motion`: swap slides for quiet fades, kill the spin.

## Accessibility notes

- Decorative animation is `aria-hidden`; a plain static sentence carries the real
  meaning for screen readers. Keep both whenever you animate text.
- Tap targets stay ≥44px; the logo `alt` is empty because it's decorative.

## Rules of thumb

- The logo is **hand-drawn — don't regenerate it.** Re-derive the file from source
  with `scripts/process_logo.py` only if needed.
- New tokens go in `:root` in `styles.css`; reuse existing ones first.
- When in doubt, do less. If it feels designed, it's probably too much.
