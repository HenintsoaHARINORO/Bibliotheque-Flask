import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def find_top_filenames(query):
    # Load embeddings
    loaded_embeddings = np.load('script/Checkpoint/embeddings (1).npy')

    # Load dataframe
    df = pd.read_csv("script/Data/final_cleaned_data_column_stop_words.csv")

    # Preprocess query
    query = query.lower()

    # Load model
    model = SentenceTransformer("script/distiluse-base-multilingual-cased-v1_local_model")

    # Encode input text
    input_text_embedding = model.encode(query)
    input_text_embedding = np.round(input_text_embedding, 5)

    # Compute similarities
    similarities = cosine_similarity([input_text_embedding], loaded_embeddings)
    similarity_scores = similarities[0]

    # Create dataframe with similarity scores
    thesis_df_similarity = df.copy()
    thesis_df_similarity["Similarity"] = similarity_scores
    thesis_df_similarity = thesis_df_similarity.sort_values(by='Similarity', ascending=False).reset_index(drop=True)

    # Select top similar items
    top_similar_items = thesis_df_similarity[["titre", "name", "mention", "parcours", "Similarity"]].head(5)

    # Find filenames corresponding to top similar items
    filenames = []
    for index, row in top_similar_items.iterrows():
        if pd.notnull(row["titre"]) and pd.notnull(row["name"]) and pd.notnull(row["mention"]) and pd.notnull(
                row["parcours"]):
            filename = df[(df["titre"] == row["titre"]) &
                          (df["name"] == row["name"]) &
                          (df["mention"] == row["mention"]) &
                          (df["parcours"] == row["parcours"])]["Filename"].values[0]
            filenames.append(filename)

    return filenames


""" 
# Example usage:
query = "densification télécommunication"
top_filenames = find_top_filenames(query)
print(top_filenames)"""
