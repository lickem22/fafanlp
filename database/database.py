from datetime import time
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://carlos:carlos@localhost/fafanlp"

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

