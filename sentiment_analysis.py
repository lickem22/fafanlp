from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline


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
