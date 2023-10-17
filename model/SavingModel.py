from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_score(emb1, emb2):
    embeddings = np.array([emb1, emb2])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100
    # print(f"q1: {q1},\n q2: {q2},\n emb1: {embeddings_dict[q1][ind]},\n emb2: {embeddings_dict[q1][ind]},\n score: {score}\n\n")
    return score

dir_path = 'mpnet/'
sentences = ["This is an example sentence", "Each sentence is converted"]
#
# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
# embeddings = model.encode(sentences)

model = SentenceTransformer(dir_path)
embeddings = model.encode(sentences)

# model.save(dir_path)

print(get_score(embeddings[0], embeddings[1]))
