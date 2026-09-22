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

Built and tested (real Champions League data, 20 clubs, 2012/13–2025/26).
Specific limitations of this module:

- **Source is community-maintained, not an official UEFA feed.** The
  openfootball/champions-league archive is public-domain and sourced
  primarily from Wikipedia (per its own `NOTES.md`). Every final in the
  dataset was checked against independently known real results as
  part of building this module, but the source isn't an official
  competition data provider.
- **Cross-era progression comparisons aren't perfectly apples-to-apples.**
  The competition format changed from a traditional 8-group stage
  (2012/13–2023/24) to a 36-team "Swiss model" league phase plus a
  playoff round (2024/25+). Both are mapped onto one 1–7 progression
  scale for comparability, but "reaching the knockout stage" meant a
  different level of difficulty under each format.
- **No player-level European statistics** — the source is match-level
  only; there's no Champions League equivalent of the Player Explorer.
- **European H2H is scoped to the 20 selected clubs.** Meetings against
  clubs outside that list are covered by each club's "opponent
  history" instead, using the opponent's raw source name (not
  canonicalized, since building a full canonical mapping for every
  club that's ever played in the Champions League was out of scope).
- **Win/draw/loss counts each match leg individually** by its own
  on-pitch result, matching standard competition-statistics
  convention — a team can record a "win" in a leg of a tie it later
  lost on aggregate or penalties. See `docs/methodology/METHODOLOGY.md`.

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
