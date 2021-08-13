from datetime import time
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


#SQLALCHEMY_DATABASE_URL = "postgresql://carlos:carlos@localhost/fafanlp"
SQLALCHEMY_DATABASE_URL = "postgresql://xiuseaxkrqslgz:ccd37b68ef34481a7e2b2d3d34679dc7be8828dbef9ea39060093fd2c2fd3d16@ec2-54-220-53-223.eu-west-1.compute.amazonaws.com:5432/d5pk7em6s1t4j8"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




def get_db():
    retries = 5
    while retries >0:
        try:
            db = SessionLocal()
            
            try:
                yield db
            except:
                db.close()
            break
            
        except Exception as e:
            print(e)
            retries = retries-1
            print(str(retries)+" retries left")
            time.sleep(5)

