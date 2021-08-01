from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://carlos:carlos@localhost/fafanlp"

engine = create_engine(SQLALCHEMY_DATABASE_URL,echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()