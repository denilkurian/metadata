from fastapi import FastAPI,HTTPException

app = FastAPI()

import redis
from logging_service.logs import configure_logging,error_middleware
######## router composition in main.py file
from metadata_services import fetch_tables,metadata_table,fetch_summary,lineage_table,metadata_crawler
from backend_services import fast_api,caching_redis
from authentication_authorisation import login_token,registration,verify_otp
from circuitbreaker_config import circuit_breaker
from authentication_authorisation.auth_api import google_auth

from fastapi_session import SessionManager



####### metadata
app.include_router(metadata_crawler.router)
app.include_router(fetch_tables.router)
app.include_router(metadata_table.router)
app.include_router(fetch_summary.router)
app.include_router(lineage_table.router)

###### product data
app.include_router(fast_api.router)
app.include_router(caching_redis.router)

####### authentication
app.include_router(login_token.router)
app.include_router(registration.router)
app.include_router(verify_otp.router)


##### circuit breaker
app.include_router(circuit_breaker.router)

######### caching
# Initialize the Redis connection in the app startup event
@app.on_event("startup")
async def startup_event():
    app.state.redis = redis.Redis(host="localhost", port=6379, db=0)


# Close the Redis connection in the app shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await app.state.redis.wait_closed()


####### loading logging function to the main app
configure_logging() 
app.middleware("http")(error_middleware)


app.include_router(google_auth.router)


# Initialize the SessionManager
manager = SessionManager()



