# Todo: MovGent Cinematic UI Redesign

- [x] Task 1: Write `tasks/plan.md` + `tasks/todo.md`
      Acceptance: both files exist and match the agreed 4-phase plan
      Deps: None

- [x] Task 2: Theme foundation — `.streamlit/config.toml`, `style.css` (palette, fonts, variables), CSS injection in `main.py`
      Acceptance: dark ink background, Bebas Neue/Manrope/IBM Plex Mono loaded, widgets use amber primary
      Deps: Task 1

### Checkpoint: Phase 1 (branch `feature/ui-theme-foundation`)
- [x] `python -m py_compile main.py` passes
- [x] `streamlit run main.py` shows themed dark app
- [x] Human reviews, then merge to `dev`

- [x] Task 3: Filmstrip sprocket header — MOVGENT wordmark + "NOW SHOWING · MOVIE AGENT" eyebrow
      Acceptance: header band with sprocket holes renders across the top, display face used with restraint
      Deps: Task 2

- [x] Task 4: Letterboxed chat screen + scene cards — assistant messages numbered `🎬 001…`, teal right-aligned user bubbles
      Acceptance: full history replays as framed scene cards in sequence; framing intact at ~360px width
      Deps: Task 3

### Checkpoint: Phase 2 (branch `feature/ui-chat-screen`)
- [x] `python -m py_compile main.py` passes
- [x] `streamlit run main.py` shows filmstrip header + scene cards
- [x] Human reviews, then merge to `dev`

- [ ] Task 5: Sticky credits sidebar — "Carte Credits" panel: Cast (routed agents), Footage (tokens), Budget (cost) from the last assistant message
      Acceptance: panel populates after a run; shows empty-state copy before the first run
      Deps: Task 4

- [ ] Task 6: Session controls — mono session-id chip + "Reset conversation" button
      Acceptance: reset clears messages and re-rolls session id; chip shows current id
      Deps: Task 5

### Checkpoint: Phase 3 (branch `feature/ui-credits-sidebar`)
- [ ] `python -m py_compile main.py` passes
- [ ] `streamlit run main.py` shows sidebar credits after a chat run
- [ ] Human reviews, then merge to `dev`

- [ ] Task 7: REC indicator — pulsing `● REC · Directing…` placeholder while `run_chatbot` executes
      Acceptance: pulse visible during processing only; no animation under `prefers-reduced-motion`
      Deps: Task 6

- [ ] Task 8: Empty-state invitation + 3 example-question chips (clicking starts a chat)
      Acceptance: empty chat shows invitation + working chips; chips disappear after first message
      Deps: Task 7

- [ ] Task 9: Polish pass — amber hover glow on scene cards, visible keyboard focus everywhere, mobile responsive check
      Acceptance: all interactive elements have visible focus; layout holds on mobile
      Deps: Task 8

### Checkpoint: Complete (branch `feature/ui-interactions`)
- [ ] `python -m py_compile main.py` passes
- [ ] `streamlit run main.py` — full flow: empty state → chips → REC pulse → scene card + credits sidebar
- [ ] Human reviews, then merge to `dev`
