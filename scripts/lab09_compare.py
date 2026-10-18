"""LAB09 · Comparación de popularidad, contenido, colaborativo e híbrido.

Script propuesto por la IA para ampliar lab09_hybrid.py (que solo evalúa el híbrido).
Corte temporal leave-one-out del proyecto; métricas: RMSE, HitRate@K, cobertura, costo.
Salidas en reports/: lab09_comparison.csv, lab09_summary.csv, lab09_profiles.csv,
lab09_diagnostics.json.
"""
from __future__ import annotations

import argparse
import json
from itertools import islice
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.metrics import catalog_coverage, hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--seeds", type=int, nargs="+", default=[42, 7, 123])
parser.add_argument("--factors", type=int, default=20)
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--alphas", type=float, nargs="+", default=[0.25, 0.75])
parser.add_argument("--k", type=int, default=10)
parser.add_argument("--max-users", type=int, default=None, help="solo para pruebas rápidas")
args = parser.parse_args()
K = args.k
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)


def norm01(values: np.ndarray) -> np.ndarray:
    return (values - values.min()) / max(values.max() - values.min(), 1e-9)


ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)

# ---- diagnóstico del corte temporal ----
train_last = train.groupby("userId")["timestamp"].max()
test_ts = test.groupby("userId")["timestamp"].min()
same_ts = int((train_last.reindex(test_ts.index) >= test_ts).sum())
strict_users = set(test_ts.index[train_last.reindex(test_ts.index) < test_ts])

# ---- catálogo y contenido ----
movie_table = movies.reset_index(drop=True).copy()
movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
item_ids = movie_table["movieId"].to_numpy()
movie_row = {int(m): i for i, m in enumerate(item_ids)}
titles = movie_table.set_index("movieId")["title"]


def content_sims(history: pd.DataFrame) -> np.ndarray | None:
    known = history[history["movieId"].isin(movie_row.keys())]
    if known.empty:
        return None
    rows = [movie_row[int(m)] for m in known["movieId"]]
    weights = np.clip(known["rating"].to_numpy() - 2.5, 0.1, None)
    profile = np.asarray(genre_matrix[rows].multiply(weights[:, None]).sum(axis=0)) / weights.sum()
    return cosine_similarity(profile, genre_matrix).ravel()


# ---- popularidad (conteo y luego media, igual que lab09_hybrid.py) ----
popular = train.groupby("movieId")["rating"].agg(["mean", "count"]).sort_values(
    ["count", "mean"], ascending=False)
popular_items = popular.index.tolist()

# ---- RMSE de baselines ----
global_mean = float(train["rating"].mean())
item_mean = train.groupby("movieId")["rating"].mean()

seen_by_user = train.groupby("userId")["movieId"].apply(set).to_dict()
hist_by_user = {u: g for u, g in train.groupby("userId")}

rows_out: list[dict] = []
first_recs: dict[str, dict[int, list[int]]] = {}
diagnostics: dict = {}

for seed_pos, seed in enumerate(args.seeds):
    start = perf_counter()
    model = MatrixFactorization(factors=args.factors, seed=seed).fit(train, epochs=args.epochs)
    train_seconds = perf_counter() - start

    model_items = set(int(i) for i in model.items)
    evaluable = test[test["userId"].isin(model.user_index) & test["movieId"].isin(model.item_index)]
    if args.max_users:
        keep = evaluable["userId"].unique()[: args.max_users]
        evaluable = evaluable[evaluable["userId"].isin(keep)]
    users = evaluable["userId"].unique().tolist()

    preds = [model.predict(r.userId, r.movieId) for r in evaluable.itertuples()]
    rmse_mf = float(root_mean_squared_error(evaluable["rating"], preds))
    rmse_global = float(root_mean_squared_error(evaluable["rating"], [global_mean] * len(evaluable)))
    rmse_item = float(root_mean_squared_error(
        evaluable["rating"], evaluable["movieId"].map(item_mean).fillna(global_mean)))

    recs: dict[str, dict[int, list[int]]] = {
        "popularidad": {}, "contenido": {}, "colaborativo": {},
        **{f"hibrido_a{a}": {} for a in args.alphas}}
    t_pop = t_con = t_col = 0.0
    random_expected = []
    skipped = 0
    for user_id in users:
        seen = seen_by_user[user_id]
        random_expected.append(K / max(len(model_items - seen), 1))

        t0 = perf_counter()
        recs["popularidad"][user_id] = list(islice((i for i in popular_items if i not in seen), K))
        t_pop += perf_counter() - t0

        t0 = perf_counter()
        sims = content_sims(hist_by_user[user_id])
        if sims is not None:
            masked = sims.copy()
            masked[np.isin(item_ids, list(seen)) | ~np.isin(item_ids, list(model_items))] = -np.inf
            recs["contenido"][user_id] = item_ids[np.argsort(-masked, kind="stable")[:K]].astype(int).tolist()
        t_con += perf_counter() - t0

        t0 = perf_counter()
        collab = model.top_n(user_id, seen, 100)
        if collab.empty or sims is None:
            skipped += 1
            t_col += perf_counter() - t0
            continue
        ids = collab["movieId"].to_numpy().astype(int)
        score = collab["collaborative_score"].to_numpy()
        recs["colaborativo"][user_id] = ids[np.argsort(-score, kind="stable")[:K]].tolist()
        normalized = norm01(score)
        content = norm01(sims[[movie_row[int(i)] for i in ids]])
        for a in args.alphas:
            hybrid = a * normalized + (1 - a) * content
            recs[f"hibrido_a{a}"][user_id] = ids[np.argsort(-hybrid, kind="stable")[:K]].tolist()
        t_col += perf_counter() - t0

    costs = {"popularidad": t_pop, "contenido": t_con}
    for name in recs:
        if name.startswith(("colaborativo", "hibrido")):
            costs[name] = train_seconds + t_col
    for name, per_user in recs.items():
        truth = evaluable[evaluable["userId"].isin(per_user)]
        strict = {u: v for u, v in per_user.items() if u in strict_users}
        rows_out.append({
            "seed": seed, "method": name,
            "hit_rate_at_10": hit_rate_at_k(per_user, truth, K),
            "hit_rate_strict": hit_rate_at_k(strict, truth[truth["userId"].isin(strict_users)], K),
            "catalog_coverage": catalog_coverage(per_user, len(model.items)),
            "users_evaluated": len(per_user),
            "cost_seconds": costs[name],
            "rmse": rmse_mf if name.startswith(("colaborativo", "hibrido")) else np.nan,
        })
    rows_out.append({"seed": seed, "method": "azar_esperado",
                     "hit_rate_at_10": float(np.mean(random_expected)), "hit_rate_strict": np.nan,
                     "catalog_coverage": np.nan,
                     "users_evaluated": len(users), "cost_seconds": 0.0, "rmse": np.nan})
    if seed_pos == 0:
        first_recs = recs
        first_users = users
        first_evaluable = evaluable
        diagnostics.update({
            "test_rows": int(len(test)), "evaluable_rows": int(len(evaluable)),
            "users_skipped_hybrid": skipped,
            "rmse_global_mean": rmse_global, "rmse_item_mean": rmse_item, "rmse_mf_seed_first": rmse_mf})
    print(f"semilla {seed}: entrenamiento {train_seconds:.1f} s, usuarios {len(users)}", flush=True)

# ---- resumen y Pareto ----
comparison = pd.DataFrame(rows_out)
summary = comparison.groupby("method").agg(
    hit_rate_mean=("hit_rate_at_10", "mean"), hit_rate_std=("hit_rate_at_10", "std"),
    hit_rate_strict_mean=("hit_rate_strict", "mean"),
    coverage_mean=("catalog_coverage", "mean"), cost_seconds_mean=("cost_seconds", "mean"),
    rmse_mean=("rmse", "mean"), rmse_std=("rmse", "std")).reset_index()
real = summary[summary["method"] != "azar_esperado"]


def dominated(row) -> bool:
    better = real[(real["hit_rate_mean"] >= row.hit_rate_mean) & (real["coverage_mean"] >= row.coverage_mean)
                  & (real["cost_seconds_mean"] <= row.cost_seconds_mean)]
    strict = better[(better["hit_rate_mean"] > row.hit_rate_mean) | (better["coverage_mean"] > row.coverage_mean)
                    | (better["cost_seconds_mean"] < row.cost_seconds_mean)]
    return len(strict) > 0


summary["pareto"] = [(m != "azar_esperado") and not dominated(r) for m, r in
                     zip(summary["method"], summary.itertuples())]
comparison.to_csv(REPORTS / "lab09_comparison.csv", index=False)
summary.to_csv(REPORTS / "lab09_summary.csv", index=False)

# ---- perfiles: historial amplio, historial corto, historial mínimo simulado, usuario nuevo ----
n_train = {u: len(seen_by_user[u]) for u in first_users}
broad, small = max(n_train, key=n_train.get), min(n_train, key=n_train.get)
truth_item = first_evaluable.set_index("userId")["movieId"].to_dict()


def show(ids) -> str:
    return " | ".join(str(titles.get(int(i), i)) for i in ids)


profile_rows = []
for label, u in [("historial amplio", broad), ("historial corto", small)]:
    for name, per_user in first_recs.items():
        if u in per_user:
            profile_rows.append({"profile": label, "userId": u, "n_train": n_train[u], "method": name,
                                 "top10": show(per_user[u]), "held_out": titles.get(truth_item[u]),
                                 "hit": int(truth_item[u] in per_user[u])})
first3 = hist_by_user[broad].sort_values("timestamp").head(3)
sims3 = content_sims(first3)
if sims3 is not None:
    masked = sims3.copy()
    masked[np.isin(item_ids, first3["movieId"].to_numpy())] = -np.inf
    profile_rows.append({"profile": "historial mínimo (3 valoraciones simuladas)", "userId": broad,
                         "n_train": 3, "method": "contenido",
                         "top10": show(item_ids[np.argsort(-masked, kind="stable")[:K]]),
                         "held_out": "", "hit": ""})
profile_rows.append({"profile": "usuario nuevo (sin historial)", "userId": int(ratings["userId"].max()) + 1,
                     "n_train": 0, "method": "popularidad (respaldo)",
                     "top10": show(popular_items[:K]), "held_out": "", "hit": ""})
pd.DataFrame(profile_rows).to_csv(REPORTS / "lab09_profiles.csv", index=False, encoding="utf-8")

diagnostics.update({
    "args": vars(args), "users_with_heldout_not_after_last_train_timestamp": same_ts,
    "users_with_strictly_later_heldout": len(strict_users),
    "users_total": int(ratings["userId"].nunique())})
(REPORTS / "lab09_diagnostics.json").write_text(
    json.dumps(diagnostics, indent=2, default=float), encoding="utf-8")

pd.set_option("display.width", 200)
print(summary.round(4).to_string(index=False))
print(json.dumps(diagnostics, indent=2, default=float))
