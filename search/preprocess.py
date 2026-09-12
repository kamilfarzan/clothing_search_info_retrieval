import re
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')

def preprocess(text: str | list) -> list:
    # lowercase, remove punctuation, tokenize, stemming, stopword policy
    if isinstance(text, list):
        text = " ".join(text)

    # lowercase
    text = text.lower()

    # remove punctuation using regex
    text = re.sub(r"[^\w\s]", '', text) # \w means any word (alphanumeric + _); \s means any whitespace character (except space)

    # tokenize
    tokens = word_tokenize(text)

    # stopword policy
    stopword_set = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stopword_set]

    # stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]

    return stemmed_tokens