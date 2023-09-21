
from fastapi import APIRouter
from sqlalchemy import create_engine, MetaData,inspect
import urllib.parse
from database.database import database_urls, username, password, host, port, database_name
from notification_services.email import send_email_notification


# Create an APIRouter instance
router = APIRouter()


# Define the /crawl_metadata endpoint
@router.post("/crawl_metadata/{db_name}",tags=['metadata'])
async def crawl_metadata(db_name: str):
    # Check if the provided db_name is supported
    db_url = database_urls.get(db_name, None)

    if db_url is None:
        return {"error": f"Unsupported database type: {db_name}"}

    # Create the connection URL using the selected database type
    url_template = "{db_url}://{username}:{password}@{host}:{port}/{database_name}"
    DATABASE_URL = url_template.format(
        db_url=db_url,
        username=username,
        password=urllib.parse.quote_plus(password),
        host=host,
        port=port,
        database_name=database_name,
    )

    try:
        # Create the database engine
        engine = create_engine(DATABASE_URL, echo=True)
        metadata = MetaData()

        # Reflect all tables in the database
        metadata.reflect(bind=engine)
        inspector = inspect(engine)

        # Get a list of all table names in the database
        table_names = metadata.tables.keys()

        # Retrieve metadata information for each table, including data types
        table_metadata = {}
        for table_name in table_names:
            table = metadata.tables[table_name]
            columns = []
            for column in table.columns:
                columns.append({
                    "name": column.name,
                    "type": str(column.type),  # Get the data type as a string
                })

            foreign_keys = []
            for foreign_key in inspector.get_foreign_keys(table_name):
                foreign_keys.append({
                    "column": foreign_key['constrained_columns'][0],
                    "referenced_table": foreign_key['referred_table'],
                })



            table_metadata[table_name] = {
                "columns": columns,
                "primary_key": [column.name for column in table.primary_key],
                "foreign_keys": foreign_keys,
            }

        # Send email notification when crawling is done
        send_email_notification(db_name)

        return {"message": f"Metadata crawl job initiated for {db_name}", "metadata": table_metadata}

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}





########### to fetch database metadata from another resource and also implemeted caching the data in redis
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from main import app
from fastapi import Depends,HTTPException
from cachetools import TTLCache
import aioredis

# class SupportedDatabases(str, Enum):
#     mysql = "mysql"
#     sqlite = "sqlite"
#     postgres = "postgres"
#     redis = "redis"
#     mongodb = "mongodb"

class Connection(BaseModel):
    string: str


Session = sessionmaker()

metadata = MetaData()

async def fetch_metadata(connection_string: Connection):
    source_db_url = connection_string.string

    # try to fetch from Redis
    redis = await aioredis.from_url('redis://localhost')
    cached_metadata_redis = await redis.get(source_db_url.encode())
    await redis.close()

    if cached_metadata_redis:
        metadata_str = cached_metadata_redis.decode()
        print("data from redis-cache")
        return metadata_str

    # If not found in Redis, fetch from MySQL
    engine = create_engine(source_db_url)
    Session.configure(bind=engine)
    session = Session()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata_str = str(metadata.tables.values())

    # Cache the data in Redis
    redis = await aioredis.from_url('redis://localhost')
    await redis.setex(source_db_url.encode(), 300, metadata_str.encode())
    await redis.close()

    print("data from mysql")
    return metadata_str

# Define the API endpoint
@app.post("/any_db_metadata/", tags=["db metadata"])
async def any_db_metadata(connection_string: Connection):
    try:
        metadata_str = await fetch_metadata(connection_string)
        return metadata_str
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})





