
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse

Base = declarative_base()

# Define a dictionary to map database types to SQLAlchemy connection URLs
database_urls = {
    "mysql": "mysql+mysqlconnector",
    "postgresql": "postgresql+psycopg2",
    "oracle": "oracle+cx_oracle",
    "snowflake": "snowflake+pydatawarehouse",
    "bigquery": "bigquery://",
    "redshift": "redshift+psycopg2",
}

# Specify the database type you want to use
selected_database = "mysql"  # Change this to the desired database type

# Database connection parameters
username = "root"
password = "denil_kurian@123"
host = "localhost"
port = 3306
database_name = "school"

# Create the connection URL using the selected database type
url_template = "{db_url}://{username}:{password}@{host}:{port}/{database_name}"
db_url = database_urls.get(selected_database, None)


DATABASE_URL = url_template.format(
    db_url=db_url,
    username=username,
    password=urllib.parse.quote_plus(password),
    host=host,
    port=port,
    database_name=database_name,
)

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()











