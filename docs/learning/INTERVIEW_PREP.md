# Interview Preparation

## Explain this project in 60 seconds

"PL Intelligence is an end-to-end Premier League analytics product I
built from scratch. I pulled real match data back to 2012/13 and player
data back to 2019/20 from public sources, built a cleaning and
validation pipeline that resolves inconsistent team names across
sources, loaded it into a star-schema SQLite database, and built an
analytics layer — league tables, head-to-head records, player
percentiles — that I checked against known real results, like
Leicester's 2015/16 title. On top of that I built a Streamlit product
with eleven pages — including global search — a k-nearest-neighbors
player similarity model, and a European Performance module comparing
20 major clubs' real Champions League record. Everything is tested —
98 passing tests, split between a fast unit/data/database suite and a
Playwright browser suite that drives the actual app."

## Explain this project in 3 minutes

Start with the 60-second version, then add:

"The interesting engineering problems were mostly about data honesty.
Two different sources call the same club different things — 'Man
United' versus 'Man Utd' — so I built a canonical team mapping and made
the pipeline fail loudly, not silently, on anything unmapped, which is
actually how I caught 'Sheffield Utd' as a gap during a real pipeline
run. The player data source only reliably covers 2019/20 onward, and
expected-goals data only exists from 2022/23 — rather than backfill
those gaps with fabricated numbers, I documented the coverage boundary
and scoped every feature that depends on it, like the similarity model,
to the seasons where the data is actually real.

For the similarity model, I used KNN over standardized per-90 stats —
goals, assists, xG, xA — because comparing four correlated rate stats
needs a real distance metric, not a sort. I made sure to exclude
goalkeepers, restrict comparisons to the same position by default, and
standardize features first, since without that, raw goal counts would
dominate the distance calculation purely from having a larger numeric
range than assists.

The whole thing is reproducible from source — every stage is a
standalone script, and the pipeline rebuilds the database byte-for-byte
from the same raw inputs."

## Explain this project technically

Pipeline: ingestion (raw data download) → cleaning (entity resolution,
date parsing, dedup) → validation (automated invariant checks) →
transformation (star-schema SQLite load) → analytics (pandas functions,
unit-tested) → one consumption layer (the Streamlit app, reading the
processed CSVs and the database directly). Grain discipline matters throughout: `FACT_MATCH` is one row
per match, `FACT_TEAM_SEASON` is one row per team per season — computed
from `FACT_MATCH`, not independently sourced, so the two can never
drift out of sync. The ML layer is a single, well-scoped KNN model with
an explicit question, feature list, normalization approach, and
documented limitations — not present to "check an AI box."

## Explain the biggest challenges

1. **Entity resolution across sources.** Solved with an explicit
   canonical mapping table and a pipeline that raises an error (not a
   silent drop) on anything unmapped.
2. **Deciding what NOT to show.** It would have been easy to backfill
   missing xG data with zeros or extrapolate player data into earlier
   seasons — resisting that in favor of documented coverage boundaries
   was a deliberate choice, not a limitation I ran out of time to fix.
3. **Knowing when to stop building.** I evaluated Power BI as a second
   consumption layer — built a real star-schema export and a
   48-measure DAX library, and confirmed it opened and wired correctly
   in Power BI Desktop — then made the call to drop it and finish one
   dashboard well instead of shipping two half-built ones. That's a
   real product decision, not a limitation I ran out of time on: the
   star schema was designed cleanly enough that adding a BI export back
   in later would be straightforward if it were ever worth it.

## Why did you evaluate Power BI, and why did you drop it?

To see whether a BI-tool consumption layer was worth adding alongside
the custom Streamlit app — star-schema modeling, relationships and DAX
measures are a different, industry-standard way of exposing the same
data model. I built the export and the DAX and confirmed the model
opened cleanly in Power BI Desktop. I dropped it because maintaining
two dashboard layers for a solo project split effort without adding
proportional value — the Streamlit app already covers everything the
Power BI pages would have, and finishing it to a high standard mattered
more than having two unfinished products. I don't claim Power BI
experience beyond what actually happened: a working data export and a
written, reviewed DAX library that I confirmed loads without error,
not a finished report.

## Why did you use Streamlit?

It let me ship a fully custom, interactive product — page-specific
layouts, a k-NN similarity search, a cinematic intro — without writing
separate frontend/backend code, appropriate for a solo portfolio build
where the goal is demonstrating the full analytics stack, not frontend
engineering.

## Why SQL?

The core analytical questions (standings, joins across teams/seasons,
aggregations) are naturally relational. A star schema in a real SQL
database keeps that relational structure explicit and testable — the
same shape a BI tool would expect, which is part of why the Power BI
evaluation was straightforward when I tried it (see "Why did you
evaluate Power BI, and why did you drop it?").

## Why Pandas?

Every cleaning and analytics step is a tabular transformation — pandas'
vectorized operations make that both concise and fast, and it's the
same DataFrame shape the entire Python data ecosystem (Streamlit,
scikit-learn, Plotly) expects.

## How did you validate your data?

Two layers: automated invariant checks (no duplicate matches, every
season has exactly 20 teams and 380 matches, result agrees with the
goal columns) run as pytest tests, plus spot-checks against independently
known real-world facts — e.g. the computed 2015/16 table matches
Leicester's actual title-winning record, and Haaland's 2022/23 season
matches his real 36-goal record.

## How did you handle missing data?

By scoping features to where the data actually exists rather than
filling gaps with invented values — player data starts at 2019/20,
advanced stats (xG/xA) start at 2022/23, and every page/doc that
depends on those states the boundary explicitly. A column that
genuinely has no value for a season is `NULL`, never a placeholder `0`.

## How does your H2H engine work?

`src/analytics/head_to_head.py` filters `FACT_MATCH`-equivalent data
to matches between two selected teams (in either home/away direction),
then computes wins/draws/losses from each team's perspective, home/away
splits, biggest-margin and highest-scoring meetings, and a frequency
count of a team's most common opponents — without labeling any pairing
a "rivalry" unless the data itself shows a real, frequent history.

## How does player similarity work?

See the ML section of `docs/learning/LEARNING_LOG.md` and
`docs/methodology/METHODOLOGY.md` — KNN over standardized per-90
features (goals, assists, xG, xA), restricted to seasons where all four
exist, outfield players only, with a minutes threshold to avoid
small-sample noise.

## How did you avoid data leakage?

The similarity model and percentiles are both computed within a single
season's data — no future-season information leaks into a given
season's comparison. There's no train/test split in this project
because there's no predictive model being evaluated (similarity search
is unsupervised nearest-neighbors, not a trained classifier/regressor);
the leakage risk that does apply — mixing seasons with and without
xG/xA — is explicitly guarded against by restricting the similarity
search to 2022/23+ only.

## How did you build the European Performance module?

I sourced real UEFA Champions League match data (2012/13–2025/26) from
a public-domain text archive, wrote a stateful parser for its
`football.txt` format (tracking stage and date context line by line,
since it isn't CSV), and filtered it to the 20 clubs named in the
brief. The interesting problems were: the competition's own format
changed partway through the range (an 8-group stage became a 36-team
"Swiss model" league phase in 2024/25), so I normalized both onto one
progression scale while documenting that they're not perfectly
equivalent in difficulty; and knockout ties decided by penalties needed
careful parsing to record real on-pitch goals separately from the
shootout score, since a penalty isn't a goal. I verified the whole
pipeline by checking every parsed final against independently known
real results — all 11 checkable finals matched exactly — and by
confirming clubs with limited Champions League history (Leicester City,
Aston Villa) only show their real, actual participation seasons, not a
fabricated full history.

## Why extend `dim_team` instead of creating a separate European table?

Because Manchester City, for example, needs to be the *same entity*
whether you're looking at its Premier League record or its Champions
League record — extending the existing dimension with the 11 new clubs
means every fact table shares one `team_id` per club, which is what
makes the Domestic vs Europe comparison page a simple filter-and-join
instead of a name-matching problem.

## What did testing catch during the European module build?

A real bug: I initially mapped only the "Manchester City FC" name
variant from the Champions League source to the canonical club, but
the source also uses plain "Manchester City" in many matches —
including a Champions League final. Without that second alias, those
matches were silently excluded from the filtered dataset (they didn't
error, they just vanished). A test checking the parsed data against
known finals caught the gap immediately, which is exactly why "runs
without errors" isn't the same as "correct" — I only found it because
I tested against ground truth I already knew, not because the code
complained.

## How did you test the UI, and what went wrong along the way?

I built a Playwright suite (`tests/ui/`, 41 tests) covering page loads,
navigation, filters, console errors and layout overflow, kept separate
from the fast unit suite since it launches a real server and browser.
Getting it reliable surfaced three real bugs, not test-writing
mistakes: Streamlit's persistent WebSocket means `networkidle` never
resolves, so I switched to explicit element waits; `st.dataframe`
renders through a canvas-based grid whose JS lazy-loads, so a fixed
delay before reading table content was a race I only caught by
checking canvas element counts directly; and one test's "did we
navigate" signal (`text=Team Explorer`) matched the sidebar link
present on *every* page, so it resolved before the real navigation
finished. Each was found with a small standalone script, not by
guessing and re-running the full suite.

## How would you scale this project?

More data: move from SQLite to Postgres, and from season-aggregate
player data to gameweek/event-level data (the FPL archive has this in
`gws/`). More competitions: add the European module using the same
star-schema pattern (`fact_european_match` at the same grain as
`FACT_MATCH`, joined to the same `dim_team`). More users: deploy the
Streamlit app behind a real hosting setup (Streamlit Community Cloud or
a container) with the database refreshed on a schedule rather than
rebuilt locally.
