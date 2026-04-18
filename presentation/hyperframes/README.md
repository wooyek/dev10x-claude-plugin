# Dev10x — HyperFrames Walkthrough

A ~2:50 product walkthrough of Dev10x, authored as a
[HyperFrames](https://github.com/heygen-com/hyperframes) HTML
composition. Renders to a 1920×1080 / 24fps MP4.

## Files

| File | Purpose |
|---|---|
| `script.md` | Scene-by-scene voice-over, on-screen text, asset cues |
| `composition.html` | HyperFrames composition — `data-*` timings match the script |
| `styles.css` | Overlay styling (cards, pipeline diagram, stats) |
| `assets/` | Drop voice-overs, screen captures, SFX, logo here |

## Narrative arc

The story follows a real Dev10x session from command to merge —
ordered by impact:

1. Cold open — `work-on` one-shot
2. Phase orchestration (classify → gather → plan → execute)
3. Self-review with `fixup!` commits
4. `gh-pr-respond` auto-chain (push → groom → push -f → ready → monitor → merge)
5. `gh-pr-monitor` background agent
6. Scroll through JTBD-formatted git log
7. Hook profile tiers (`minimal` / `standard` / `strict`)
8. Close — 70 skills · 21 agents · 16 hooks

## How to produce the assets

### Voice-over / avatar (HeyGen)

For each `avatar-*.mp4` listed in `script.md` § Asset Inventory:
1. Copy the VO paragraph from the matching scene
2. Generate with a HeyGen avatar at 1080×1080 (for mid-shot) or 720×720 (for PiP)
3. Export as muxed video+audio MP4; HyperFrames reads the audio track
   alongside the video track — set `muted` off on the avatar clip if
   you want the VO to ride with it, or split VO to a separate track-1
   audio clip.

### Screen captures

| Clip | What to record |
|---|---|
| `screen-work-on.mp4` | Real `/Dev10x:work-on <url>` invocation — classify, gather, plan approval, first few execute ticks |
| `screen-review.mp4` | `Dev10x:review` producing findings, then `Dev10x:review-fix` creating three `fixup!` commits |
| `screen-respond.mp4` | `Dev10x:gh-pr-respond` processing PR comments end-to-end |
| `screen-monitor.mp4` | `Dev10x:gh-pr-monitor` status board — include the bot-review loop |
| `git-log-scroll.mp4` | `git log --oneline --no-decorate \| head -40` in a wide terminal, smooth scroll |
| `screen-hooks.mp4` | The profile-tier table from `.claude/rules/hook-patterns.md`, with one `export DEV10X_HOOK_PROFILE=strict` demo line |

Target 1080p minimum. Use a monospace font with good ligatures.

### SFX & music

Any royalty-free library works. Levels in `composition.html`:

- `bg-music` at `data-volume="0.18"` — keep it as a bed
- `sfx-chime` / `sfx-whoosh` unvolumed (full) — short hits
- `sfx-keystroke` at `0.35` — loops under the git-log scroll
- `sfx-close` at `0.9` — outro punctuation

## Rendering

From the repo root:

```bash
# Install hyperframes CLI once (see upstream README for current install)
# npm install -g @heygen/hyperframes   # example — check upstream

hyperframes render \
  presentation/hyperframes/composition.html \
  --output presentation/hyperframes/out.mp4 \
  --width 1920 --height 1080 --fps 24
```

If you prefer the Docker renderer, mount this directory and point
at `composition.html`. Deterministic output: the same assets and
composition always produce the same MP4.

## Editing the arc

Edit `script.md` first — timings, VO, and cues live there. Then
keep `composition.html` `data-start` / `data-duration` values in
sync. The two files are the canonical source; `styles.css` is
presentational and can be changed freely without touching timings.

## Attribution

Prose and composition are authored material — feel free to adapt,
trim, or restructure for a shorter cut (e.g. 60s teaser: scenes
1 + 4 + 6 + 8).
