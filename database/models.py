import dashboard
from sqlalchemy import Integer, String,Float,Date,Boolean
from sqlalchemy.orm import query, relationship
from sqlalchemy.orm import session
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import column, null
from sqlalchemy.sql.schema import Column, ForeignKey, Table
#from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from fastapi import HTTPException
import bcrypt
from database.database import SessionLocal, get_db
import re   
  
email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
password_regex = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,15}$' 
#username_regex = '^([a-zA-Z])[a-zA-Z_-]*[\w_-]*[\S]$|^([a-zA-Z])[0-9_-]*[\S]$|^[a-zA-Z]*[\S]$' 
username_regex = '^[a-zA-Z0-9][a-zA-Z0-9_]{2,29}$'
phone_regex = '^(\(?\+?[0-9]*\)?)?[0-9_\- \(\)]*$'
Base = declarative_base()

'''association_table = Table('association', Base.metadata,
    Column('left_id', ForeignKey('users.id'), primary_key=True),
    Column('right_id', ForeignKey('plans.id'), primary_key=True)
) ''' 
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    contact = Column(String(16), nullable=False)
    password = Column(String(128),nullable = False)
    children = relationship("Membership")
    type = Column(Integer,nullable= False)
    verified = Column(Boolean,default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    @validates('username')
    def validate_username(self,key,value):
    
        db = SessionLocal()
       
          
        if db.query(User).filter(User.username==value).first():
            db.close()
            raise HTTPException(status_code=401, detail=" username already in use") 
        if not (re.search(username_regex,value)):
            raise HTTPException(status_code=401, detail="invalid username: username must contain not space and no special characters") 
        else:
            return value
    
    @validates('email')
    def validate_email(self,key,value):
    
        db = SessionLocal()
        if db.query(User).filter(User.email==value).first():
            #print("passe ")
            db.close()
            raise HTTPException(status_code=401, detail=" addresse email deja utilise") 
        if not (re.search(email_regex,value)):
            raise HTTPException(status_code=401, detail=" addresse email invalide") 
            
        else:
            return value  
    
    @validates('contact') 
    def validate_contact(self,key,value):
        if not (re.search(phone_regex,value)):
            raise HTTPException(status_code=401, detail="Invalid phone number  ") 
        else:
            return value 
        #print("Working")
        #if key  in query:
         #   raise ValueError("Le nom d'utilisateur est deja utilise")


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    password = Column(String(128),nullable = False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    def check_password(self, password):
        return bcrypt.checkpw(self.password.encode('utf-8'), password.encode('utf-8'))
    @validates('email')
    def validate_email(self,key,value):
    
        db = SessionLocal()
        if db.query(User).filter(User.email==value).first():
            #db.close()
            raise HTTPException(status_code=401, detail=" addresse email deja utilise") 
        if not (re.search(email_regex,value)):
            raise HTTPException(status_code=401, detail=" addresse email invalide") 
            
        else:
            return value  

    
    @validates('password') 
    def validate_password(self,key,value):
        if not (re.search(password_regex,value)):
            raise HTTPException(status_code=401, detail="Password must be between 8-15 digits, containing at least one alphanumeric character one uppercase letter and one lower case letter ") 
        else:
            return value 
'''
'''

   
   
#many-to-many-association

class Membership(Base):
    __tablename__ = 'memberships'
    left_id = Column(ForeignKey('users.id'), primary_key=True)
    right_id = Column(ForeignKey('plans.id'), primary_key=True)
    expiring_date = Column(DateTime,nullable=False)
    expired = Column(Boolean,default = False)
    plan = relationship("Plan")
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

     


'''class Pricing(Base):
    __tablename__ = 'pricings'

    id = Column(Integer, primary_key=True)
    price = Column(Float,nullable = False)
    duration = Column(Integer, nullable=False)
    is_trial = Column(Boolean, default=False,nullable=False)
    end_date = column(Date)'''
class Plan (Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True)
    price = Column(Float,nullable = False)
    duration = Column(Integer, nullable=False)
    is_trial = Column(Boolean, default=False,nullable=False)
    dashboard_eligible = Column(Boolean, default=False)
    max_number = Column(Integer,default=100)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    


class ApiRequest(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    type_request = Column(Integer, nullable=False)
    nb_texts = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def create(self,db):
        db.add(self)
        db.commit()
        return self.id