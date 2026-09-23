# Future Improvements

Ordered roughly by value-to-effort. Power BI is explicitly not on this
list — it was evaluated and intentionally dropped (see
`docs/PROJECT_PROGRESS.md`); Streamlit is the final, single dashboard
layer for this project.

1. **Stabilize the Playwright suite under repeated/CI-style execution.**
   It's correct — every test passes reliably in isolation, and every
   failure encountered during development was root-caused to a real
   issue and fixed (see `docs/learning/LEARNING_LOG.md`). But 5
   back-to-back runs in one session produced inconsistent results
   (41/41 down to 34/41, different tests each time) on a shared,
   general-purpose machine, pointing to resource contention rather than
   app bugs. Worth investigating: run tests serially with forced
   garbage-collection pauses between them, reduce parallel browser
   contexts, or run on a dedicated (not shared) machine before trusting
   it as a hard CI gate.
2. **Add the Playwright suite to CI** once stabilized (see above) — no
   CI is configured for this project at all yet.
3. **Clustering-based team/player archetypes** — a genuinely motivated
   addition to the ML layer (e.g. k-means over team attacking/defensive
   profiles) with the same rigor as the similarity model: a clear
   question, documented features, and evaluation.
4. **Deploy to Streamlit Community Cloud** and link the live URL from
   the README.
5. **Expand the learning log and interview prep** to the full topic
   list in the original project brief.
6. **Gameweek-level player data** (not just season totals) for a richer
   Player Explorer (form over the season, not just end-of-season
   aggregates) — the FPL archive has this in `gws/` per season.
7. **Canonical opponent names for the European module.** Currently only
   the 20 selected clubs have canonical names in `team_master.csv`;
   opponents outside that list display their raw source name. A fuller
   European club master list would let Opponent History display
   consistent names for every club, not just the 20.
8. **Europa League / Conference League** — the same openfootball
   organization publishes these competitions in the same format; could
   extend the European module using `dim_competition` (already
   designed to support more than one competition).
9. **Global Search coverage** — currently searches teams, European
   clubs, players and seasons. Could extend to matches (e.g. "Arsenal
   vs Chelsea 2019") and referees.
