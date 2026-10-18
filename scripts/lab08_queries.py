import pandas as pd
from inf8239_u03.config import MOVIELENS_DIR
from inf8239_u03.data import load_movielens
from inf8239_u03.recommenders import ContentRecommender

QUERIES = ["Toy Story (1995)", "Pulp Fiction (1994)", "Alien (1979)", "Schindler's List (1993)"]
_, movies = load_movielens(MOVIELENS_DIR)
model = ContentRecommender().fit(movies)
frames = []
for title in QUERIES:
    genres = movies.loc[movies["title"] == title, "genres"].iloc[0]
    print(f"\n{title}  [{genres}]")
    rec = model.recommend(title, 10)
    print(rec[["title", "genres", "content_score"]].to_string(index=False))
    frames.append(rec.assign(query=title))
pd.concat(frames).to_csv("reports/content_queries.csv", index=False, encoding="utf-8")
