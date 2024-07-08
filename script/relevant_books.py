import pickle
import spacy
import string
import re
from gensim import corpora
from gensim.models import TfidfModel, LsiModel
from gensim.similarities import Similarity
import pandas as pd

# Load the dictionary
dictionary = corpora.Dictionary.load('script/Checkpoint/dictionary.gensim')

# Load the TF-IDF model
data_tfidf_model = TfidfModel.load('script/Checkpoint/data_tfidf_model.gensim')

# Load the LSI model
data_lsi_model = LsiModel.load('script/Checkpoint/data_lsi_model.gensim')

# Load the stop words list and punctuations
with open('script/Checkpoint/stop_words.pkl', 'rb') as f:
    stop_words = set(pickle.load(f))

with open('script/Checkpoint/punctuations.pkl', 'rb') as f:
    punctuations = pickle.load(f)

# Load Spacy NLP model
spacy_nlp = spacy.load('fr_core_news_md')

# Recreate the tokenizer function
def spacy_tokenizer(sentence):
    sentence = re.sub('\'','',sentence)
    sentence = re.sub('\w*\d\w*','',sentence)
    sentence = re.sub(' +',' ',sentence)
    sentence = re.sub(r'\n: \'\'.*','',sentence)
    sentence = re.sub(r'\n!.*','',sentence)
    sentence = re.sub(r'^:\'\'.*','',sentence)
    sentence = re.sub(r'\n',' ',sentence)
    sentence = re.sub(r'[^\w\s]',' ',sentence)
    tokens = spacy_nlp(sentence)
    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens]
    tokens = [word for word in tokens if word not in stop_words and word not in punctuations and len(word) > 2]
    return tokens

# Load your DataFrame
file_path = 'script/Data/final_cleaned_data_column_stop_words.csv'
df = pd.read_csv(file_path)

# Create the similarity index
corpus = corpora.MmCorpus('script/Checkpoint/data_lsi_model_mm')
data_index = Similarity('script/BibliothèqueFlask', corpus, num_features=corpus.num_terms)
from operator import itemgetter

def get_relevant_books(query, num_best=5):
    query_bow = dictionary.doc2bow(spacy_tokenizer(query))
    query_tfidf = data_tfidf_model[query_bow]
    query_lsi = data_lsi_model[query_tfidf]
    data_index.num_best = num_best
    movies_list = data_index[query_lsi]
    movies_list.sort(key=itemgetter(1), reverse=True)
    filenames = []

    for j, movie in enumerate(movies_list):
        movie_index = movie[0]
        if movie_index in df.index:
            filenames.append(df['Filename'][movie_index])
        else:
            print(f"Index {movie_index} is out of bounds for the DataFrame")
        if j == (data_index.num_best - 1):
            break

    return filenames
# Test the function
""" 
result = get_relevant_books("architecture ")
print(result)"""
