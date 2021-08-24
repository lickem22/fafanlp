#from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
#from transformers import pipeline
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer
tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())

def sentiment_analysis(documents,model,tokenizer):
    sentiments =[]
    nlp = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    for document in nlp(documents):
        score = dict(document)
        if score['score']<0.85:
            sentiments.append('NEUTRE')
        elif score['label']=='POSITIVE':
            sentiments.append('POSITIF')
        elif score['label']=='NEGATIVE':
            sentiments.append('NEGATIF')

    return sentiments
def sentiment_analysis2(documents):
    senti_list = []
    for i in documents:
        print(i)
        vs = tb(i).sentiment[0]
        print(vs)
        if (vs > 0):
            senti_list.append('POSITIVE')
        elif (vs < 0):
            senti_list.append('NEGATIVE')
        else:
            senti_list.append('NEUTRE')   
    return senti_list