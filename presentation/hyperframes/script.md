# Dev10x — 2-Minute Product Walkthrough

Format: HeyGen-style avatar narration + screen capture overlays, 1920×1080.
Total runtime: **~2:50**. Assumes 24-fps render.

Each scene lists: voice-over (VO), on-screen text (OST), asset cues.
`data-*` attribute timings below map 1:1 to `composition.html`.

---

## Scene 1 — Cold open (0:00 – 0:10)

**VO:** "One command. A ticket, a PR, a merge. Dev10x turns your
intent into shippable code — and keeps you out of the loop until
a decision actually needs you."

**OST:** `/Dev10x:work-on  TEAM-133  sentry://...`
(monospace, center, 56pt, fades in char-by-char at 0:02)

**Assets:**
- `assets/avatar-intro.mp4` — avatar mid-shot, neutral backdrop
- `assets/sfx-whoosh.wav` — single transition hit at 0:09

---

## Scene 2 — work-on orchestrator (0:10 – 0:35)

**VO:** "`work-on` takes anything — a ticket URL, a Sentry link, a
Slack thread, plain English — and runs four phases: classify,
gather, plan, execute. Context arrives from every source in
parallel. A playbook picks the right shipping pipeline. You
approve once."

**OST cards (sequential, 3s each):**
1. `Phase 1 · Classify` — tag cloud: `linear-ticket`, `github-pr`, `sentry-issue`, `note`
2. `Phase 2 · Gather (parallel)` — subagent fan-out graphic
3. `Phase 3 · Plan` — numbered task list with "Approve / Edit"
4. `Phase 4 · Execute` — green checkmarks flowing down

**OST pill (0:28–0:35):** `friction: adaptive  ·  mode: solo-maintainer`
(bottom-right, rounded, green)

**Assets:**
- `assets/screen-work-on.mp4` — terminal recording, 1080×720, centered
- `assets/avatar-talking.mp4` — PiP bottom-left, 320×320

---

## Scene 3 — Code review with fixups (0:35 – 0:55)

**VO:** "Dev10x reviews your own branch before you push. Every
finding becomes a `fixup!` commit pointing at the original change.
No rebase gymnastics. No review-comment archaeology."

**OST (0:38–0:55):** terminal text scroll, left half:
```
Dev10x:review   →  3 findings
Dev10x:review-fix
  ✓ fixup! abc123  Extract helper
  ✓ fixup! def456  Add type hints
  ✓ fixup! 789abc  Guard null case
```

**Assets:**
- `assets/screen-review.mp4` — terminal capture
- `assets/lottie-checkmark.json` — per-fixup confetti flourish

---

## Scene 4 — gh-pr-respond auto-chain (0:55 – 1:25)

**VO:** "Review came back with comments? `gh-pr-respond` triages
each thread, writes the fix as a `fixup!`, pushes, grooms the
history, force-pushes, marks the PR ready, re-monitors CI after
every force push — because force push invalidates CI — and merges
when it's green. No babysitting."

**OST (pipeline diagram animating left-to-right, 0:58–1:22):**
```
fixup → push → groom → push -f → ready → monitor → merge
```
Each node lights up green as VO hits the word. `monitor` pulses
while CI is running.

**OST callout box (1:15–1:25):**
`force push invalidates CI — re-monitor before declaring green`
(yellow border, sticky-note style)

**Assets:**
- `assets/screen-respond.mp4` — real session recording
- `assets/sfx-chime.wav` — one per pipeline stage

---

## Scene 5 — gh-pr-monitor in the background (1:25 – 1:50)

**VO:** "Meanwhile, `gh-pr-monitor` watches from the background.
CI failures, bot reviews, unresolved threads — it catches them,
triages them, files fixups, and pings you only when the PR is
green and ready."

**OST (timeline bar, 1:28–1:48):**
`CI running... ✓  claude-review: 2 comments → fixups pushed ✓
hygiene-review: ✓  ready to merge`

**Assets:**
- `assets/screen-monitor.mp4` — split-screen: status board + terminal
- `assets/avatar-talking-2.mp4` — PiP

---

## Scene 6 — Beautiful git log (1:50 – 2:15)

**VO:** "Every commit is outcome-focused. Not 'add this', not
'update that' — what the change enables for the user. Scroll back
through six months of history and you read a product story."

**OST (terminal scroll, monospace 32pt, auto-scrolling 1:52–2:15):**
```
✨ GH-959 Shorten session startup by consolidating hooks
✨ GH-860 Surface per-hook execution timing for latency triage
✨ GH-413 Let users dial hook strictness per session
✨ GH-955 Prevent silent merges past unresolved CI checks
✨ GH-952 Offer structured retry after rejected commands
✨ GH-940 Enable auto-merge in solo-maintainer shipping pipeline
✨ GH-908 Support multi-platform installs via unified CLI
♻️ GH-928 Strengthen recurring audit finding guards
✨ GH-934 Enable decision-aware session resume guidance
```

**OST callout (2:08–2:15):** `gitmoji + ticket + JTBD outcome — enforced by hooks`

**Assets:**
- `assets/git-log-scroll.mp4` — recorded `git log --oneline` scroll
- `assets/sfx-keystroke.wav` — typewriter loop under the scroll

---

## Scene 7 — Hook profile tiers (2:15 – 2:35)

**VO:** "Hooks keep you honest. Dial strictness per session:
`minimal` for throwaway scripts, `standard` for daily work,
`strict` when you want gitmoji and JTBD enforced. One env var."

**OST three-column chart (2:18–2:33):**
| minimal | standard | strict |
|:-:|:-:|:-:|
| DX001–DX005 | +skill-redirect | +commit-jtbd |
| safety only | default | shared repos |

**OST terminal line (2:30–2:35):** `export DEV10X_HOOK_PROFILE=strict`

**Assets:**
- `assets/screen-hooks.mp4` — chart animated with cells filling in

---

## Scene 8 — Close (2:35 – 2:50)

**VO:** "Seventy skills. Twenty-one agents. Sixteen hooks. One
opinionated, composable, solo-friendly shipping pipeline. Dev10x."

**OST (centered, large):**
```
70  skills
21  agents
16  hooks
```
(count-up animation, 2:37–2:42)

**OST bottom (2:45–2:50):** `github.com/Dev10x-Guru/dev10x-claude`

**Assets:**
- `assets/avatar-outro.mp4` — avatar mid-shot
- `assets/logo.png` — Dev10x wordmark
- `assets/sfx-close.wav` — soft resolve

---

## Asset inventory (to record/source)

| Asset | Duration | Notes |
|---|---|---|
| `avatar-intro.mp4` | 10s | HeyGen avatar, neutral backdrop |
| `avatar-talking.mp4` | 25s | loop-safe, for PiP |
| `avatar-talking-2.mp4` | 25s | second angle |
| `avatar-outro.mp4` | 15s | sign-off |
| `screen-work-on.mp4` | 25s | terminal capture |
| `screen-review.mp4` | 20s | terminal capture |
| `screen-respond.mp4` | 30s | terminal capture |
| `screen-monitor.mp4` | 25s | split-screen |
| `git-log-scroll.mp4` | 25s | `git log --oneline` scroll |
| `screen-hooks.mp4` | 20s | chart animation |
| `logo.png` | — | wordmark |
| `sfx-whoosh.wav` | 0.5s | transitions |
| `sfx-chime.wav` | 0.3s | pipeline stage ticks |
| `sfx-keystroke.wav` | loop | under git log |
| `sfx-close.wav` | 2s | outro |
| `lottie-checkmark.json` | 1s | per-fixup flourish |
| `bg-music.wav` | 170s | -18 dB bed |
