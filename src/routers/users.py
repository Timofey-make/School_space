from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import delete as sql_delete, and_
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update
from src import init
from src import function

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/register", tags=["Регистрация"])
async def register(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("register.html", {"request": request})

@router.post("/doregister", tags=["Регистрация"])
async def doregister(
    request: Request,
    name: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
):
    login = login.strip()
    name = name.strip()

    if " " in login or " " in name:
        return JSONResponse({"error": "Логин или имя не может содержать пробелы"}, status_code=400)
    
    with Session(init.engine) as conn:
        stmt = select(init.User).where(init.User.username == login)
        data = conn.execute(stmt).fetchall()
        if data:
            return JSONResponse({"error": "Пользователь с таким логином уже есть"}, status_code=400)

        else:
            user = init.User(
                name=name,
                username=login,
                password=function.hash_password(password),
                title="Новичок",
                background="#333333",
                min_points=0
            )
            conn.add(user)
            conn.commit()

    conn = Session(init.engine)
    stmt = select(init.User).where(init.User.username == login)
    id = conn.execute(stmt).fetchall()[0][0].id
    conn.commit()
    conn.close()
    redirect = RedirectResponse(url="/", status_code=303)
    # Устанавливаем куки
    redirect.set_cookie(key="id", value=str(id))
    redirect.set_cookie(key="name", value=function.encrypt(name))
    redirect.set_cookie(key="username", value=function.encrypt(login))
    return redirect

@router.get("/login", tags="Логин")
async def login(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

@router.post("/dologin", tags="Логин")
async def dologin(
    request: Request,
    auth: str = Form(...),
    password: str = Form(...)
):
    error = True
    with Session(init.engine) as conn:
        stmt = select(init.User).where(init.User.username == auth)
        data = conn.execute(stmt).fetchall()
        if data and data[0][0].password == function.hash_password(password):
            # Создаем редирект-ответ
            redirect = RedirectResponse(url="/", status_code=303)
            # Устанавливаем куки
            redirect.set_cookie(key="id", value=str(data[0][0].id))
            redirect.set_cookie(key="name", value=function.encrypt(data[0][0].name))
            redirect.set_cookie(key="username", value=function.encrypt(data[0][0].username))
            return redirect
        else:
            return JSONResponse({"error": "Неверный логин или пароль"}, status_code=400)
        
@router.get("/logout", tags="Выход")
async def logout(request: Request):
    # Создаем редирект-ответ
    redirect = RedirectResponse(url="/", status_code=303)
    # Устанавливаем куки
    redirect.delete_cookie(key="id")
    redirect.delete_cookie(key="name")
    redirect.delete_cookie(key="username")
    return redirect