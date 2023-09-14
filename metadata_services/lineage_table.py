from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import networkx as nx
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoSuchTableError  # Import the exception
from database.database import engine

router = APIRouter()
Session = sessionmaker(bind=engine)

# Endpoint to generate lineage
@router.get("/lineage/{table_name}", tags=['metadata'])
def generate_lineage(table_name: str):
    lineage_graph = nx.DiGraph()

    def explore_table_joins(table_name, parent_table=None):
        try:
            with Session() as session:
                # Check if the table exists in the database
                if not engine.has_table(table_name):
                    raise NoSuchTableError(f"Table '{table_name}' does not exist in the database.")

                query = text(f"SHOW CREATE TABLE {table_name};")
                result = session.execute(query)
                create_table_stmt = result.fetchone()[1]

                # Parse the CREATE TABLE statement to find foreign keys and related tables
                # This part may require more complex parsing based on your specific database schema
                lines = create_table_stmt.split('\n')
                for line in lines:
                    if "FOREIGN KEY" in line:
                        parts = line.strip().split(' ')
                        idx = parts.index("REFERENCES")
                        column_name = parts[idx - 2].strip("(),")
                        related_table_name = parts[idx + 1].strip("(),`")

                        lineage_graph.add_edge(table_name, related_table_name, foreign_key=column_name)

                        explore_table_joins(related_table_name, table_name)
        except NoSuchTableError as e:
            raise HTTPException(status_code=404, detail=str(e))  # Return 404 if the table doesn't exist
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    explore_table_joins(table_name)

    # Serialize the lineage graph as JSON
    lineage_json = nx.readwrite.json_graph.node_link_data(lineage_graph)

    return {"lineage": lineage_json}




