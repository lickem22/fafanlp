import datetime
from typing import Optional, List

from sqlalchemy.sql.sqltypes import DateTime
from pydantic import BaseModel
from typing import Optional

class Text(BaseModel):
    texts: List[str]
    #keywords: Optional[int]

#class CustomKeywordModel(BaseModel):
class UserRequest(BaseModel):
    username: str
    email:str
    contact:str
    type:int
    password: str
    
class UserAuthentication(BaseModel):
    username: str
    password: str
    email: str
class PasswordForgotten(BaseModel):
    username: str
    email: str
class PasswordRecovery(BaseModel):
    username: str
    password: str
    email: str
class PlanRequest(BaseModel):
    price: float
    duration: int
    is_trial: bool
    dashboard_eligible:bool
class MembershipRequest(BaseModel):
    left_id:int
    right_id: int
    expired: bool