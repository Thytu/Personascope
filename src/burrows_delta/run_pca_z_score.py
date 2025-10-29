import os

from faststylometry import Corpus
from faststylometry import tokenise_remove_pronouns_en
from faststylometry import calculate_burrows_delta
from faststylometry import predict_proba, calibrate


train_corpus = Corpus()
test_corpus = Corpus()

for author in os.listdir("dataset"):
    for i, book in enumerate(os.listdir(f"dataset/{author}")):
        with open(f"dataset/{author}/{book}", "r") as f:
            text = f.read()

        if i == 0:
            test_corpus.add_book(author, book, text)
        else:
            train_corpus.add_book(author, book, text)


train_corpus.tokenise(tokenise_remove_pronouns_en)
test_corpus.tokenise(tokenise_remove_pronouns_en)

print(calculate_burrows_delta(train_corpus, test_corpus, vocab_size = 50))

calibrate(train_corpus)
print(predict_proba(train_corpus, test_corpus))




import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import pandas as pd

split_test_corpus = test_corpus.split(80000)

df_delta = calculate_burrows_delta(train_corpus, split_test_corpus)
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
