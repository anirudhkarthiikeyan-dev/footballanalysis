# Future Improvements

Ordered roughly by value-to-effort.

1. **Compile the `.pbix`.** Follow `powerbi/README.md` in an
   environment with Power BI Desktop installed; commit the finished
   file (or a PDF export of the report pages, since `.pbix` binaries
   don't diff well in git).
2. **Team form / momentum measure in Power BI**, properly windowed with
   a "last N matches" table pattern rather than the simplified
   placeholder in `dax/measures.dax`.
3. **Add the Playwright suite to CI** — it exists and passes locally
   (`tests/ui/`, 41 tests) but isn't wired into a CI pipeline yet (no
   CI is configured for this project at all).
4. **Clustering-based team/player archetypes** — a genuinely motivated
   addition to the ML layer (e.g. k-means over team attacking/defensive
   profiles) with the same rigor as the similarity model: a clear
   question, documented features, and evaluation.
5. **Deploy to Streamlit Community Cloud** and link the live URL from
   the README.
6. **Expand the learning log and interview prep** to the full topic
   list in the original project brief.
7. **Gameweek-level player data** (not just season totals) for a richer
   Player Explorer (form over the season, not just end-of-season
   aggregates) — the FPL archive has this in `gws/` per season.
8. **Canonical opponent names for the European module.** Currently only
   the 20 selected clubs have canonical names in `team_master.csv`;
   opponents outside that list display their raw source name. A fuller
   European club master list would let Opponent History display
   consistent names for every club, not just the 20.
9. **Europa League / Conference League** — the same openfootball
   organization publishes these competitions in the same format; could
   extend the European module using `dim_competition` (already
   designed to support more than one competition).
10. **Global Search coverage** — currently searches teams, European
    clubs, players and seasons. Could extend to matches (e.g. "Arsenal
    vs Chelsea 2019") and referees.
