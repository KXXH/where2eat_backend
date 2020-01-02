from sqlalchemy import Column, String, create_engine,Integer,DATETIME,FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
Base = declarative_base()

class EatHistory(Base):
    __tablename__='history'
    id=Column(Integer,primary_key=True)
    place=Column(String(20))
    price=Column(FLOAT())
    date=Column(DATETIME)

engine = create_engine('sqlite:///eatRecord.db', echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

if __name__=="__main__":
    where=input("今天吃了哪？")
    how_much=float(input("吃了多少钱?"))
    session=Session()
    record=EatHistory(place=where,price=how_much,date=datetime.now())
    session.add(record)
    session.commit()
    session.close()