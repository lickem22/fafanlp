#from server import new_keywords
from preprocessing import preprocessing_french2
import numpy as np 
import pandas as pd
import json
from keywords_extraction import extract_keywords2
from sentiment_analysis import sentiment_analysis

'''
get the data in a json format for keyboard extraction. 
'''
#keywords
def keywords_count(keywords,isKeyword = False):
    if isKeyword:
        #transform to numpy array
        x = np.array(keywords)
        data = dict({})
        labels = []
        counts = []
        #unique_list = 
        #get each keyword
        for item in np.unique(x):
            count = keywords.count(item)
            if count >1:
                labels.append(item)
                counts.append(count)
                #data[item] = count
        #add to dictionaany
        data["labels"] = labels
        data["counts"] = counts
       #print(data["count"])
       #get dataframe from dict
        df = pd.DataFrame.from_dict(data)
       
        #sort by count of keywords, descending order
        df = df.sort_values(by=['counts'],ascending=False)
        return json.dumps(df.to_dict('list'))
        #return 0
    else:
        #preprocess data
        preprocessed = preprocessing_french2(keywords)
        #
        #print(extract_keywords2(preprocessed))
        #get keywords add all to the same array
        raw_data = sum(extract_keywords2(preprocessed),[])
        data = keywords_count(raw_data,True)
        return json.dumps(data)
        

#sentiments

def sentiments_count(array,model,tokenizer,isSentiment=False):
    if isSentiment:
        x = np.array(array)
        data = dict({})
        labels = []
        counts=[]
        #unique_list = 
        for item in np.unique(x):
            counts.append(array.count(item))
            labels.append(item)
        data["labels"] = labels
        data["counts"] = counts
        return json.dumps(data)
    else:
        data = sentiments_count(sentiment_analysis(array,model,tokenizer),model,tokenizer,True)
        return json.dumps(data)