from database.models import Membership, User
from database.database import SessionLocal
from schemas import UserAuthentication
from datetime import datetime 
import time
from typing import Dict

import jwt
from decouple import config


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str,label="access_token"):
    return {
        label: token
    }
def get_login_token(user):
    payload = {
        "id":user.id,
        "username": user.username,
        "email": user.email,
        "contact":user.contact,
        "type":user.contact
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM).decode('utf-8')
    return token_response(token,"user_token")

def signJWT(user: User,expiring_date,max_number,is_eligible) -> Dict[str, str]:

    payload = {
        "user_id":user.id,
        "username": user.username,
        "max_number":max_number,
        "expires": datetime.timestamp(expiring_date),
        "is_eligible":is_eligible
    
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM).decode('utf-8')

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except Exception as e: 
        print(e)
        return {}


