
from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text


router = APIRouter()


# Generate a summary for a specific table
@router.get("/table/{table_name}/summary")
def get_table_metadata_summary(table_name: str):
    with engine.connect() as connection:
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
        create_time_params = {"db_name": "school", "table_name": table_name}
        create_time = connection.execute(create_time_query, create_time_params).scalar()

        
        table_description = "Table description goes here"  

    # Create a metadata summary
    metadata_summary = {
        "Table Name": table_name,
        "Table Size": row_count,
        "Table Creation Date": create_time,
        "Table Description": table_description,
    }

    return {"metadata_summary": metadata_summary}


