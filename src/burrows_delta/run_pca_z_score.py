import os

import pandas as pd
import matplotlib.pyplot as plt

from faststylometry import Corpus
from sklearn.decomposition import PCA
from faststylometry import tokenise_remove_pronouns_en
from faststylometry import calculate_burrows_delta
from faststylometry import predict_proba, calibrate


train_corpus = Corpus()
test_corpus = Corpus()

for author in os.listdir("dataset"):
    for i, book in enumerate(os.listdir(f"dataset/{author}")):
        with open(f"dataset/{author}/{book}", "r") as f:
            text = f.read()

        if "_delphi" in author or "interview_ai_career_journey" in book:
            test_corpus.add_book(author, book, text)
        elif i == 0:
            test_corpus.add_book(author, book, text)
        else:
            train_corpus.add_book(author, book, text)


train_corpus.tokenise(tokenise_remove_pronouns_en)
test_corpus.tokenise(tokenise_remove_pronouns_en)

burrows_delta = calculate_burrows_delta(train_corpus, test_corpus, vocab_size = 50)
print(burrows_delta)
burrows_delta.to_csv("output/burrows_delta.csv")

calibrate(train_corpus)

predictions = predict_proba(train_corpus, test_corpus)
print(predictions)
predictions.to_csv("output/burrows_delta_predictions.csv")


# -- Plot PCA of z-scores of test corpus --
split_test_corpus = test_corpus.split(80000)

calculate_burrows_delta(train_corpus, split_test_corpus)
z_scores = split_test_corpus.author_z_scores

pca_model = PCA(n_components=2)
pca_matrix = pca_model.fit_transform(z_scores.T)
authors = split_test_corpus.authors
df_pca_by_author = pd.DataFrame(pca_matrix)
df_pca_by_author["author"] = authors
plt.figure(figsize=(15,15))

for author, pca_coordinates in df_pca_by_author.groupby("author"):
    plt.scatter(*zip(*pca_coordinates.drop("author", axis=1).to_numpy()), label=author)
for i in range(len(pca_matrix)):
    plt.text(pca_matrix[i][0], pca_matrix[i][1],"  " + authors[i], alpha=0.5)

plt.legend()

plt.title("Representation using PCA of works in training corpus")
plt.show()


# -- Plot PCA of author-level proximity --
# Author-level proximity plot (aggregate chunks per author)
df_features = pd.DataFrame(z_scores.T)
df_features["author"] = authors

# Mean z-score vector per author (author centroids in feature space)
author_means = df_features.groupby("author").mean(numeric_only=True)

# Project author centroids using the same PCA model
author_pca = pca_model.transform(author_means.to_numpy())
df_author_pca = pd.DataFrame(author_pca, columns=["pc1", "pc2"])
df_author_pca["author"] = author_means.index.to_list()

plt.figure(figsize=(12, 12))

# Ensure base authors (with and without _delphi) share the same color
df_author_pca["base_author"] = df_author_pca["author"].str.replace(r"_delphi$", "", regex=True)
unique_bases = sorted(df_author_pca["base_author"].unique().tolist())
cmap = plt.get_cmap("tab20")
base_to_color = {ba: cmap(i % cmap.N) for i, ba in enumerate(unique_bases)}

for base_author, group in df_author_pca.groupby("base_author"):
    color = base_to_color[base_author]
    plt.scatter(group["pc1"], group["pc2"], s=20, c=[color], label=base_author)
    for _, row in group.iterrows():
        plt.text(row["pc1"], row["pc2"], "  " + row["author"], alpha=0.9, color=color)

plt.title("PCA of author centroids (closeness between authors)")
plt.xlabel("PC 1")
plt.ylabel("PC 2")
plt.grid(alpha=0.2)
plt.legend(title="Author", loc="best")
plt.show()
