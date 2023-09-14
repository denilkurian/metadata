
from fastapi import APIRouter,HTTPException,Depends
import redis,json
from sqlalchemy.orm import class_mapper,Session
from database.models import Product
from database.database import get_db
from main import app


router = APIRouter()



def serialize_product(product):
    columns = [column.key for column in class_mapper(Product).columns]
    product_dict = {col: getattr(product, col) for col in columns}
    return product_dict

def fetch_cached_product(redis_conn, product_name: str):
    cached_data = redis_conn.get(product_name)
    if cached_data:
        return json.loads(cached_data)
    return None


def fetch_product_from_db(db: Session, product_name: str):
    return db.query(Product).filter(Product.name == product_name).first()


def cache_product_in_redis(redis_conn, product_name: str, serialized_product, ttl_seconds: int = 60):
    redis_conn.setex(product_name,ttl_seconds, json.dumps(serialized_product))
    print(f"Product cached in Redis: {product_name}")


###### to get the product and add to cache
@router.get("/products/{product_name}", tags=['redis'])
async def get_product(product_name: str, db: Session = Depends(get_db)):
    # Attempt to fetch the product from Redis
    cached_product = fetch_cached_product(app.state.redis, product_name)
    if cached_product:
        print("Data is from cache")
        return cached_product

    # Fetch from MySQL
    product = fetch_product_from_db(db, product_name)
    if product:
        # Serialize the fetched data
        serialized_product = serialize_product(product)

        # Cache the serialized data in Redis
        cache_product_in_redis(app.state.redis, product_name, serialized_product, ttl_seconds=60)
        
        print("Data is from MySQL")
        return serialized_product

    raise HTTPException(status_code=404, detail="Product not found")   



############### function to  flush all cache from redis
@router.get("/flush-cache", tags=['redis'])
async def flush_cache():
    app.state.redis.flushdb()  # This will clear the entire Redis database
    return {"message": "Cache flushed"}







