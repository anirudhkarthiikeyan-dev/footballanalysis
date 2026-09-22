# Limitations

Honest list of what this project does not do, and why.

## Data coverage

- **No player-level data before 2019/20.** The vaastav/FPL archive has
  `players_raw.csv` back to 2016/17, but no matching `teams.csv` for
  2016/17–2018/19, so player→team assignment can't be done reliably for
  those seasons. Rather than guess, they're excluded entirely.
- **No xG/xA before 2022/23.** Not tracked by the Fantasy Premier League
  game itself before roughly that point. Shown as `NULL`, never a
  fabricated `0`.
- **No advanced event data** (progressive passes, pressures, touches in
  box, shot maps). No free, reliable source covers this across the
  project's full historical range — would require a paid provider
  (Opta/StatsBomb-class) to do properly.
- **No penalties-scored breakout** — the source field isn't populated
  reliably enough across seasons to trust.

## League table tie-breaks

Ties are broken by points → goal difference → goals scored →
alphabetical, which matches the Premier League's real rule almost
always, but not every historical edge case (rare head-to-head or
play-off tie-breaks aren't modeled). No season in this dataset was
actually decided by such an edge case, so the computed tables match
real historical standings, but the tie-break logic itself is a
simplification worth knowing about.

## European Performance module

**Not yet built.** The project brief calls for a 20-club Champions
League comparison module; no Champions League match data has been
sourced or ingested yet. This is the largest remaining gap — see
`docs/PROJECT_PROGRESS.md` for the plan.

## Power BI

The data model and full DAX measure library are complete and
documented in `powerbi/`, but no `.pbix` file is included — Power BI
Desktop was not available in the environment this project was built
in. Opening the model in Desktop and wiring the documented
relationships takes about 10 minutes; see `powerbi/README.md`.

## Machine learning scope

Only one ML model is included (player similarity via KNN). The project
brief mentions clustering and broader "advanced analytics" — those
weren't added because they didn't have a clear, well-motivated question
to answer yet (per this project's own rule: don't add ML just to claim
"AI"). Candidates for a genuinely useful addition are listed in
`FUTURE_IMPROVEMENTS.md`.

## Testing scope

32 automated tests cover data quality, database integrity, analytics
correctness, and the ML module (all passing). The Streamlit app itself
was verified manually page-by-page in a live browser session (see
`docs/PROJECT_PROGRESS.md`), not via an automated UI test suite —
Playwright browser tests are not yet written.

## Documentation scope

The project brief calls for a full learning log and interview-prep
document covering ~25 topics in depth. What's included covers the
concepts actually used in this build; it is a solid starting point, not
the exhaustive version described in the original brief. See
`docs/learning/LEARNING_LOG.md` and `docs/learning/INTERVIEW_PREP.md`.

## Deployment

Documented for Streamlit Community Cloud (see README); not actually
deployed to a public URL as part of this build.
