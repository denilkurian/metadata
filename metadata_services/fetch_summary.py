
from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text
from database.database import get_db_name

router = APIRouter()


# Generate a summary for a specific table
@router.get("/table/{table_name}/summary" ,tags=['metadata'])
def get_table_metadata_summary(table_name: str):
    db_name = get_db_name()  # Set the database name here

    with engine.connect() as connection:
        # Check if the table exists
        check_table_query = text("""
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = :db_name
            AND TABLE_NAME = :table_name;
        """)
        check_table_params = {"db_name": db_name, "table_name": table_name}
        existing_table = connection.execute(check_table_query, check_table_params).scalar()

        if existing_table is None:
            return {"error": f"Table '{table_name}' does not exist in database '{db_name}'"}

        # Fetch table size (number of rows)
        count_query = text(f"SELECT COUNT(*) FROM {table_name};")
        row_count = connection.execute(count_query).scalar()

        # Fetch table creation date
        create_time_query = text("""
            SELECT CREATE_TIME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = :db_name
            AND TABLE_NAME = :table_name;
        """)
        create_time_params = {"db_name": db_name, "table_name": table_name}
        create_time = connection.execute(create_time_query, create_time_params).scalar()
        table_description = ""

        # Create a metadata summary
        metadata_summary = {
            "Database Name": db_name,
            "Table Name": table_name,
            "Table Size": row_count,
            "Table Creation Date": create_time,
            "Table Description": table_description,
        }

        return {"metadata_summary": metadata_summary}









