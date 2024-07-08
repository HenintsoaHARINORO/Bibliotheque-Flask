import joblib
import pandas as pd
import re
import string
import spacy
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

file_path = 'script/Data/title_dataset.csv'
df = pd.read_csv(file_path)

# Load Spacy French model
spacy_nlp = spacy.load('fr_core_news_sm')


# Function for data cleaning and processing
def spacy_tokenizer_data(sentence):
    # Remove distracting single quotes
    sentence = re.sub('\'', '', sentence)
    # Remove digits and words containing digits
    sentence = re.sub('\w*\d\w*', '', sentence)
    # Replace extra spaces with single space
    sentence = re.sub(' +', ' ', sentence)
    # Remove unwanted lines starting from special characters
    sentence = re.sub(r'\n: \'\'.*', '', sentence)
    sentence = re.sub(r'\n!.*', '', sentence)
    sentence = re.sub(r'^:\'\'.*', '', sentence)
    # Remove non-breaking new line characters
    sentence = re.sub(r'\n', ' ', sentence)
    # Remove punctuations
    sentence = re.sub(r'[^\w\s]', ' ', sentence)
    # Create token object
    tokens = spacy_nlp(sentence)
    # Lower, strip, and lemmatize
    tokens = [word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens]
    # Remove stopwords and exclude words less than 2 characters
    tokens = [word for word in tokens if
              word not in spacy.lang.fr.stop_words.STOP_WORDS and word not in string.punctuation and len(word) > 2]
    return tokens

tokenizer = spacy_tokenizer_data
# Load tokenizer and model with error handling
try:
    with open('script/Checkpoint/tokenizer_spacy_66.pkl', 'wb') as file:
        joblib.dump(spacy_tokenizer_data, file)
    model = joblib.load('script/Checkpoint/model_mlp_66.pkl')
except Exception as e:
    print("Error loading tokenizer or model:", e)
    tokenizer = None
    model = None

label_mapping = dict(zip(df['labels'], df['classe']))


def predict_real_class(query_string):
    if not query_string:
        return None

    if tokenizer is None or model is None:
        print("Tokenizer or model is not loaded.")
        return None

    # Tokenize the query string using the loaded tokenizer
    query_tokens = tokenizer(query_string)

    # Convert tokens to a string
    query_string = ' '.join(query_tokens)

    # Predict the label for the query
    predicted_label = model.predict([query_string])[0]

    # Map the predicted numerical label to the real class name
    real_class = label_mapping.get(predicted_label)

    return real_class

""" 
# Example usage:
query = "electrique"
real_class = predict_real_class(query)
print("Real Class:", real_class)"""
