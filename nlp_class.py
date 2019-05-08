from bs4 import BeautifulSoup
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


class NLP_Feature_Engineer_():
    def __init__(self):
        self.all_descrips = None

    def get_text(self, soup):
        return [p.text.replace('\xa0', '') for p in soup.find_all('p') if p.text.replace('\xa0', '') != '']

    def get_description_string_(self, df):
        # turn html into soup opject for parsing
        df['soups'] = df.description.apply(lambda x: BeautifulSoup(x, features="lxml") )
        
        # get all the text out of each description
        df.soups = df.soups.apply(lambda x: self.get_text(x))
        
        # turn description into one long string
        all_descriptions = df.soups.apply(lambda x: ''.join(x))
        
        self.all_descrips = all_descriptions

    def fit_transform(self, df):
        self.get_description_string_(df)
        tfidf = TfidfVectorizer(stop_words='english')
        vecs = tfidf.fit_transform(self.all_descrips)
        vec_arr = vecs.toarray()
        
        decomp = TruncatedSVD(n_components=100)
        lsaX = decomp.fit_transform(vec_arr)
        
        return lsaX

    