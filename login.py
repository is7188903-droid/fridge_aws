from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from user import create_user, hash_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request, msg: str = ""):
    return templates.TemplateResponse(request, "login.html", {"msg": msg, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    found = db.query(User).filter(User.username == username).first()
    if not found or found.password != hash_password(password):
        return templates.TemplateResponse(request, "login.html",
                                          {"msg": "", "error": "아이디 또는 비밀번호가 틀렸습니다."})
    request.session["user_id"] = found.id
    request.session["username"] = found.username
    return RedirectResponse("/fridge", status_code=303)

@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"error": None})

@router.post("/signup")
def signup(request: Request, username: str = Form(...), password: str = Form(...),
           password2: str = Form(...), db: Session = Depends(get_db)):
    if password != password2:
        return templates.TemplateResponse(request, "signup.html", {"error": "비밀번호가 일치하지 않습니다."})
    try:
        create_user(db, username, password)   # user.py의 POST 생성 로직 재사용
    except HTTPException as e:
        return templates.TemplateResponse(request, "signup.html", {"error": e.detail})
    return RedirectResponse("/login?msg=ok", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
