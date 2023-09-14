
from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# api for Fetch all tables in the database
@router.get("/tables",tags=['metadata'])
def get_tables():
    with engine.connect() as connection:
        query = text("SHOW TABLES;")
        result = connection.execute(query)
        table_names = [row[0] for row in result]

        logger.info("Successfully retrieved tables from the database")
    return {"tables": table_names}




