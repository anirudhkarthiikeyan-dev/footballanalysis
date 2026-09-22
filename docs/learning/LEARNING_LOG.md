# Learning Log

Each entry: what it means, why this project uses it, exactly where in
this codebase, what you should understand, a concrete example from this
build, an interview question, and a one-paragraph way to explain it in
an interview. This covers the concepts actually used in PL Intelligence
— see `FUTURE_IMPROVEMENTS.md` for expanding this to the full topic list.

---

## Python (pandas / NumPy)

**What it means:** Python is the glue language here; pandas gives
tabular data structures (DataFrames) and vectorized operations; NumPy
underlies pandas' numeric computation.

**Why used:** every stage of the pipeline — ingestion, cleaning,
analytics — is pandas transformations on DataFrames, not row-by-row
Python loops (except where a calculation genuinely needs per-row logic,
e.g. `home_away_split`).

**Where:** `src/cleaning/clean_matches.py`, `src/analytics/*.py`.

**What to understand:** vectorized operations (`df["col"] = df["a"] - df["b"]`)
are far faster than `.apply()` with a Python function, which is in turn
faster than a manual `for` loop — because vectorized ops run in
compiled C, not the Python interpreter, per row.

**Example from this project:** `league_table.py` computes `goals_for`,
`goals_against`, `points` for a whole season's table using
`.sum()` and boolean masks (`home["result"] == "H"`), not a loop over
each team.

**Interview question:** "Why is `df.apply(lambda...)` often slower than
a direct vectorized pandas operation?"

**How to explain it:** `.apply()` calls a Python function once per row
(or column), paying Python's interpreter overhead every time. A
vectorized op like `df["a"] - df["b"]` runs as a single compiled
operation over the whole underlying NumPy array — no per-row Python
call at all.

---

## Data cleaning & entity resolution

**What it means:** turning inconsistent, messy raw data into a single
trustworthy table — including resolving the same real-world entity
written differently across sources.

**Why used:** football-data.co.uk calls a club `"Man United"`; the FPL
archive calls it `"Man Utd"`. Without resolving these to one canonical
name, the same club would silently split into two "different" teams in
every aggregation.

**Where:** `data/external/team_master.csv` (the mapping table),
`src/cleaning/clean_matches.py` and `clean_players.py` (where it's applied).

**What to understand:** entity resolution needs a source of truth
(here, a hand-built canonical list) and an explicit failure mode for
unmapped values — this project's cleaning scripts `raise ValueError` on
any unmapped team name rather than silently dropping or guessing it.

**Example from this project:** adding `Sheffield Utd -> Sheffield United`
to `team_master.csv` after the pipeline raised exactly that error on a
previously-unseen FPL team-name string.

**Interview question:** "How do you handle the same entity being
represented differently across two data sources?"

**How to explain it:** build one canonical reference table mapping
every known raw variant to a single canonical identity, and make the
pipeline fail loudly (not silently drop or guess) when it meets a
variant that isn't in the mapping yet — that's what surfaced the
`Sheffield Utd` gap in this project.

---

## SQL / SQLite & star schema

**What it means:** SQLite is a real embedded SQL database; a star
schema organizes data into fact tables (events/measurements) surrounded
by dimension tables (descriptive context) joined on surrogate keys.

**Why used:** the analytical questions this project answers (league
tables, H2H, trends) are naturally SQL aggregations, and a star schema
is the same shape both SQL and Power BI expect.

**Where:** `database/schema.sql`, `src/transformation/build_database.py`.

**What to understand:** `FACT_MATCH` (grain: one row per match) is
different from `FACT_TEAM_SEASON` (grain: one row per team per season)
— mixing grains in one query (e.g. summing `FACT_MATCH.home_goals`
alongside `FACT_TEAM_SEASON.points` without a proper join) double-counts
or produces nonsense.

**Example from this project:** `tests/test_database.py::test_leicester_2015_16_title`
runs a real SQL join across `fact_team_season`, `dim_team`, `dim_season`
and checks the result against a known real fact.

**Interview question:** "What's the difference between a fact table and
a dimension table, and why does grain matter?"

**How to explain it:** a fact table stores measurable events at one
specific level of detail (its "grain") — e.g. one row per match. A
dimension table stores descriptive attributes you filter/group by (team
name, season label). Getting the grain wrong — joining two facts at
different grains without an intermediate aggregation — silently
multiplies or undercounts rows.

---

## Data validation

**What it means:** automated, explicit checks that data meets known
invariants, run as code (not eyeballed) so a bad pipeline run fails
loudly instead of silently producing wrong numbers downstream.

**Why used:** a subtle bug (e.g. mis-parsed date, wrong team mapping)
should break a test, not surface three pages later as a wrong chart.

**Where:** `src/validation/validate_matches.py`, `tests/test_data_quality.py`.

**What to understand:** validation checks two different things —
*structural* invariants (no duplicate match_id, every season has 20
teams) and *logical* invariants (the `result` column must agree with
the actual goal columns).

**Example from this project:** `test_result_consistent_with_goals`
recomputes `H`/`D`/`A` from `home_goals`/`away_goals` and asserts it
matches the source's own `result` column — catching any pipeline bug
that could desync the two.

**Interview question:** "How do you know your cleaned data is actually
correct, not just 'runs without errors'?"

**How to explain it:** "runs without errors" only proves the code
didn't crash. Correctness needs assertions against known invariants
(row counts, uniqueness, cross-column consistency) and, where possible,
against independently known ground truth — this project checks its
computed 2015/16 league table against the real historical result.

---

## Statistics: per-90 rates and percentiles

**What it means:** per-90 normalizes a counting stat (goals) by playing
time so a player with 900 minutes isn't unfairly compared to one with
3,000. A percentile says what fraction of a comparison group a value
beats.

**Why used:** raw goal totals conflate "good at scoring" with "played a
lot" — per-90 separates those.

**Where:** `src/analytics/player_stats.py`.

**What to understand:** percentiles are only meaningful within a
comparable cohort — this project always scopes them to the same season
+ position, and only above a minutes threshold, to avoid comparing a
forward to a defender or crowning a 2-game hot streak as "elite."

**Example from this project:** `percentile_rank()` filters to
`season == X and position == Y and minutes >= 450` before ranking —
removing any of those three filters would produce a misleading number.

**Interview question:** "Why not just rank players by raw goal count?"

**How to explain it:** raw totals are biased by playing time and role —
per-90 controls for minutes, and scoping percentiles to the same
season+position cohort controls for the fact a forward and a
center-back have completely different expected output.

---

## Machine learning: k-nearest neighbors for similarity

**What it means:** KNN finds the k data points closest to a query point
in feature space, under a chosen distance metric.

**Why ML is appropriate here:** comparing four correlated per-90 stats
at once needs a genuine multi-dimensional distance calculation — not
something a `WHERE` clause or a single `ORDER BY` can express.

**Where:** `src/ml/player_similarity.py`.

**What to understand:** features must be standardized
(`StandardScaler`) before computing distance, or a feature with larger
raw units (goals, typically 0–30) silently dominates one with smaller
units (assists) — this is one of the most common practical ML mistakes.

**Example from this project:** `find_similar_players("Erling Haaland", "2022/23")`
returns a plausible list of high-output forwards by standardized
goals/assists/xG/xA — not just "other players who also scored a lot."

**Interview question:** "Why do you need to normalize features before
KNN, and what happens if you don't?"

**How to explain it:** KNN's distance calculation treats every feature
as directly comparable numbers. Without scaling, a feature with a
larger numeric range (goals: 0-36) dominates the distance regardless of
its actual importance, effectively ignoring smaller-range features like
assists. `StandardScaler` puts every feature on the same footing
(zero mean, unit variance) before distance is computed.

---

## Data visualization (Plotly) & dashboard design

**What it means:** choosing a chart type and encoding that makes the
underlying pattern legible, not just "a chart."

**Why used:** every chart in this app answers a specific question
(e.g. "has scoring gone up or down over 14 seasons?" → a line chart
with a clear trend, not a table of 14 numbers).

**Where:** `app/pages/2_League_Trends.py`, `app/pages/4_Head_to_Head.py`.

**What to understand:** a stacked bar (home/draw/away % by season) is
the right choice when parts must sum to a meaningful whole (100%); a
line chart is right for a trend over time; a radar chart is right for
comparing a fixed small set of normalized dimensions (percentile
profile) — using the wrong one for the data shape actively misleads.

**Interview question:** "How do you choose a chart type?"

**How to explain it:** start from the question, not the data. "How has
X changed over time" → line/area. "How do parts make up a whole" →
stacked bar or pie (sparingly). "How do multiple entities compare
across several normalized dimensions" → radar. Then design for the
chart to be readable at a glance, not decorative.

---

## Power BI & DAX

**What it means:** Power BI is a BI tool that loads tables into an
in-memory model and computes measures with DAX (Data Analysis
Expressions) — a formula language built around filter context.

**Why used:** to demonstrate the BI-tool side of analytics (star-schema
modeling, measures, relationships) alongside the custom Streamlit product.

**Where:** `powerbi/` (model exports + `dax/measures.dax`).

**What to understand:** a DAX measure isn't computed once — it's
re-evaluated for every cell of a visual, in that cell's *filter
context* (whatever slicers/rows/columns are active). `SUM(fact_team_season[points])`
returns a different number in a "by season" table than in a "by team"
table, because the filter context differs, even though it's the same
one-line formula.

**Interview question:** "What's 'filter context' in DAX, and why does
it matter?"

**How to explain it:** filter context is the set of filters (from
slicers, visual rows/columns, and any `CALCULATE` wrapping) active when
a measure is evaluated. The same measure formula produces different
results depending on what's filtered — that's what makes one DAX
measure reusable across many visuals instead of writing a new
calculation per chart.

---

## Streamlit

**What it means:** a Python framework that turns a script into a web
app, re-running top-to-bottom on every interaction.

**Why used:** to ship the custom analytics product without writing
separate frontend/backend code.

**Where:** `app/Home.py`, `app/pages/*.py`.

**What to understand:** because Streamlit re-runs the whole script on
every widget interaction, expensive work (loading CSVs, hitting the DB)
must be wrapped in `@st.cache_data`/`@st.cache_resource` or it re-runs
needlessly on every click — see `app/components/data.py`.

**Interview question:** "How does Streamlit's execution model differ
from a traditional web app, and what does that mean for performance?"

**How to explain it:** Streamlit has no persistent server-side request
handlers — every interaction re-executes the script from the top. That
makes the code simple (linear, no callback wiring) but means anything
expensive must be explicitly cached, or it recomputes on every click.

---

## Git / GitHub

**What it means:** version control and a hosting platform for
collaborating on and publishing code.

**Why used:** standard practice for any real software project; also
how this project is intended to be shared as a portfolio piece.

**What to understand:** `.gitignore` here deliberately excludes
regenerable derived data (`data/raw/`, `data/processed/`,
`database/*.db`) — not because it's sensitive, but because it's large,
regenerable from committed scripts, and (for the raw source data) not
this project's to redistribute.

**Interview question:** "What do you decide to `.gitignore`, and why?"

**How to explain it:** anything regenerable from source (build
artifacts, downloaded/derived data, compiled files) and anything that
shouldn't be redistributed (large raw datasets with unclear licensing,
secrets) — commit the code that produces it, not the output itself.

---

## Parsing semi-structured text data

**What it means:** turning a human-readable but not machine-structured
text format (not CSV, not JSON — a text listing with indentation and
inline annotations meant to be readable) into a clean, tabular dataset.

**Why used:** the Champions League source data
(openfootball/champions-league) is published as a `football.txt`-format
text listing — real, verified data, but not structured like the CSV
sources used elsewhere in this project.

**Where:** `src/cleaning/clean_european.py`.

**What to understand:** semi-structured text needs a *stateful* parser,
not a single regex — you track context line by line (current stage,
current date) and apply different regexes for different line types
(stage headers start with "▪", date lines match a weekday+month
pattern, match lines have team names and a score expression). Getting
the *score expression* right required understanding the domain first:
`"3-4 pen. 1-1 a.e.t. (1-1, 0-1)"` needs football knowledge (penalty
shootouts aren't goals) to parse correctly, not just regex skill.

**Example from this project:** the parser self-validates by comparing
its own parsed match count against each source file's own declared
`"# Matches NNN"` header — a cheap, source-provided ground truth that
catches parser bugs immediately rather than downstream.

**Interview question:** "How do you validate a parser you wrote for a
format you don't control?"

**How to explain it:** where the source provides any independently
computable check (a declared row count, a checksum, a known total),
use it as an automated assertion rather than trusting that "it ran
without errors" means it parsed correctly. Where the source doesn't
provide that, validate against external ground truth you can verify
independently — this project checked every parsed Champions League
final against real, well-known historical results.

---

## Handling format drift within one data source

**What it means:** a single source's structure can change over time
(a competition reformats, a schema evolves) — a robust pipeline
normalizes those variants to one consistent shape rather than assuming
the format is static.

**Why used:** the Champions League changed formats partway through this
project's date range — an 8-group stage (2012/13–2023/24) became a
36-team "Swiss model" league phase (2024/25+), with different stage
names in the source text (`"Group A"` vs `"League, Matchday 3"`) and an
extra round (`"Playoffs"`) that didn't exist before. The source even
contains a literal spelling inconsistency (`"Gruppe G"`/`"Gruppe H"`,
German for "Group", for three consecutive seasons).

**Where:** `src/cleaning/clean_european.py::normalize_stage`,
`src/analytics/european.py` (the 1–7 progression scale).

**What to understand:** normalizing format drift is a modeling choice
with a real tradeoff, not a free win — collapsing "8-group stage" and
"36-team league phase" onto the same "tier 1" of a progression scale
makes cross-era comparison *possible*, but the two formats aren't
equally difficult to advance from, and that limitation has to be
documented, not hidden by the normalization.

**Example from this project:** `docs/methodology/METHODOLOGY.md` and
`LIMITATIONS.md` both explicitly flag this — normalizing data for
comparability doesn't mean claiming the comparison is perfect.

**Interview question:** "What do you do when a data source's schema
changes partway through the history you're analyzing?"

**How to explain it:** normalize to one consistent representation so
downstream code and analysis doesn't need to special-case every era,
but document exactly what the normalization glosses over — silently
normalizing away a real structural difference is how misleading
comparisons happen.

---

## Extending a schema without forking it

**What it means:** when a new feature needs new fact tables, deciding
whether to extend existing dimension tables or create parallel ones.

**Why used:** the European Performance module needed 11 clubs that
aren't in the Premier League — the question was whether to give them a
separate `dim_team_european` or add them to the existing `dim_team`.

**Where:** `src/transformation/build_database.py` — `dim_team` is built
from the *union* of every canonical name in `team_master.csv`, so
adding the 11 new clubs there was enough; no schema change to
`dim_team` itself was needed, and `fact_european_match` /
`fact_club_season_europe` reference the exact same `team_id` values
the Premier League fact tables use.

**What to understand:** this is what makes cross-domain analysis
(Domestic vs Europe) possible without a manual join or name-matching
step at query time — Manchester City has exactly one `team_id`, shared
across every fact table it appears in. A parallel dimension table would
have needed a separate mapping layer to compare the two.

**Interview question:** "When would you add rows to an existing
dimension table versus create a new one?"

**How to explain it:** if the new entities are the same *kind* of
thing the dimension already models (here: football clubs) and might
need to be joined against the same facts or compared across domains,
extend the existing dimension. Create a new one when the entities are
genuinely a different kind of thing, or when the join patterns never
overlap.

---

## End-to-end architecture / data storytelling

**What it means:** designing the whole pipeline — source to
insight — as one coherent, reproducible system, and presenting findings
in a way a non-technical audience can trust and act on.

**Why used:** the whole point of this project is demonstrating the
full workflow, not an isolated notebook analysis.

**What to understand:** "data storytelling" isn't decoration — it's
being explicit about what a number does and doesn't mean (see the
Methodology page's coverage notes) so a reader doesn't over-trust a
metric that has real gaps (e.g. no xG before 2022/23).

**Interview question:** "Walk me through this project end to end."

**How to explain it:** see `INTERVIEW_PREP.md` for the full 60-second /
3-minute / technical versions of this answer.
