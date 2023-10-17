import json, time

from . import db
import pandas as pd
from model import embeddings as emb


def get_similar(input_question, percentage, n=3):
    start_time = time.time()
    q_df = db.get_df()
    print(f"q_df len = {len(q_df)}\n")

    emb_df = db.get_df("QEmbeddings")
    print(f"emb_df len = {len(emb_df)}\n")
    similarity_df = pd.DataFrame()
    # print("TYPE EMBS: ", type(json.loads(emb_df["Embeddings"][1])))
    similarity_df[['Question', 'Answer', 'link']] = q_df[['Question', 'Answer', 'link']]
    input_embedding = emb.get_embeddings(input_question)
    similarity_df["cosine_similarity"] = (emb_df["Embeddings"]
                                          .apply(lambda db_emb: emb.get_emb_score(json.loads(db_emb), input_embedding)))
    similarity_df = similarity_df.sort_values(by='cosine_similarity', ascending=False)
    if percentage != 'none':
        mask = similarity_df['cosine_similarity'] >= int(percentage)
        first_n = similarity_df[mask].head(n)
    else:
        first_n = similarity_df.head(n)
    print(f"Processing Time: {time.time()- start_time} seconds")
    return first_n

