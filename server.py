
from datetime import datetime
from emails import decode_verification_token, send_recovery_mail
from emails import send_confirmation_mail
import os
import time 
import json
from types import MemberDescriptorType
from sqlalchemy.orm import query
from sqlalchemy.orm import session
import uvicorn
from sqlalchemy.orm.session import Session

from database.database import get_db
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from fastapi import FastAPI,Header,UploadFile,File,Form,Request,Body,Depends,HTTPException
from typing import List,Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from datetime import datetime
#my packages 
from database.models import ApiRequest, Membership, Plan, User
from schemas import MembershipRequest, PasswordForgotten, PasswordRecovery, PlanRequest, Text, UserAuthentication, UserRequest
from auth.auth_handler import get_login_token, signJWT,decodeJWT
from auth.auth_bearer import JWTBearer
from preprocessing import preprocessing_french
from keywords_extraction import extract_keywords2
from sentiment_analysis import sentiment_analysis
from utils import before_save_file, folder_exists,get_payload, load_data_from_path
from dashboard import keywords_count, sentiments_count
PHRASER_LOCATION = 'models/phraser.pkl'
KEYWORDS_CANDIDATES =  'models/keywords-candidates/cv.pkl'

#global variables
#model = TFAutoModelForSequenceClassification.from_pretrained("tblard/tf-allocine")
#stokenizer = AutoTokenizer.from_pretrained("tblard/tf-allocine")


#initialise app
app = FastAPI()
db1 =get_db
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    db = get_db()
    # create a dummy entry
    #await User.objects.get_or_create(email="test@test.com")


@app.on_event("shutdown")
async def shutdown():
    db1.close()

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

@app.post("/users/new/",tags=["user"])
async def user_create(user: UserRequest,db: Session = Depends(get_db) ):
    #users.append(user) # replace with db call, making sure to hash the password first
    
    to_create = User(
        username=user.username,
        email=user.email,
        contact = user.contact,
        password = user.password,
        verified = False,
        #password = user.password,
        type = user.type)
    to_create.set_password(user.password)
    try:
        db.add(to_create)
        db.commit()
        if True:
            await send_confirmation_mail([to_create.email],to_create)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail= "Something went wrong "+e)
    return { 
    "success": True,
    "created_id": to_create.id
        }

    
@app.post("/users/update/",tags=["user"])
async def user_update(id:int,instance: UserRequest,db: Session = Depends(get_db) ):
    #users.append(user) # replace with db call, making sure to hash the password first
    user =  db.query(User).filter(User.email==instance.email).first() 
    to_create = User(
        username=user.username,
        email=user.email,
        contact = user.contact,
        password = user.password,
        verified = False,
        #password = user.password,
        type = user.type)
    to_create.set_password(user.password)
    if True:
        db.add(to_create)
        db.commit()
    else:
        raise HTTPException(status_code=500, detail= "Something went wrong "+e)
    return { 
    "success": True,
    "created_id": to_create.id
        }
@app.post("/users/send-verification")
async def resend_verification_mail(instance: PasswordForgotten,db: Session = Depends(get_db)):
    user =  db.query(User).filter(User.email==instance.email).first() 
    print(user)
    if user:

        return await send_confirmation_mail([user.email],user)
            

    else:
        raise  HTTPException(status_code =404, detail="User doesn't exist",headers={"WWW.Authenticate":"Bearer"} )
#verify user
@app.get("/users/verify",response_class=HTMLResponse)
async def email_verification(request:Request,token:str,db: Session = Depends(get_db)):
    try:
        payload = await decode_verification_token(token)
       
    except Exception:
         raise HTTPException(status_code =404, detail="Wrong token",headers={"WWW.Authenticate":"Bearer"} )

    user =  db.query(User).filter(User.id==payload['id']).first()
    if User:
        if not user.verified:
            user.verified = True
            db.commit()
        return templates.TemplateResponse("verified.html",{"request":request,"username":user.username})
    else:
        raise  HTTPException(status_code =404, detail="User doesn't exist",headers={"WWW.Authenticate":"Bearer"} )

@app.post("/users/password-forgotten/",tags=["user"])
async def password_forgotten(forgotten: PasswordForgotten,db: Session = Depends(get_db)):
    try:
        user =  db.query(User).filter(User.username==forgotten.username).first()   
        if user:
            return await send_recovery_mail([user.email],user)

        else:
            raise  HTTPException(status_code =404, detail="User doesn't exist",headers={"WWW.Authenticate":"Bearer"} )
    except Exception as e:
        print(e)



 #recover password       
@app.get("/users/password-recovery",response_class=HTMLResponse)
async def recovery_page(request:Request,token:str,db: Session = Depends(get_db)):
    try:
        payload = await decode_verification_token(token)
       
    except Exception:
         raise HTTPException(status_code =404, detail="Wrong token",headers={"WWW.Authenticate":"Bearer"} )

    user =  db.query(User).filter(User.id==payload['id']).first()
    if User:
        if not user.verified:
            raise HTTPException(status_code =403, detail="User not verified",headers={"WWW.Authenticate":"Bearer"} )
        return templates.TemplateResponse("new_password.html",{"request":request,"username":user.username,"email":user.email})
    else:
        raise  HTTPException(status_code =404, detail="User doesn't exist",headers={"WWW.Authenticate":"Bearer"} )

# new passwod
@app.post("/users/newpassword")
async def new_password(instance:PasswordRecovery,db: Session = Depends(get_db)):
    user =  db.query(User).filter(User.username==instance.username).first()  
    if user:
        user.set_password(instance.password)   
        db.commit()
        return user.id
    else:
        raise HTTPException(status_code =404, detail="User doesn't exist",headers={"WWW.Authenticate":"Bearer"} )

    
@app.post("/users/login/",tags=["user"])
async def user_create(user_auth: UserAuthentication,db: Session = Depends(get_db) ):
    #users.append(user) # replace with db call, making sure to hash the password first
    
    user =  db.query(User).filter(User.email==user_auth.email).first()
    if user:
        
            print(user.password)
            print(user.check_password(user_auth.password))
            return get_login_token(user)
    else:
        raise HTTPException(status_code=404, detail= "User not found  ")


 

@app.post("/users/token",tags=["user"])
async def token_create(instance: UserAuthentication,db: Session = Depends(get_db)):
  
    user= db.query(User).filter(User.username==instance.username).first()
    query = db.query(Membership).join(User).filter(User.username==instance.username).filter(Membership.expired==False).first()
    if query and user:
            if (user.verified):
                plan = db.query(Plan).filter(Plan.id==query.right_id).first()
                print(plan)
                try:
                    return signJWT(user,query.expiring_date,plan.max_number,plan.dashboard_eligible)
                except Exception as e:
                    print(e)
            else:
                raise HTTPException(status_code=401, detail="User not verified. Please check user is verified")
    else:
        raise HTTPException(status_code=400, detail="Membership not found make sure you have one")
    '''try:
        if query and user:
            if (user.verified):
                plan = db.query(Plan).filter(Plan.id==query.right_id).first()
                return signJWT(instance,query.expiring_date,plan.max_number,plan.dashboard_eligible)
            else:
                raise HTTPException(status_code=401, detail="User not verified. PLease check user is verified")
        else:
            raise HTTPException(status_code=400, detail="Membership not found make sure you have one")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Somethin went wrong"+e)'''
'''

KEYBOARD EXTRACTION

'''

@app.post("/memberships/new",tags=["members"])
async def create_membership(member: MembershipRequest, db: Session = Depends(get_db)):
    #dt_object = datetime.fromtimestamp(1628629068.1242206).date()
    timestamp_now = datetime.timestamp(datetime.now())
    #now = datetime.now()
    plan= db.query(Plan).filter(Plan.id==member.right_id).first()
    print(plan.id)
    user =  db.query(User).filter(User.id==member.left_id).first()
    expiring_date = datetime.fromtimestamp(timestamp_now+plan.duration)
    print(user.id)
    if user and plan:
        print(1)
        membership =  db.query(Membership).join(User).join(Plan).filter(Membership.left_id==user.id).filter(Membership.expired ==False).one_or_none()
        #membership.expired= True
        
        if membership:
            membership.expired= True
            if membership.right_id ==plan.id:
                
                print(expiring_date)
                print(expiring_date)
                membership.expiring_date = expiring_date
                membership.expired = False
                
            else:
                new_membership =  db.query(Membership).join(User).join(Plan).filter(Membership.left_id==user.id).filter(Membership.right_id==plan.id).one_or_none()
                
                if new_membership:
                    print("if")
                    new_membership.expiring_date = expiring_date
                    new_membership.expired = False
                else:
                        to_create = Membership(
                        left_id=user.id,
                        right_id = plan.id,
                        expiring_date = expiring_date,
                        expired = False
                        )
                        db.add(to_create)
        else:
            
            to_create = Membership(
                        left_id=user.id,
                        right_id = plan.id,
                        expiring_date = expiring_date,
                        expired = False
                        )
            db.add(to_create)
        db.commit()
        


    return { 
        "success": True
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
#keyboard extraction
@app.put("/keywords-extraction/extract-keywords", tags=["keywords"],dependencies=[Depends(JWTBearer())])
async def new_keywords(text: Text,Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    payload = get_payload(Authorization)
    h = len(text.texts)
    print(h)
    #keywords_list = extract_keywords(text.texts)
    if h<payload['max_number']:
        print(True)
        #preprocessed = preprocessing_french(text.texts)
        keywords_list = extract_keywords2(text.texts)
        #print(keywords_list)
        print("ok")
        to_create = ApiRequest(type_request=1,
                                nb_texts = h,
                                user_id = payload['user_id'])
        to_create.create(db)
        print("fine")  
        return keywords_list
    else:
        raise HTTPException(status_code=403, detail="You are allowed only "+str(payload['max_number'])+" texts as input")

    #keywords_list = extract_keywords2(text.texts)
    #get access_token
    
@app.put("/keywords-extraction/test")
async def test_keywords(text: Text):
    #payload = get_payload(Authorization)
    
    #h = len(text.texts)
    #keywords_list = extract_keywords(text.texts)
    try:
    
        preprocessed = preprocessing_french(text.texts)
        keywords_list = extract_keywords2(preprocessed)
        return keywords_list
    except Exception as e:
        print(e)
    
        #print(keywords_list)
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
@app.put("/sentiment-analysis/sentiments",tags=["sentiments"], dependencies=[Depends(JWTBearer())])
async def analyse_sentiments(text: Text,Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    
    payload = get_payload(Authorization)
    h = len(text.texts)
    #keywords_list = extract_keywords(text.texts)
    if h<payload['max_number']:
        sentiments = sentiment_analysis(text.texts,model,tokenizer)
        to_create = ApiRequest(type_request=2,
                                nb_texts = h,
                                user_id = payload['user_id'])
        to_create.create(db)
        return sentiments
    else:
        raise HTTPException(status_code=403, detail="You are allowed only "+str(payload['max_number'])+" texts as input")
    return sentiments


'''
DASHBOARD 

'''
@app.post("/save-text/csv",tags=["dashboard"] ,dependencies=[Depends(JWTBearer())])
async def save_data(file:UploadFile = File(...),Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
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
        to_create = ApiRequest(type_request=3,
                                nb_texts = 0,
                                user_id = payload['user_id'])
        to_create.create(db)
    return json.dumps({"detail":"FILE succesfully saved "})
      
    '''
    df = get_df(f,content,retrain)
    if is_valid(df,unsupervised=True)==True:
        f.write(content)
        train_tfidf(df['text'],(1,2),'tf_idf_Test.pkl','cv_Test.pkl','candidates_Test.pkl')
    else:
        return is_valid(df,True)
    ''' 



@app.get("/dashboard/keywords/barchart",tags=["dashboard"], dependencies=[Depends(JWTBearer())])
async def keywords_barchart(request: Request,Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    #data = extract_keywords2(text.texts)
    payload = get_payload(Authorization)
    df = load_data_from_path(payload['username'])
    #df = load_data_from_path("Test")
    #print(df)
    data = keywords_count(df.text)
    to_create = ApiRequest(type_request=4,
                                nb_texts = len(df.text),
                                user_id = payload['user_id'])
    to_create.create(db)
    return templates.TemplateResponse("barchart_keywords.html", {"request": request, "data":data})
    #return data
'''
SENTIMENT ANALYSIS DASHBOARD
'''
@app.put("/dashboard/sentiments/barchart", tags=["dashboard"],dependencies=[Depends(JWTBearer())])
async def keywords_barchart(text: Text,request: Request,Authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    #data = extract_keywords2(text.texts)
    payload = get_payload(Authorization)
    if payload['is_eligible']:
        data = sentiments_count(text.texts,model,tokenizer)
        to_create = ApiRequest(type_request=5,
                                nb_texts = len(text.texts),
                                user_id = payload['user_id'])
        to_create.create(db)
        return templates.TemplateResponse("barchart_keywords.html", {"request": request, "data":data})
    else:
        return HTTPException(status_code=404,detail = "You are not eligible to this feature")

if __name__ =='__main__':
    uvicorn.run("server:app",host = "0.0.0.0",port=8000)