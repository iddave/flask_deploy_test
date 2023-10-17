from model import embeddings as emb
from sentence_transformers import SentenceTransformer
from flaskr import db
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# mpnet_path = "C:/Users/Администратор/PycharmProjects/flask_test/model/mpnet"
# model = SentenceTransformer(mpnet_path)

sentences = ["This is an example sentence", "Each sentence is converted"]
# print(emb.get_score(sentences[0], sentences[1]))
# print(emb.get_embeddings(sentences[0]))


def get_similar(input_question, n = 3):
    q_df = db.get_df()
    emb_df = db.get_df("QEmbeddings")
    similarity_df = pd.DataFrame()
    print(type(emb_df["Embeddings"][1]))
    # similarity_df["cosine_similarity"] = emb_df["Embeddings"].apply(lambda embeddings_json: emb.get_score)

get_similar("some qqqqq")