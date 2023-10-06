
from sqlalchemy import Column, Integer, String,ForeignKey,DateTime
from database.database import Base
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from datetime import timedelta


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
    first_name = Column(String(255),nullable = False,index = True)
    last_name = Column(String(255), index = True)
    date_of_birth = Column(DateTime)
    sex = Column(String(50))
    email = Column(String(255),unique = True,index = True,nullable = False)
    hashed_password = Column(String(255))

    google_auth = relationship("GoogleAuthUser", back_populates="user")



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


########## temporarily saving otp data
class OTPVerification(Base):
    __tablename__ = "otp_verification"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    otp = Column(String(50))
    expiration = Column(DateTime, default=func.now() + timedelta(minutes=5))
    first_name = Column(String(50))
    last_name = Column(String(50))
    sex = Column(String(50))
    date_of_birth = Column(DateTime)



class GoogleAuthUser(Base):
    __tablename__ = "google_auth_user"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(255), unique=True, nullable=False)  # Google's unique identifier for the user
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # ForeignKey to link with your existing user model

    # Relationship to your existing User model
    user = relationship("User", back_populates="google_auth")





