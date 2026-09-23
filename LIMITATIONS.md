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

## Power BI — descoped, not a limitation of the current product

Power BI was explored during development (a real star-schema export
and a 48-measure DAX library were built, and the model was opened and
wired successfully in Power BI Desktop) and then intentionally dropped
in favor of a single, finished Streamlit dashboard rather than two
partial ones. The exploration is preserved unedited in
`_archive_old/powerbi_exploration/` for reference, but it is not part
of the product — nothing in this repo requires Power BI to run, and no
Power BI experience is claimed beyond what's actually there (a data
model export + written, unexecuted-until-descoping DAX). See
`docs/PROJECT_PROGRESS.md` for the decision and date.

## Machine learning scope

Only one ML model is included (player similarity via KNN). The project
brief mentions clustering and broader "advanced analytics" — those
weren't added because they didn't have a clear, well-motivated question
to answer yet (per this project's own rule: don't add ML just to claim
"AI"). Candidates for a genuinely useful addition are listed in
`FUTURE_IMPROVEMENTS.md`.

## Testing scope

57 fast unit/data/database/analytics tests (`tests/`) — 100% reliable,
verified passing repeatedly across sessions with zero flakes.

41 Playwright browser tests (`tests/ui/` — every page loads, no
console/network errors, no horizontal overflow, filters actually
change real data, navigation and the intro's Enter/Skip both work).
This suite is correct (every individual test passes reliably when run
in isolation, and every failure it's ever produced was root-caused to
a real, now-fixed issue — see `docs/learning/LEARNING_LOG.md`'s
Playwright entry) but it is **not currently rock-solid under repeated
back-to-back execution** on a shared, general-purpose machine: running
it 5 times in a row in one session produced results ranging from
41/41 to 34/41, with a different subset failing each time, consistent
with system resource contention rather than an application defect (see
`docs/PROJECT_PROGRESS.md` for the investigation). Treat a single
Playwright run's result as informative, not as an absolute pass/fail
gate the way the fast suite is — see `FUTURE_IMPROVEMENTS.md`.

The Playwright suite is separate and slower (launches a real Streamlit
server and headless Chromium) — see README for how to run it. It does
not run automatically with the fast `pytest tests/` command; run it
explicitly with `pytest tests/ui/`.

## Documentation scope

The project brief calls for a full learning log and interview-prep
document covering ~25 topics in depth. What's included covers the
concepts actually used in this build; it is a solid starting point, not
the exhaustive version described in the original brief. See
`docs/learning/LEARNING_LOG.md` and `docs/learning/INTERVIEW_PREP.md`.

## Deployment

Documented for Streamlit Community Cloud (see README); not actually
deployed to a public URL as part of this build.
