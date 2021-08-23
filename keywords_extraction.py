from sklearn.feature_extraction.text import CountVectorizer
#import nltk
import joblib
from fastapi import HTTPException

from sklearn.feature_extraction.text import TfidfTransformer
from rake_nltk import Rake
#from stop_words import get_stop_words
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
import yake

PATH_TFIDF = 'models/tfidf/'
PATH_KC = 'models/keywords-candidates/'
PATH_CV='models/count-vectorizer/'

def train_tfidf(documents,ngram_range=(1,2),name_tfidf='tf_idf.pkl',name_cv='cv.pkl',name_candidates = 'candidates.pkl'):
    stopwords = nltk.corpus.stopwords.words('french')
    count =  CountVectorizer(ngram_range=ngram_range,max_df=0.85,stop_words=stopwords).fit(documents)
    word_count_vector = count.fit_transform(documents)
    candidates = count.get_feature_names()
    tfidf_transformer = TfidfTransformer(smooth_idf= True,use_idf = True)
    #fit
    tfidf_transformer.fit(word_count_vector)
    #save
    joblib.dump(tfidf_transformer, PATH_TFIDF+name_tfidf)
    joblib.dump(count,PATH_CV+name_cv)
    joblib.dump(candidates,PATH_KC+name_candidates)
    return tfidf_transformer

'''
    Functions to get keywords
'''
def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

def extract_from_vector(feature_names, sorted_items, topn=10):
    """get the feature names and tf-idf score of top n items"""

    #use only topn items from vector
    sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    for idx, score in sorted_items:
        fname = feature_names[idx]

        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]

    return results

'''
    Get keywords
'''
def get_keywords(documents,n_keywords=10,name_tfidf='tfidf.pkl',name_cv='cv.pkl',name_candidates = 'cv.pkl'):
    keywords_list = []
    tfidf = joblib.load(PATH_TFIDF+name_tfidf)
    count = joblib.load(PATH_CV+name_cv)
    candidates = joblib.load(PATH_KC+name_candidates)
    #generate tf-idf for the given document
    for doc in documents:
        tf_idf_vector = tfidf.transform(count.transform([doc]))

        sorted_items = sort_coo(tf_idf_vector.tocoo())

        sorted_items = sort_coo(tf_idf_vector.tocoo())
        keywords = extract_from_vector(candidates,sorted_items,n_keywords)
        keywords_list.append(keywords)

    return keywords_list
def extract_keywords(documents):
    #french_stopwords = get_stop_words('fr')
    r = Rake(language='french',stopwords = fr_stop)
    keywords = []
    if isinstance(documents, list):
        for  document in documents:
            if isinstance(document, str):
                r.extract_keywords_from_text(document)

                keywords.append(r.get_ranked_phrases())
            else:
                return ({'error':' Du texte est requis'})
    else:
        return ({'error':'Type list requis'})

        
    return keywords

def extract_keywords2(documents,nb_keywords=5):
    extractor = yake.KeywordExtractor()
    language = "fr"
    max_ngram_size = 2
    deduplication_threshold = 0.9
    keywords_lst = []
    if isinstance(documents, list):
        for  document in documents:
            if isinstance(document, str) and len(document.split())>2:
                custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=nb_keywords, features=None)
                keywords = custom_kw_extractor.extract_keywords(document)
                keywords_lst.append([keyword[0] for keyword in keywords])
            elif len(document.split())<=2 :
                keywords_lst.append([])
                #raise HTTPException(status_code = ,detail ="Each text should have more than "
    else:
        raise HTTPException(status_code = 404,detail ="Type list required")
    return keywords_lst


