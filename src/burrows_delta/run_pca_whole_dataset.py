import os
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from faststylometry import tokenise_remove_pronouns_en

# PCA on the whole dataset (no train/test split)
# Build a document-term matrix from all texts after tokenization, then apply PCA
all_tokens = []
all_authors = []
all_titles = []

for author in os.listdir("dataset"):
    for book in os.listdir(f"dataset/{author}"):
        with open(f"dataset/{author}/{book}", "r") as f:
            text = f.read()
        tokens = tokenise_remove_pronouns_en(text)
        all_tokens.append(tokens)
        all_authors.append(author)
        all_titles.append(book)

vectorizer = CountVectorizer(
    analyzer=lambda x: x,
    preprocessor=lambda x: x,
    tokenizer=None,
    token_pattern=None,
    max_features=1000
)
X = vectorizer.fit_transform(all_tokens).toarray()

pca_model = PCA(n_components=2)
pca_matrix = pca_model.fit_transform(X)

df_pca_by_author = pd.DataFrame(pca_matrix, columns=["PC1", "PC2"])
df_pca_by_author["author"] = all_authors

plt.figure(figsize=(15,15))
for author, pca_coordinates in df_pca_by_author.groupby("author"):
    plt.scatter(*zip(*pca_coordinates[["PC1", "PC2"]].to_numpy()), label=author)
for i in range(len(pca_matrix)):
    plt.text(pca_matrix[i][0], pca_matrix[i][1], "  " + all_titles[i], alpha=0.5)

plt.legend()
plt.title("PCA of all documents (no train/test split)")
plt.show()
