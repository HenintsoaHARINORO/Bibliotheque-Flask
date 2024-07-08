import re
import PyPDF2
from nltk.tokenize import word_tokenize

import pandas as pd
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
import ssl
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from script.classify_title import predict_real_class
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the stopwords file
stopwords_file = os.path.join(script_dir, 'stopwords-fr.txt')
def sort_coo(coo_matrix):
    """Sort a dict with highest score"""
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def extract_title_and_author(pdf_file):
    text = extract_last_page_text(pdf_file)
    # Define regular expression patterns to extract title (Titre) and author (Auteur)
    titre_match = re.search(r'Titre\s*du\s*mémoire\s*:\s*«([^»]+)»', text, re.IGNORECASE)
    if not titre_match:
        titre_match = re.search(r'Titre\s*:\s*«([^»]+)»', text, re.IGNORECASE)
    if not titre_match:
        titre_match = re.search(r'Titre\s*:\s*(.+)', text, re.IGNORECASE)

    # Extract the title
    titre = titre_match.group(1).strip().replace('\n', ' ').replace('\r', '') if titre_match else None

    # Extract the author information
    auteur_match = re.search(r'Auteur\s*:\s*(.+)', text, re.IGNORECASE)
    if not auteur_match:
        # If "Auteur" is not found, try to extract "Nom" and "Prénoms"
        nom_match = re.search(r'Nom\s*:\s*(.+)', text, re.IGNORECASE)
        prenoms_match = re.search(r'Prénoms\s*:\s*(.+)', text, re.IGNORECASE)
        if nom_match and prenoms_match:
            nom = nom_match.group(1).strip()
            prenoms = prenoms_match.group(1).strip()
            auteur = f"{nom} {prenoms}"
        else:
            auteur = None
    else:
        auteur = auteur_match.group(1).strip()

    # Replace multiple spaces with a single space in the title
    titre = re.sub(r'\s+', ' ', titre) if titre else None

    return titre, auteur


def extract_topn_from_vector(feature_names, sorted_items, topn):
    """get the feature names and tf-idf score of top n items"""

    # use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    # word index and corresponding tf-idf score
    for idx, score in sorted_items:
        # keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    # create a tuples of feature, score
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]

    return results


def get_keywords(vectorizer, feature_names, doc):
    """Return top k keywords from a doc using TF-IDF method"""

    # generate tf-idf for the given document
    tf_idf_vector = vectorizer.transform([doc])

    # sort the tf-idf vectors by descending order of scores
    sorted_items = sort_coo(tf_idf_vector.tocoo())

    # extract only TOP_K_KEYWORDS
    keywords = extract_topn_from_vector(feature_names, sorted_items, TOP_K_KEYWORDS)

    return ' '.join(list(keywords.keys()))


PUNCTUATION = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
TOP_K_KEYWORDS = 50

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


# nltk.download('wordnet')


def extract_mention(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Extract text from the first page
        first_page_text = reader.pages[0].extract_text()

        # Split text into lines
        lines = first_page_text.split('\n')

        mention_line = None

        mention_started = False
        # Define keywords to search for (case-insensitive)
        keywords = ['mention', 'filière', 'département']

        # Regex pattern to capture information following keywords
        pattern = r'(?:' + '|'.join(keywords) + r')\s*:\s*(.*)'

        # Iterate through lines
        for line in lines:
            # Convert line to lowercase for case-insensitive matching
            line_lower = line.lower()

            # Check if any keyword is present in the lowercase line
            if any(keyword in line_lower for keyword in keywords):
                # Extract information using regex pattern
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    mention_line = match.group(1).strip()
                    mention_started = True  # Indicate that mention extraction has started
                else:
                    mention_started = False  # Reset if no valid match

            elif mention_started:
                # Check if the line contains "Parcours" (indicating end of mention)
                if 'parcours' in line_lower:
                    # Stop processing mention if "Parcours" is found
                    break
                else:
                    # Append this line to the existing mention text
                    mention_line += ' ' + line.strip()

        return mention_line


def extract_lines_with_keyword(pdf_file_path):
    # Open the PDF file
    keyword = "ECOLE"
    with open(pdf_file_path, 'rb') as pdf_file:
        # Create a PdfFileReader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the text from the first page
        first_page_text = pdf_reader.pages[0].extract_text()

        # Clean the text (remove non-word characters)
        cleaned_text = re.sub(r'[^\w\s\dÀ-ÿ]', '', first_page_text)

        # Split text into lines and remove empty lines
        cleaned_text_lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]

        # Filter lines containing the keyword
        lines_with_keyword = [line for line in cleaned_text_lines if keyword.lower() in line.lower()]

        # Join filtered lines into a single string
        extracted_text = '\n'.join(lines_with_keyword)

        return extracted_text


def extract_university_from_pdf(pdf_file_path):
    # Open the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        # Create a PdfFileReader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the first page
        first_page_text = pdf_reader.pages[0].extract_text()

        # Search for the word "université" and everything after it in the same line
        match = re.search(r'UNIVERSITE.*', first_page_text, re.IGNORECASE)
        if match:
            return match.group(0)
        else:
            return None


def extract_parcours(pdf_file_path):
    # Open the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        # Create a PdfFileReader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the text from the first page
        first_page_text = pdf_reader.pages[0].extract_text()

        # Define a regular expression pattern to match "parcours" followed by optional colon
        pattern = r'(?i)\bparcours\b\s*:?\s*(.*)'

        # Search for the pattern in the text
        match = re.search(pattern, first_page_text)

        if match:
            # Get the extracted text after the matched pattern
            extracted_text = match.group(1).strip()
            return extracted_text

    return None


def extract_date(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf = PyPDF2.PdfReader(pdf_file)
        first_page_text = pdf.pages[0].extract_text()
        # Regular expression pattern to match French date format
        date_pattern = (r'\b(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre'
                        r'|décembre)\s+\d{4})\b')
        match = re.search(date_pattern, first_page_text, re.IGNORECASE)
        if match:
            matched_date_str = match.group(0)
            return matched_date_str
        else:
            return None  # Return None if no date is found


def extract_name(pdf_file_path):
    # Open the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        # Create a PdfFileReader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from the first page (page index 0)
        first_page_text = pdf_reader.pages[0].extract_text()

        # Define regular expression patterns to capture different presenter information
        presenter_patterns = [
            r'(Présenté\s+par)\s*:?([^\n]*)',
            r'(Réalisé\s+par)\s*:?([^\n]*)',
            r'(Présenté\s+et\s+soutenu\s+par)\s*:?([^\n]*)'
        ]

        # Iterate through presenter patterns
        for pattern in presenter_patterns:
            presented_by_match = re.search(pattern, first_page_text, re.IGNORECASE)
            if presented_by_match:
                # Extract the text following the matched pattern
                presented_by_info = presented_by_match.group(2).strip()

                # If the extracted text is empty or contains only whitespace characters,
                # try to find the next non-empty line
                if not presented_by_info:
                    lines = first_page_text.split('\n')
                    found_presented_by = False

                    for line in lines:
                        if re.search(pattern, line, re.IGNORECASE):
                            found_presented_by = True
                        elif found_presented_by:
                            cleaned_line = line.strip()
                            if cleaned_line:
                                return cleaned_line

                return presented_by_info.strip()

    return None


def extract_title_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        first_page_text = PyPDF2.PdfReader(pdf_file).pages[0].extract_text()
        title_pattern_1 = r'Intitulé\s*:\s*«\s*(.*?)\s*»'
        title_pattern_2 = r'Intitulé\s*:\s*(.*?)\s*Présenté'
        title_match_1 = re.search(title_pattern_1, first_page_text, re.IGNORECASE | re.DOTALL)
        title_match_2 = re.search(title_pattern_2, first_page_text, re.IGNORECASE | re.DOTALL)
        title = title_match_1.group(1).strip() if title_match_1 else (
            title_match_2.group(1).strip() if title_match_2 else None)
        return re.sub(r'\s+', ' ', title) if title else None


def extract_last_page_text(pdf_file):
    """
    Extract text from the last page of a PDF file.
    """
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        last_page_text = reader.pages[num_pages - 1].extract_text()
        return last_page_text.strip()


def clean_text(text):
    """Text cleaning function"""
    if text is None:
        return ""
    # Convert text to lowercase
    text = text.lower()

    # Remove Roman numerals
    text = re.sub(r'\b[ivxlcdm]+\b', '', text)

    # Remove special characters and extra spaces, preserving accents
    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', text)

    # Tokenize the text
    tokens = word_tokenize(text)

    # Load French stopwords
    with open(stopwords_file, 'r') as f:
        french_stopwords = set(f.read().splitlines())

    # Remove stopwords and tokens containing digits
    filtered_tokens = [word for word in tokens if word not in french_stopwords and not word.isdigit()]

    # Join the filtered tokens back into a single string
    cleaned_text = ' '.join(filtered_tokens)

    return cleaned_text


def clean_whole_text(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdfReader = PyPDF2.PdfReader(file)
        num_pages = len(pdfReader.pages)
        cleaned_texts = []
        text = ""
        # Extract text from each page
        for page_num in range(num_pages):
            pageObj = pdfReader.pages[page_num]
            page_text = pageObj.extract_text()
            if page_text:
                text += page_text

        # Clean the extracted text
        cleaned_text = clean_text(text)
        cleaned_texts.append(cleaned_text)
        return cleaned_texts


french_lemmatizer = FrenchLefffLemmatizer(with_additional_file=False)


def clean_and_lemmatize(text):
    lemmatized_text = [french_lemmatizer.lemmatize(word.lower()) for word in text.split()]
    return ' '.join(lemmatized_text)


def clean_with_lemmatizer(text):
    return clean_and_lemmatize(text)


model_dbow = joblib.load('script/Checkpoint/model_dbow_78.pkl')
log_reg_classifier = joblib.load('script/Checkpoint/best_logreg_78.pkl')


# Function to preprocess new data and infer document vectors
def preprocess_and_infer_doc_vectors(new_data, model):
    if isinstance(new_data, str):
        # If new_data is a single string (single document), convert it to a list
        new_data = [new_data]
    document_vectors = [model.infer_vector(doc.split()) for doc in new_data]
    return document_vectors


def extract_pdf_content(pdf_path):
    """
    Extract resume paragraph, abstract, keywords, and mots clés from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        tuple: Tuple containing (resume, abstract, keywords, mots_clés).
    """
    # Call the function to extract text from the last page of the PDF
    text = extract_last_page_text(pdf_path)

    # Define patterns for extracting resume paragraphs
    resume_patterns = [
        r'RESUME\s*([\s\S]+?)(?:ABSTRACT|Mots clés|$)',
        r'Résumé\s*([\s\S]+?)(?:ABSTRACT|Mots clés|$)',
        r'Résumé\s*([\s\S]+?)(?:ABSTRACT|Mots clés|$)',
        r'RÉSUM É\s*([\s\S]+?)(?:ABSTRACT|Mots clés|$)'
    ]

    # Try each pattern to extract the resume paragraph
    resume_paragraph = None
    for pattern in resume_patterns:
        resume_match = re.search(pattern, text, re.IGNORECASE)
        if resume_match:
            resume_paragraph = resume_match.group(1).strip()
            break

    # Extract abstract, keywords, and mots clés
    abstract_match = re.search(r'ABSTRACT\s*([\s\S]+?)(?:Keywords|Mots clés|$)', text, re.IGNORECASE)
    keywords_match = re.search(r'Keywords:\s*([\s\S]+?)(?:Auteur|Mots clés|$)', text)
    mots_clés_match = re.search(r'Mots clés\s*:\s*([\s\S]+?)\n', text)

    # Prepare extracted content
    extracted_resume = resume_paragraph if resume_paragraph else None
    extracted_abstract = abstract_match.group(1).strip() if abstract_match else None
    extracted_keywords = keywords_match.group(1).strip() if keywords_match else None
    extracted_mots_clés = mots_clés_match.group(1).strip() if mots_clés_match else None

    return extracted_resume, extracted_abstract, extracted_keywords, extracted_mots_clés


def extract_and_predict(pdf_file_path):
    # Create a DataFrame to store extracted information
    data = pd.DataFrame(
        columns=['Filename', 'University', 'ecole', 'mention', 'parcours', 'date', 'name', 'titre', 'Résumé',
                 'Abstract', 'keywords', 'Mots clés', 'Cleaned Text', 'Top Keywords', 'Data'])

    # Extract and clean text from the PDF
    cleaned_texts = clean_whole_text(pdf_file_path)

    # Assign cleaned text to the DataFrame
    data['Cleaned Text'] = cleaned_texts

    # Lemmatize the text
    data['Cleaned Text'] = data['Cleaned Text'].apply(lambda x: clean_with_lemmatizer(x) if pd.notnull(x) else '')

    # Extract other information from the PDF
    university = extract_university_from_pdf(pdf_file_path)
    ecole = extract_lines_with_keyword(pdf_file_path)
    mention = extract_mention(pdf_file_path)
    parcours = extract_parcours(pdf_file_path)
    date = extract_date(pdf_file_path)

    title, name = extract_title_and_author(pdf_file_path)
    resume, abstract, keywords, mots_clés = extract_pdf_content(pdf_file_path)
    resume = clean_text(resume)
    resume = clean_with_lemmatizer(resume) if pd.notnull(resume) else ''

    # Write extracted information to the DataFrame
    data.loc[0] = [os.path.basename(pdf_file_path), university, ecole, mention, parcours, date, name, title,
                   resume, abstract, keywords, mots_clés,
                   data['Cleaned Text'].iloc[0], None, None]

    # Initialize and fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(smooth_idf=True, use_idf=True)
    vectorizer.fit_transform(data['Cleaned Text'].to_list())
    feature_names = vectorizer.get_feature_names_out()

    # Write top keywords to the DataFrame
    top_keywords = get_keywords(vectorizer, feature_names, data['Cleaned Text'].iloc[0])
    data.at[0, 'Top Keywords'] = top_keywords

    # Concatenate résumé, mots clés, and top keywords
    data['Data'] = data[['Résumé', 'Mots clés', 'Top Keywords']].fillna('').agg(' '.join, axis=1)

    # Preprocess the new data and infer document vectors
    new_data_vectors = preprocess_and_infer_doc_vectors(data['Data'], model_dbow)

    # Predict the classes
    predicted_classes = log_reg_classifier.predict(new_data_vectors)

    # Map predicted classes to their corresponding labels
    mapping_df = pd.read_excel('script/unique_mentions_per_class.xlsx', header=None)
    mapping_dict = {row[0]: row[1] for row in mapping_df.values}
    mapped_classes = [mapping_dict[pred_class] for pred_class in predicted_classes]

    # Convert data to strings
    date_str = str(date)
    title_str = str(title)
    name_str = str(name)
    university_str = str(university)
    ecole_str = str(ecole)
    mapped_classes_str = str(mapped_classes[0])
    theme = str(predict_real_class(title_str))
    return {
        "date": date_str,
        "title": title_str,
        "name": name_str,
        "university": university_str,
        "ecole": ecole_str,
        "mapped_classes": mapped_classes_str,
        "theme": theme
    }


""" 
# Call the function with the PDF file path
pdf_file_path = '/Users/henintsoa/PycharmProjects/BibliothèqueFlask/uploads/AdrisoaEddyM_ESPA_LIC_2016.pdf'
extracted_data, predicted_classes = extract_and_predict(pdf_file_path)

# Print the extracted data and predicted classes
print("Extracted Data:")
print(extracted_data)
print("Predicted Classes:")
print(predicted_classes)"""
