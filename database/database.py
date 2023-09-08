


from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector

Base = declarative_base()

import urllib.parse

# Encode the password using urllib.parse.quote_plus
password = urllib.parse.quote_plus("denil_kurian@123")

# Construct the DATABASE_URL
DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/school"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

