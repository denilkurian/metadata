from fastapi import FastAPI


app = FastAPI()


######## router composition in main.py file
from metadata_services import fetch_tables,metadata_table,fetch_summary,lineage_table,metadata_crawler
from backend_services import fast_api,caching_redis
from authentication_authorisation import login_token,registration

#######metadata
app.include_router(metadata_crawler.router)
app.include_router(fetch_tables.router)
app.include_router(metadata_table.router)
app.include_router(fetch_summary.router)
app.include_router(lineage_table.router)

######product data
app.include_router(fast_api.router)
app.include_router(caching_redis.router)

#######authentication
app.include_router(login_token.router)
app.include_router(registration.router)



import redis
#########3 caching
# Initialize the Redis connection in the app startup event
@app.on_event("startup")
async def startup_event():
    app.state.redis = redis.Redis(host="localhost", port=6379, db=0)


# Close the Redis connection in the app shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await app.state.redis.wait_closed()


