import json
import os
import glob
import pandas as pd
from io import StringIO
from fastapi import HTTPException
from auth.auth_handler import decodeJWT
COLNAMES= ['text']
ERRORS_FRENCH = {"CSV invalide":["Le fichier csv ne doit contenir que des textes",
                                "Le fichier csv ne doit pas contenir plus d'une colonne "
                                ]}
'''
Check if a folder exists and create it if it doesn't
'''
def folder_exists(path):
    # You should change 'test' to your preferred folder.
    MYDIR = (path)
    CHECK_FOLDER = os.path.isdir(MYDIR)

    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(MYDIR)
        print("created folder : ", MYDIR)

    else:
        print(MYDIR, "folder already exists.")
    return CHECK_FOLDER

'''def get_df(file,content ,retrain = False):
    #filename = os.path.abspath(file.name)
    df = pd.DataFrame()
     
    if not retrain:
        new_path = os.path.dirname(filename)
        csv_files = glob.glob(os.path.join(new_path, "*.csv"))
  
        # loop over the list of csv files
        for f in csv_files:
            
            # read the csv file
            df_temp = pd.read_csv(f,names=COLNAMES)
            df = pd.concat([df,df_temp])
            # print the location and filename
            print('Location:', f)
            print('File Name:', f.split("\\")[-1])
            # print the content
            print('Content:')
            #display(df)
        

    #save current file
    s=str(content,'utf-8')
    data = StringIO(s) 
    df=pd.concat([df,pd.read_csv(data,names=COLNAMES)])
    df.reset_index(inplace=True, drop=True)
        
    return df
'''


def get_df(path):
    #filename = os.path.abspath(file.name)
    if not os.path.isdir(path):
        raise HTTPException(status_code = 404, detail= "You do not have any data saved. Please save data ")
    df = pd.DataFrame()
     
    
    #new_path = os.path.dirname(filename)
    csv_files = glob.glob(os.path.join(path, "*.csv"))

    # loop over the list of csv files
    
    for f in csv_files:
        
        # read the csv file
        df_temp = pd.read_csv(f,names=COLNAMES)
        df = pd.concat([df,df_temp])
        # print the location and filename
        print('Location:', f)
        print('File Name:', f.split("\\")[-1])
        # print the content
        print('Content:')
        #display(df)
        

    #save current file
    df.reset_index(inplace=True, drop=True)
        
    return df
def is_valid(df,unsupervised=True):

    if len(df.columns)>1 and unsupervised:
        return json.dumps(ERRORS_FRENCH[1])
    if 'text' not in df.columns:
        return json.dumps(ERRORS_FRENCH[1])
    for document in df['text']:
        if isinstance(document, str):
            continue
        else:
            return json.dumps(ERRORS_FRENCH[0])
        

    return True
def get_payload(authorization):
    token = authorization.split()[1]
    payload = decodeJWT(token)
    return payload

def before_save_file(payload,file_content,default_filecontent="text/csv"):
    if payload["username"]!="" and payload["is_eligible"] is True and file_content==default_filecontent:
        return True
    elif file_content!=default_filecontent:
        raise  HTTPException(status_code = 400, detail="The file is not a "+default_filecontent+" file")
    else:
        raise  HTTPException(status_code = 401, detail="You ar not eligible for this feature")

def load_data_from_path(username):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f'{dir_path}/uploads/{username}/csv/'
    df = get_df(path)


    return  df