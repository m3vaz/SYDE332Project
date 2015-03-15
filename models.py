from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Boolean
from sqlalchemy import create_engine


Base = declarative_base()

class Flow(Base):
	__tablename__ = 'flowdata'
	
	id = Column(Integer, primary_key=True) # Will be marked as autoincrement
	site = Column(Integer)
	amount = Column(Integer)
	measuredateyear = Column(Integer)
	measuredatemonth = Column(Integer)
	measuredateday = Column(Integer)
	datapoints = Column(Integer)
	average = Column(Boolean, default=False)
	
engine = create_engine('mysql://root:pass1234@localhost/SYDE332')
Base.metadata.create_all(engine)



