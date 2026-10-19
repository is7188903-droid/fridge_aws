import hashlib
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    password: str

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def create_user(db: Session, username: str, password: str) -> User:
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    new_user = User(username=username, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 기존 POST 통신 방식의 회원 생성 API
@router.post("/")
def post_user(data: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(db, data.username, data.password)
    return {"id": new_user.id, "username": new_user.username}

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return [{"id": u.id, "username": u.username} for u in db.query(User).all()]
