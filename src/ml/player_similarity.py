"""Player similarity model.

Question answered: "which outfield players had a statistically similar
per-90 production profile in a given season?"

Why ML is appropriate: similarity across several correlated per-90 rate
stats isn't something a single sort or filter can answer — it needs a
distance metric over a multi-dimensional feature space, which is exactly
what k-nearest-neighbors gives us.

Data: fact_player_season (2019/20-2025/26), outfield players only
(goalkeepers excluded — their defining stats, saves and goals conceded,
aren't comparable to outfield production and would need a separate model).

Features (all per-90, so playing time doesn't bias the comparison):
  goals_per_90, assists_per_90, xg_per_90, xa_per_90
xG/xA are only available 2022/23 onward, so similarity search is
restricted to seasons where all four features exist — mixing seasons
with and without xG would silently zero-fill the missing half and bias
every distance calculation, so we don't.

Normalization: StandardScaler (zero mean, unit variance) per feature,
fit on the search cohort (same season, minutes >= threshold) — without
this, goals (typically 0-30) would dominate assists/xA (typically
smaller ranges) purely from having larger raw units.

Distance metric: Euclidean distance on standardized features, which is
what scikit-learn's NearestNeighbors uses by default and is equivalent
to a fixed-weight cosine-style comparison once features are standardized.

Limitations: no positional sub-role awareness (a standardized striker
and standardized winger with similar output can look "similar" here
even if their in-game role differs), no minutes-weighting beyond the
cutoff, and small cohorts (e.g. few FWDs with 900+ minutes in one
season) can make neighbors feel like a small pool.
"""
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

FEATURES = ["goals_per_90", "assists_per_90", "xg_per_90", "xa_per_90"]
MIN_SEASON_FOR_SIMILARITY = "2022/23"  # first season with xG/xA
MIN_MINUTES = 450


def _prep_cohort(players_per90: pd.DataFrame, season: str, position: str | None = None) -> pd.DataFrame:
    df = players_per90[
        (players_per90["season"] == season)
        & (players_per90["minutes"] >= MIN_MINUTES)
        & (players_per90["position"] != "GK")
    ].dropna(subset=FEATURES).copy()
    if position:
        df = df[df["position"] == position]
    return df.reset_index(drop=True)


def find_similar_players(players_per90: pd.DataFrame, player_name: str, season: str,
                          same_position_only: bool = True, top_n: int = 8) -> pd.DataFrame:
    target_row = players_per90[(players_per90["player_name"] == player_name) & (players_per90["season"] == season)]
    if target_row.empty:
        return pd.DataFrame()
    target_position = target_row.iloc[0]["position"] if same_position_only else None

    cohort = _prep_cohort(players_per90, season, target_position)
    if player_name not in cohort["player_name"].values or len(cohort) < 2:
        return pd.DataFrame()

    scaler = StandardScaler()
    X = scaler.fit_transform(cohort[FEATURES])

    k = min(top_n + 1, len(cohort))
    model = NearestNeighbors(n_neighbors=k, metric="euclidean")
    model.fit(X)

    target_idx = cohort.index[cohort["player_name"] == player_name][0]
    distances, indices = model.kneighbors(X[[target_idx]])

    result = cohort.iloc[indices[0]].copy()
    result["similarity_distance"] = distances[0]
    result = result[result["player_name"] != player_name]
    return result[["player_name", "team", "position"] + FEATURES + ["similarity_distance"]].reset_index(drop=True)
