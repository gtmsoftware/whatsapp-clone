from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal
from pydantic import BaseModel
import jwt
import bcrypt
import datetime

SECRET_KEY = "mysecretkey"

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Register Endpoint
app = FastAPI()

@app.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(username=user.username, password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}

# Login Endpoint
@app.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode(
        {"sub": db_user.username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return {"access_token": token, "token_type": "bearer"}
