# Requires transformers>=4.51.0
# Requires sentence-transformers>=2.7.0
import os
import umap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from sentence_transformers import SentenceTransformer


"""
This show that simple embedding will care more about the content of the text than the style of the author.
"""


model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"device_map": "cpu"},
    tokenizer_kwargs={"padding_side": "left"},
)

documents = []
labels = []  # author directory names, e.g., "dara", "thytu", "dara_delphi"

for author in sorted(os.listdir("dataset")):
    author_path = f"dataset/{author}"
    if not os.path.isdir(author_path):
        continue
    for book in sorted(os.listdir(author_path)):
        file_path = f"{author_path}/{book}"
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r") as f:
            text = f.read()
        documents.append(text)
        labels.append(author)


embeddings = []
for i in range(0, len(documents)):
    text = documents[i]
    embeddings.append(
        model.encode(text[: min(len(text), 1000)], prompt_name="query")
    )


all_embeddings = np.array(embeddings)

# Dimension reduction and clustering libraries
standard_embedding = umap.UMAP(random_state=42, n_neighbors=2).fit_transform(all_embeddings)

unique_labels = sorted(set(labels))
cmap = plt.cm.get_cmap('tab20', len(unique_labels))
label_to_color = {label: cmap(i) for i, label in enumerate(unique_labels)}
point_colors = [label_to_color[label] for label in labels]

plt.scatter(standard_embedding[:, 0], standard_embedding[:, 1], c=point_colors)

# Legend mapping colors to author names
handles = [mpatches.Patch(color=label_to_color[label], label=label) for label in unique_labels]
plt.legend(handles=handles, title="Author", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
