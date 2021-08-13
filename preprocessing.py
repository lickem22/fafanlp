# Libraries
import os
import glob
import nltk
import string
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
#from gensim.models.phrases import Phrases, Phraser
#initialise phraser
#et phrases
    #pass
#phraser = melusine.nlp_tools.Phraser()
#phraser.train(df)
'''
    arguments:
        listofSentence: corpus (list of sentences)

'''

def preprocessing_french(listofSentence,phraser_path ='models/phraser.pkl') :
    stopwords = nltk.corpus.stopwords.words('french')
    mots = set(line.strip() for line in open('./dictionnaire.txt',encoding="utf8"))
    lemmatizer = FrenchLefffLemmatizer()
    preprocess_list = []
    for sentence in listofSentence :
        #words without punctuation and with lowercase only
        sentence_w_punct = "".join([i.lower() for i in sentence if i not in string.punctuation])

        #get rid of digits
        sentence_w_num = ''.join(i for i in sentence_w_punct if not i.isdigit())

        #tokenize sentence
        tokenize_sentence = nltk.tokenize.word_tokenize(sentence_w_num)

        #Remove stopwords
        words_w_stopwords = [i for i in tokenize_sentence if i not in stopwords]

        words_lemmatize = (lemmatizer.lemmatize(w) for w in words_w_stopwords)

        #lemmatize words: Only keep the root
        sentence_clean = ' '.join(w for w in words_lemmatize if w.lower() in mots or not w.isalpha())

        preprocess_list.append(sentence_clean)
        #phrase documents
        #processed_text = phrase_documents(preprocess_list,phraser_path)


    return preprocess_list
    '''
    The phraser will help to link words that have a meaning when used together
    (for example, New York will be New_York)
'''
def phrase_documents(documents,path='models/phraser.pkl'):
    bigram = Phraser.load(path)
    queries = bigram[documents]
    return queries

'''
        Train phraser

'''
def train_phraser(documents,save_path='models/phraser.pkl'):
    phrases = Phrases(documents, min_count=1, threshold=1)
    bigram = Phraser(phrases)
    bigram.save(save_path)
    return 0


'''
        save uploaded file to uploads 
        def save_file(file,company):
    filename = f'{dir_path}/uploads/{company}/{time.time()}-{file.filename}'
    f = open(f'{filename}', 'wb')
    content = await file.read()
    f.write(content)
    return filename

'''

