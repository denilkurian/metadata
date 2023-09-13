from database.database import engine
from fastapi import APIRouter
from sqlalchemy import text
import networkx as nx

router = APIRouter()


# Endpoint to generate lineage
@router.get("/lineage/{table_name}")
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
