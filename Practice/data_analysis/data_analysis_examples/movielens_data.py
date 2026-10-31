import pandas as pd

unames = ["user_id", "gender", "age", "occupation", "zip"]
users = pd.read_table(
    "datasets/movielens/users.dat",
    sep="::",
    header=None,
    names=unames,
    engine="python"
)

rnames = ["user_id", "movie_id", "rating", "timestamp"]
ratings = pd.read_table(
    "datasets/movielens/ratings.dat",
    sep="::",
    header=None,
    names=rnames,
    engine="python"
)

mnames = ["movie_id", "title", "genres"]
movies = pd.read_table(
    "datasets/movielens/movies.dat",
    sep="::",
    header=None,
    names=mnames,
    engine="python"
)


#merge datasets

data = pd.merge(
    pd.merge(ratings, users),
    movies
)


#calculate movie ratings

mean_ratings = data.pivot_table(
    "rating",
    index="title",
    columns="gender",
    aggfunc="mean"
)

#Find movies with enough ratings

ratings_by_title = data.groupby("title").size()

active_titles = ratings_by_title.index[
    ratings_by_title >= 250
]

mean_ratings = mean_ratings.loc[active_titles]


#Find movies with the highest rating differences

mean_ratings["diff"] = (
    mean_ratings["M"] - mean_ratings["F"]
)

sorted_by_diff = mean_ratings.sort_values("diff")