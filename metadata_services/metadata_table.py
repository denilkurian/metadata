
from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text
from database.database import get_db_name

router = APIRouter()


# Fetch metadata for a specific table
@router.get("/table/{table_name}/metadata",tags=['metadata'])
def get_table_metadata(table_name: str):
    db_name = get_db_name()  # Call the get_db_name function to retrieve the db_name

    with engine.connect() as connection:
        # Fetch information from the information_schema database
        query = text("""
            SELECT 
                COLUMN_NAME, 
                COLUMN_TYPE, 
                IS_NULLABLE, 
                COLUMN_DEFAULT, 
                COLUMN_KEY, 
                EXTRA, 
                COLUMN_COMMENT 
            FROM 
                information_schema.COLUMNS 
            WHERE 
                TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = :table_name;
        """)
        params = {"db_name": db_name, "table_name": table_name}
        result = connection.execute(query, params)
        column_metadata = [{"Column Name": row[0], "Column Type": row[1], "Is Nullable": row[2], 
                            "Default Value": row[3], "Column Key": row[4], "Extra": row[5], 
                            "Column Comment": row[6]} for row in result]
    return {"metadata": column_metadata}













