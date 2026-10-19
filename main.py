from datetime import date
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Food
import user
import login

Base.metadata.create_all(bind=engine)

app = FastAPI(title="냉장고 음식 관리")
app.add_middleware(SessionMiddleware, secret_key="fridge-final-project-secret")
app.include_router(user.router)
app.include_router(login.router)
templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    return RedirectResponse("/login")

@app.get("/fridge")
def fridge_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    foods = db.query(Food).filter(Food.user_id == user_id).order_by(Food.expiry_date).all()
    return templates.TemplateResponse(request, "fridge.html", {
        "username": request.session.get("username"),
        "foods": foods,
        "today": date.today(),
    })

@app.post("/fridge/add")
def add_food(request: Request, name: str = Form(...), quantity: int = Form(1),
             expiry_date: str = Form(""), db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    food = Food(name=name, quantity=quantity,
                expiry_date=date.fromisoformat(expiry_date) if expiry_date else None,
                user_id=user_id)
    db.add(food)
    db.commit()
    return RedirectResponse("/fridge", status_code=303)

@app.post("/fridge/delete/{food_id}")
def delete_food(food_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    food = db.query(Food).filter(Food.id == food_id, Food.user_id == user_id).first()
    if food:
        db.delete(food)
        db.commit()
    return RedirectResponse("/fridge", status_code=303)
