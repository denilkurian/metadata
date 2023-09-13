
from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text


router = APIRouter()


# api for Fetch all tables in the database
@router.get("/tables",tags=['metadata'])
def get_tables():
    with engine.connect() as connection:
        query = text("SHOW TABLES;")
        result = connection.execute(query)
        table_names = [row[0] for row in result]
    return {"tables": table_names}




