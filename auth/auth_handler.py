from database.models import Membership
from database.database import SessionLocal
from schemas import UserAuthentication
from datetime import datetime 
import time
from typing import Dict

import jwt
from decouple import config


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(user: UserAuthentication,expiring_date,max_number,is_eligible) -> Dict[str, str]:

    payload = {
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