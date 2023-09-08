from fastapi import FastAPI
from sqlalchemy import MetaData,text,func
from database.database import engine

app = FastAPI()

metadata = MetaData()
metadata.bind = engine


# api for Fetch all tables in the database
@app.get("/tables")
def get_tables():
    with engine.connect() as connection:
        query = text("SHOW TABLES;")
        result = connection.execute(query)
        table_names = [row[0] for row in result]
    return {"tables": table_names}


# Fetch metadata for a specific table
@app.get("/table/{table_name}/metadata")
def get_table_metadata(table_name: str):
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
        params = {"db_name": "school", "table_name": table_name}
        result = connection.execute(query, params)
        column_metadata = [{"Column Name": row[0], "Column Type": row[1], "Is Nullable": row[2], 
                            "Default Value": row[3], "Column Key": row[4], "Extra": row[5], 
                            "Column Comment": row[6]} for row in result]
    return {"metadata": column_metadata}



# Generate a summary for a specific table
@app.get("/table/{table_name}/summary")
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



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)



import networkx as nx

# Endpoint to generate lineage
@app.get("/lineage/{table_name}")
def generate_lineage(table_name: str):
    # Initialize a directed graph for lineage
    lineage_graph = nx.DiGraph()

    # Function to recursively explore table joins
    def explore_table_joins(table_name, parent_table=None):
        with engine.connect() as connection:
            query = text(f"SHOW CREATE TABLE {table_name};")
            result = connection.execute(query)
            create_table_stmt = result.fetchone()[1]

            # Parse the CREATE TABLE statement to find foreign keys and related tables
            # This part may require more complex parsing based on your specific database schema
            # Here, we assume foreign keys are defined as FOREIGN KEY (column_name) REFERENCES related_table_name
            lines = create_table_stmt.split('\n')
            for line in lines:
                if "FOREIGN KEY" in line:
                    parts = line.strip().split(' ')
                    idx = parts.index("REFERENCES")
                    column_name = parts[idx - 2].strip("(),")
                    related_table_name = parts[idx + 1].strip("(),`")

                    # Add the edge to the lineage graph
                    lineage_graph.add_edge(table_name, related_table_name, foreign_key=column_name)

                    # Recursively explore related tables
                    explore_table_joins(related_table_name, table_name)

    # Start exploring the table joins
    explore_table_joins(table_name)

    # Serialize the lineage graph as JSON
    lineage_json = nx.readwrite.json_graph.node_link_data(lineage_graph)

    return {"lineage": lineage_json}















