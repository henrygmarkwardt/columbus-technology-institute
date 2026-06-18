# AGENTS.md — Columbus Technology Institute

Guidance for AI agents (and humans) working in this repo.

## What this is

A static marketing site for the "Columbus Technology Institute" (CIT): a deadpan
parody of a frontier AI lab. The joke lives entirely in the **content** (e.g. the
rotating hook "The Only Frontier AI built for frogs / Canadians / ..."); the
**design plays it 100% straight**, like a real lab. Keep that contrast — never make
the design itself jokey.

## Stack

Plain static HTML + CSS + vanilla JS. 
Hosted on GitHub Pages.



## Deploy

GitHub Pages serves `main` at the repo root. **Pushing to `main` auto-deploys**
Live: https://henrygmarkwardt.github.io/columbus-technology-institute/

> **Always test locally and get the owner's sign-off before pushing.** Do not deploy
> unreviewed changes.

## Conventions

- **Design tokens** live in `:root` in `styles.css`: `--bg #FFF8E8`, `--bg-alt #FFEDC2`,
  `--accent #912F56`, `--text #1F2932`. Accent text only on `--bg` (contrast). No cards,
  no shadows, left-aligned editorial layout. `DESIGN.md` is the source of truth.
- **Type:** Newsreader (serif, headings/body) + Inter (small UI), loaded from Google Fonts.
- **The logo is hand-drawn — do not regenerate it.** To re-derive the asset from the source
  art, use `scripts/process_logo.py`.
```
