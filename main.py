# from fastapi import FastAPI,Request,status
# from App.Routes.Auth_Users.login_register import auth_router
# from App.Database.init_db import create_tables
# from App.Routes.Auth_Users.profile import profile_router
# from App.Routes.Menu_Routes.menu_routes import menu_router
# from sqlalchemy.exc import SQLAlchemyError,IntegrityError
# from fastapi.responses import JSONResponse
# import uvicorn

# #=====================Creating App===================
# app=FastAPI()

# #===============Running Data base Tables==============
# create_tables()

# #================Error Handling in main.py==================

# # 1. IntegrityError Handler (Fixing signature and return)
# @app.exception_handler(IntegrityError)
# async def database_integrity_error(request: Request, exc: IntegrityError):
#     print(f"Integrity Error: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         content={"detail": "Database constraint violation (e.g., duplicate entry or invalid reference)."}
#     )

# # 2. SQLAlchemy General Error Handler
# @app.exception_handler(SQLAlchemyError)
# async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
#     print(f"Database Error: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"detail": "A database connection or query error occurred."}
#     )

# # 3. Global Handler (Alwayys Keep it in End)
# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     print(f"Global Unexpected Error: {exc}")
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"detail": "An internal server error occurred."},
#     )
# #================Including Router in main.py===============    
# app.include_router(auth_router,prefix='/auth',tags=['Authentication'])
# app.include_router(profile_router,prefix="/profile",tags=["Profile"])
# app.include_router(menu_router,prefix="/menu",tags=["Menu Management"])

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)

from enum import Enum
from typing import Optional
from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uvicorn

# Aapki Base aur get_db imports
from App.Database.database import Base, get_db 

# 1. Enum Class (str se inherit karna zaroori hai dropdown ke liye)
class PizzaCatEnum(str, Enum):
    SIGNATURE = "Signature & Classics"
    MEAT_FEAST = "Meat Feast"
    SPICY = "Hot & Spicy"

# 2. Database Model
class Category_M(Base):
    __tablename__ = "categories" # Spelling theek kar di
    __table_args__ = {'extend_existing': True} # Taake woh purana error na aaye
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(PizzaCatEnum), unique=True, nullable=False)
    description = Column(String(500), nullable=True)

# 3. Pydantic Schemas
class Category_Base(BaseModel):
    name: PizzaCatEnum  # Yahan naam bilkul Enum class wala hona chahiye
    description: Optional[str] = None

    model_config = {"from_attributes": True}

class Category_Res(Category_Base):
    id: int

# 4. FastAPI App aur Endpoints
app = FastAPI()

@app.get("/categories", response_model=list[Category_Res])
def get_all_categories(db: Session = Depends(get_db)):
    # Yahan 'Category_M' aayega kyunke upar wahi define kiya hai
    categories = db.query(Category_M).all()
    return categories

# Test ke liye POST endpoint (Dropdown check karne ke liye)
@app.post("/categories", response_model=Category_Res)
def create_category(category: Category_Base, db: Session = Depends(get_db)):
    new_cat = Category_M(**category.model_dump())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)