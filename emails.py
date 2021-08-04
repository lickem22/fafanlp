from database.models import User
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form,HTTPException
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel, EmailStr
from typing import List
from decouple import config
import jwt

EMAIL_SECRET = config("EMAIL_SECRET")
JWT_ALGORITHM = config("algorithm")


class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = config("EMAIL"),
    MAIL_PASSWORD = config("PASS"),
    MAIL_FROM = config("EMAIL"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


def effify(non_f_str: str):
    return eval(f'f"""{non_f_str}"""')

async def decode_verification_token(token:str):
    payload = jwt.decode(token,EMAIL_SECRET,algorithms=[JWT_ALGORITHM])
    '''try:
        payload = jwt.decode(token,EMAIL_SECRET,algorithms=[JWT_ALGORITHM])
        
    except Exception as e:
        print(e)
        #raise HTTPException(status_code =401, email="Invalid token",headers={"WWW.Authenticate":"Bearer"} )'''
    return payload

'''
email for user confirmation
'''
async def send_confirmation_mail(email: List,user:User) -> JSONResponse:
    token_data = {
        "id":user.id,
        "username":user.username,
    }
    token = jwt.encode(token_data,EMAIL_SECRET, algorithm=JWT_ALGORITHM).decode('utf-8')    
    with open('templates/user_verification.html', 'r') as file:
        data = file.read()
    #html = effify(data)
    #transform content to f string 
    html =  eval(f'f"""{data}"""')

    
    message = MessageSchema(
        subject="fafanlp verification email",
        recipients=email,  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})     
'''
email for password  change
'''


async def send_recovery_mail(email: List,user:User) -> JSONResponse:
    token_data = {
        "id":user.id,
        "username":user.username,
        "verified":user.verified
    }
    token = jwt.encode(token_data,EMAIL_SECRET, algorithm=JWT_ALGORITHM).decode('utf-8')    
    with open('templates/password_recovery.html', 'r') as file:
        data = file.read()
    #html = effify(data)
    #transform content to f string 
    html =  eval(f'f"""{data}"""')

    
    message = MessageSchema(
        subject="fafanlp password recovery",
        recipients=email,  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})     