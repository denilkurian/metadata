
from fastapi import APIRouter
from sqlalchemy import create_engine, MetaData
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
            table_metadata[table_name] = {
                "columns": columns,
                "primary_key": [column.name for column in table.primary_key],
            }

        # Send email notification when crawling is done
        send_email_notification(db_name)

        return {"message": f"Metadata crawl job initiated for {db_name}", "metadata": table_metadata}

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}




    









