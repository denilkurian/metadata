from pydantic import BaseModel
from fastapi import Depends, HTTPException,APIRouter
from sqlalchemy.orm import Session
from database.models import Product ,User
from database.database import engine, Base,get_db
from typing import List
from authentication_authorisation.authorisation import get_current_user


Base.metadata.create_all(bind=engine, checkfirst=True)


router = APIRouter()


####### for validation,serialisation of models
class ProductCreate(BaseModel):
    name: str
    product_type: str
    price: int


class ProductResponse(ProductCreate):
    id: int


class UserCreate(BaseModel):
    username: str
    email : str
    hashed_password: str
    


### create a new product
@router.post("/products/", response_model=ProductResponse,tags=['product'])
def create_product(user: ProductCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    db_user = Product(**user.dict()) 
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



### update a product
@router.put("/products/{product_id}", response_model=ProductResponse ,tags=['product'])
def update_product(product_id: int, updated_user: ProductCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    db_user = db.query(Product).filter(Product.id == product_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if updated_user.name:
        db_user.name = updated_user.name
    if updated_user.product_type:
        db_user.product_type = updated_user.product_type
    if updated_user.price:
        db_user.price = updated_user.price

    db.commit()
    db.refresh(db_user)
    return db_user




### get(list) all products from database
@router.get("/products/", response_model=List[ProductResponse] ,tags=['product'])
def get_all_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


#### delete a product
@router.delete("/products/{product_id}",tags=['product'])
def delete_product(product_id:int,db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):
     user = db.query(Product).filter(Product.id == product_id).first()
     if user is None:
         raise HTTPException(status_code=404,detail="Product not found")
     db.delete(user)
     db.commit()
     return  f"{product_id} deleted successfully"



from database.models import Favorite

####### aad to favourites list for each user separately
@router.post("/products/{product_id}/add_favorite/",tags=['product'])
def add_to_favorites(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    favorite = Favorite(
        user_id=current_user.id,
        product_id=product.id,
        product_name=product.name,
        product_type=product.product_type,
        product_price=product.price
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {"message": "Product added to favorites"}



class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product_name: str
    product_type: str
    product_price: int

### list of added favorites for each user
@router.get("/favorites/", response_model=List[FavoriteResponse],tags=['product'])
def get_user_favorite_products(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite_products = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorite_products







