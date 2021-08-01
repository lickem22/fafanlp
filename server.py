from datetime import datetime
import os
import time 
import json
from types import MemberDescriptorType
from sqlalchemy.orm import query
from sqlalchemy.orm import session

from sqlalchemy.orm.session import Session

from database.database import get_db
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from fastapi import FastAPI,Header,UploadFile,File,Form,Request,Body,Depends,HTTPException
from typing import List,Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime
#my packages 
from database.models import Membership, Plan, User
from schemas import MembershipRequest, PlanRequest, Text, UserAuthentication, UserRequest
from auth.auth_handler import signJWT,decodeJWT
from auth.auth_bearer import JWTBearer
from preprocessing import preprocessing_french
from keywords_extraction import extract_keywords2
from sentiment_analysis import sentiment_analysis
from utils import before_save_file, folder_exists,get_payload, load_data_from_path
from dashboard import keywords_count, sentiments_count
PHRASER_LOCATION = 'models/phraser.pkl'
KEYWORDS_CANDIDATES =  'models/keywords-candidates/cv.pkl'

#global variables
model = TFAutoModelForSequenceClassification.from_pretrained("tblard/tf-allocine")
tokenizer = AutoTokenizer.from_pretrained("tblard/tf-allocine")

#initialise app
app = FastAPI()

templates = Jinja2Templates(directory="chart_templates")

@app.get("/")
def home():
    return {"Hello": "FastAPI"}


'''@app.put("/keywords-extraction/get_keywords")
async def new_keywords(text: Text,key: Optional[str] = Header(None)):
    #text_processed = preprocessing_french(text.texts)
    #keywords_list = get_keywords(text_processed)
    keywords_list = extract_keywords(text.texts)
    return keywords_list'''

'''
LOGIN AND SECURITY
'''
#create user 

@app.post("/user/new",tags=["user"])
async def user_create(user: UserRequest,db: Session = Depends(get_db) ):
    #users.append(user) # replace with db call, making sure to hash the password first
    
    try: 
        to_create = User(
        username=user.username,
        email=user.email,
        contact = user.contact,
        #password = user.password,
        type = user.type)
        to_create.set_password(user.password)
        db.add(to_create)
        db.commit()
        return { 
        "success": True,
        "created_id": to_create.id
    }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail= "Something went wrong "+e)  


 

@app.post("/user/token",tags=["user"])
async def create_token(user: UserAuthentication,db: Session = Depends(get_db)):
    try:
        query = db.query(Membership).join(User).filter(User.username==user.username).filter(Membership.expired==False).first()
        if query:
            if (query.verified):
                plan = db.query(Plan).filter(Plan.id==query.right_id).first()
                return signJWT(user,query.expiring_date,plan.max_number,plan.dashboard_eligible)
            else:
                raise HTTPException(status_code=401, detail="User not verified. PLease check user is verified")
        else:
            raise HTTPException(status_code=400, detail="Membership not found make sure you have one")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Somethin went wrong"+e)
'''
KEYBOARD EXTRACTION

'''
@app.get("/user/test",tags=["user"])
async def create_token2(db: Session = Depends(get_db)):
    query = db.query(Membership).join(User).filter(User.username=="fafanlp").filter(Membership.expired==False).first()
    
    try:
        print(query.expiring_date)
        
    except Exception as e:
        print(e)


    return True

@app.post("/member/test",tags=["user"])
async def create_membership(member: MembershipRequest, db: Session = Depends(get_db)):
    dt_object = datetime.fromtimestamp(1628629068.1242206).date()
    try:
        to_create = Membership(
            left_id=member.left_id,
            right_id = member.right_id,
            expiring_date = dt_object,
            expired = member.expired
            )
        #to_create.set_password(user.password)
        db.add(to_create)
        db.commit()
    except Exception as e:
        print(e)
    return { 
        "success": True,
        "created_id": to_create.id
    }
@app.post("/plan/test",tags=["user"])
async def create_membership(member: PlanRequest, db: Session = Depends(get_db)):
    
    to_create = Plan(
        price=member.price,
        duration = member.duration,
        dashboard_eligible = member.dashboard_eligible
        )
    #to_create.set_password(user.password)
    db.add(to_create)
    db.commit()
    return { 
        "success": True,
        "created_id": to_create.id
    }

@app.put("/keywords-extraction/extract-keywords", dependencies=[Depends(JWTBearer())])
async def new_keywords(text: Text,Authorization: Optional[str] = Header(None)):
    payload = get_payload(Authorization)
    h = len(text.texts)
    #keywords_list = extract_keywords(text.texts)
    if 101<payload['max_number']:
        preprocessed = preprocessing_french(text.texts)
        keywords_list = extract_keywords2(preprocessed)
        return keywords_list
    else:
        raise HTTPException(status_code=403, detail="You are allowed only "+str(payload['max_number'])+" texts as input")

    #keywords_list = extract_keywords2(text.texts)
    #get access_token
    
    
   

'''@app.post("/keywords-extraction/train", dependencies=[Depends(JWTBearer())])
async def train_keywords_model(company:Optional[str]=Form(...),retrain:bool = Form(...),file:UploadFile = File(...),Authorization: Optional[str] = Header(None)):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    payload = get_payload(Authorization)

    print(dir_path)
    if file.content_type =="text/csv" and payload["company"]!=None:
        filename = f'{dir_path}/uploads/{payload["company"]}/{time.time()}-{file.filename}'
        #print(os.path.dirname(filename))
        folder_exists(os.path.dirname(filename))
        f = open(f'{filename}', 'wb')
        content = await file.read()
        # print(type( await file.read()))
        
       
        #documents = pd.read_csv(content,names =['text'])
        df = get_df(f,content,retrain)
        if is_valid(df,unsupervised=True)==True:
            f.write(content)
            train_tfidf(df['text'],(1,2),'tf_idf_Test.pkl','cv_Test.pkl','candidates_Test.pkl')
        else:
            return is_valid(df,True)




    else:
        return {"error": "Please insert a csv file"}
    return {
        "status":"Model training has succesfully started."
    }

'''
'''
SENTIMENT ANALYSIS
'''
@app.put("/sentiment-analysis/sentiments", dependencies=[Depends(JWTBearer())])
async def analyse_sentiments(text: Text,Authorization: Optional[str] = Header(None)):
    
    payload = get_payload(Authorization)
    h = len(text.texts)
    #keywords_list = extract_keywords(text.texts)
    if h<payload['max_number']:
        sentiments = sentiment_analysis(text.texts,model,tokenizer)
        return sentiments
    else:
        raise HTTPException(status_code=403, detail="You are allowed only "+str(payload['max_number'])+" texts as input")
    return sentiments


'''
DASHBOARD 

'''
@app.post("/save-text/csv", dependencies=[Depends(JWTBearer())])
async def save_data(file:UploadFile = File(...),Authorization: Optional[str] = Header(None)):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    payload = get_payload(Authorization)

    print(dir_path)
    authorised = before_save_file(payload,file.content_type)
    if authorised:
        filename = f'{dir_path}/uploads/{payload["username"]}/csv/{time.time()}-{file.filename}'
        #print(os.path.dirname(filename))
        #check if folder exists if not create 
        folder_exists(os.path.dirname(filename))
        f = open(f'{filename}', 'wb')
        content = await file.read()
        f.write(content)
    return json.dumps({"detail":"FILE succesfully saved "})
      
    '''
    df = get_df(f,content,retrain)
    if is_valid(df,unsupervised=True)==True:
        f.write(content)
        train_tfidf(df['text'],(1,2),'tf_idf_Test.pkl','cv_Test.pkl','candidates_Test.pkl')
    else:
        return is_valid(df,True)
    ''' 



@app.get("/dashboard/keywords/barchart", dependencies=[Depends(JWTBearer())])
async def keywords_barchart(request: Request,Authorization: Optional[str] = Header(None)):
    #data = extract_keywords2(text.texts)
    payload = get_payload(Authorization)
    df = load_data_from_path(payload['username'])
    #df = load_data_from_path("Test")
    #print(df)
    data = keywords_count(df.text)
    return templates.TemplateResponse("barchart_keywords.html", {"request": request, "data":data})
    #return data
'''
SENTIMENT ANALYSIS DASHBOARD
'''
@app.put("/dashboard/sentiments/barchart", dependencies=[Depends(JWTBearer())])
async def keywords_barchart(text: Text,request: Request,Authorization: Optional[str] = Header(None)):
    #data = extract_keywords2(text.texts)
    payload = get_payload(Authorization)
    if payload['is_eligible']:
        data = sentiments_count(text.texts,model,tokenizer)
        return templates.TemplateResponse("barchart_keywords.html", {"request": request, "data":data})
    else:
        return HTTPException(status_code=404,detail = "You are not eligible to this feature")