from fastapi import FastAPI


app = FastAPI()


######## loading of crawling of metadata from database
from meta import meta_crawl
from api import fetch_tables,metadata_table,fetch_summary,lineage_table


app.include_router(meta_crawl.router)
app.include_router(fetch_tables.router)
app.include_router(metadata_table.router)
app.include_router(fetch_summary.router)
app.include_router(lineage_table.router)

