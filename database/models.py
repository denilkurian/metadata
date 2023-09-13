
from sqlalchemy import Column, Integer, String,ForeignKey
from database.database import Base
from sqlalchemy.orm import relationship 

### model created for product
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    product_type = Column(String(50))
    price = Column(Integer)
    
    favorites = relationship("Favorite", back_populates="product", cascade="all, delete")


### model for user
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255),unique = True,index = True)
    hashed_password = Column(String(255))



#### model for add to favorites (products)
class Favorite(Base):
    __tablename__ = "favorite"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    product_name = Column(String(50))
    product_type = Column(String(50))
    product_price = Column(Integer)

    product = relationship("Product", back_populates="favorites")












