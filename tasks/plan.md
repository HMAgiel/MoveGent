# Implementation Plan: MovGent Cinematic UI Redesign

## Overview

Redesign the MovGent Streamlit chat (`main.py`) into a dark, cinematic "projection room" experience: filmstrip marquee header, letterboxed chat screen with numbered scene cards, a sticky film-credits sidebar (Cast/Footage/Budget from the agent run), and orchestrated interactivity (REC pulse, quick-question chips, focus polish). No new dependencies; theming via `.streamlit/config.toml` + injected CSS.

## Architecture Decisions

- **Palette** grounded in the film color grade (teal-orange) on a blue-tinted charcoal base — deliberately not the generic "near-black + acid accent" dark default:
  - Ink `#0E1217`, Panel `#161C24`, Line `#222A36`, Text `#E7EAEE`, Muted `#8B95A5`, Amber `#F2A93B`, Teal `#5FB3B0`
- **Type**: Bebas Neue (display, marquee/poster caps, used with restraint), Manrope (body), IBM Plex Mono (data/session/frame numbers)
- **Signature metaphor**: chat history as film frames — assistant replies are numbered scene cards; run details become a "Carte Credits" panel (Cast = routed agents, Footage = tokens, Budget = cost)
- **UI copy in English** (user decision); code comments stay Indonesian per `AGENTS.md`
- **Branching**: one `feature/ui-*` branch per phase, off `dev`, one commit, merged back to `dev` after human review — `dev` stays runnable at every checkpoint
- **Run commands**: plain `streamlit run main.py` — `uv` is NOT used (user decision)

## Task List

### Phase 1: Theme foundation — branch `feature/ui-theme-foundation`
- [ ] Task 1: Write plan/todo files (this repo)
- [ ] Task 2: `.streamlit/config.toml` dark theme + `style.css` palette/fonts + CSS injection in `main.py`

### Checkpoint: Phase 1
- [ ] App loads with dark bg, correct fonts, amber-primary widgets

### Phase 2: Filmstrip header + chat screen — branch `feature/ui-chat-screen`
- [ ] Task 3: Sprocket-strip header (MOVGENT wordmark, "NOW SHOWING · MOVIE AGENT" eyebrow)
- [ ] Task 4: Letterboxed chat column + scene cards with frame numbers + teal user bubbles

### Checkpoint: Phase 2
- [ ] History renders as numbered scene cards; framing holds on mobile

### Phase 3: Credits sidebar — branch `feature/ui-credits-sidebar`
- [ ] Task 5: Sticky "Carte Credits" panel (Cast/Footage/Budget from last run)
- [ ] Task 6: Mono session-id chip + "Reset conversation" button

### Checkpoint: Phase 3
- [ ] Sidebar updates after a run; reset clears chat + session id

### Phase 4: Interactivity polish — branch `feature/ui-interactions`
- [ ] Task 7: Pulsing `● REC · Directing…` indicator during processing (respects `prefers-reduced-motion`)
- [ ] Task 8: Empty-state invitation + 3 example-question chips
- [ ] Task 9: Amber hover glow, focus rings, mobile responsive pass

### Checkpoint: Complete
- [ ] All acceptance criteria met; ready for review

## Verification

No test suite, linter, or typecheck in this repo (`AGENTS.md`). Per task:
1. `python -m py_compile main.py`
2. `streamlit run main.py` — manual visual check against acceptance criteria
3. Chat-flow checks (sidecar credits after a run) need the full stack (env, SQLite, Qdrant); layout checks work without it

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Streamlit widget internals change between versions (`>=1.57.0`) | Med | Target stable `data-testid` selectors; keep CSS additive/overridable |
| Chat-flow verification needs full stack (db/Qdrant/keys) | Med | Layout verified on page load alone; chat checks done once stack is up |
| `dev` has uncommitted `.gitignore` change + untracked `skills-lock.json` | Low | Phase commits stage only UI files explicitly |
| Google Fonts require network | Low | Streamlit app already requires network (Qdrant/OpenAI); system fonts as fallback |

## Open Questions

- None (design decisions confirmed with human)
