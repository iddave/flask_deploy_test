from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time
import os

current_dir = os.path.dirname(__file__)
mpnet_path = os.path.join(current_dir, "mpnet")
model = SentenceTransformer(mpnet_path)
# def get_embeddings(sentences):
#     embeddings = np.array(model.encode(sentences))
#     # print(f"embeddings: {embeddings}")
#     return embeddings


def get_embeddings(sentence):
    t0 = time.time()
    emb = model.encode(sentence).tolist()
    print(f"time for model encoding: {time.time() - t0}\n")
    return emb


def get_score(sent1, sent2):
    emb1 = np.array(get_embeddings(sent1))
    emb2 = np.array(get_embeddings(sent2))
    score = cosine_similarity([emb1], [emb2])[0][0] * 100
    # print(f"q1: {q1},\n q2: {q2},\n emb1: {embeddings_dict[q1][ind]},\n emb2: {embeddings_dict[q1][ind]},\n score: {score}\n\n")
    return score


def get_emb_score(emb1, emb2):
    emb1 = np.array(emb1)
    emb2 = np.array(emb2)
    score = cosine_similarity([emb1], [emb2])[0][0] * 100
    # print(f"q1: {q1},\n q2: {q2},\n emb1: {embeddings_dict[q1][ind]},\n emb2: {embeddings_dict[q1][ind]},\n score: {score}\n\n")
    return score
# e= get_score("That is a happy person", "Today is a sunny day")
# print(type(e),"\n", e)
