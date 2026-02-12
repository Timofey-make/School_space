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

@router.post("/delete_account")
async def delete_account(
    request: Request,
    id: int = Form(...),
):
    cookie_user_id = request.cookies.get("id")
    if cookie_user_id is None:
        return RedirectResponse("/", status_code=303)

    cookie_user_id = int(cookie_user_id)

    with Session(init.engine) as session:

        # Определяем кто делает запрос
        stmt = select(init.User).where(init.User.id == cookie_user_id)
        current_user = session.scalar(stmt)

        # Определяем кого удаляем
        stmt = select(init.User).where(init.User.id == id)
        target_user = session.scalar(stmt)

        if not target_user or target_user.id == 1:
            return RedirectResponse("/", status_code=303)
        
        # Проверка прав
        if not current_user or (current_user.id != 1 and not current_user.is_admin) and (id != cookie_user_id):
            return RedirectResponse("/", status_code=303)

        # Получаем имя удаляемого пользователя
        target_username = target_user.username

        # Удаляем пользователя
        session.execute(sql_delete(init.User).where(init.User.id == id))
        session.commit()

        # Удаляем вопросы удалённого пользователя
        session.execute(
            sql_delete(init.Question).where(init.Question.owner == target_username)
        )
        session.commit()

        # Удаляем комментарии удалённого пользователя
        session.execute(
            sql_delete(init.Comment).where(init.Comment.owner == target_username)
        )
        session.commit()

    # Если пользователь удалил СВОЙ аккаунт — выходим
    if id == cookie_user_id:
        return RedirectResponse("/users/logout", status_code=303)

    # Если админ удалил чужой аккаунт
    return RedirectResponse("/", status_code=303)