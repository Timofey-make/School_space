from fastapi import FastAPI, Request, Form, Response, requests
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime
from sqlalchemy import delete as sql_delete, and_
from sqlalchemy.orm import Session
import time
import os
import uuid
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from requests import session
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update
import uuid
import shutil
from fastapi import UploadFile, File
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Depends
from . import init
from . import function
import sqlite3
import uvicorn
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.routers import users, questions, api, answers, admin

app = FastAPI()
from fastapi.staticfiles import StaticFiles
import os

app.include_router(users.router)
app.include_router(questions.router)
app.include_router(api.router)
app.include_router(answers.router)
app.include_router(admin.router)

init.Base.metadata.create_all(init.engine)
static_dir = os.path.join(os.path.dirname(__file__), "static")

if not os.path.exists(static_dir):
    print("Папка static не найдена по пути:", static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

async def check_user_exists(request: Request):
    user_id = request.cookies.get("id")
    if user_id:
        try:
            with Session(init.engine) as session:
                user = session.get(init.User, int(user_id))
                if not user:
                    response = RedirectResponse(url="/users/logout", status_code=303)
                    response.delete_cookie(key="id")
                    response.delete_cookie(key="name")
                    response.delete_cookie(key="username")
                    return response
        except (ValueError, TypeError):
            response = RedirectResponse(url="/users/logout", status_code=303)
            response.delete_cookie(key="id")
            response.delete_cookie(key="name")
            response.delete_cookie(key="username")
            return response
    return None

@app.exception_handler(404)
async def not_found(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )
 
@app.get("/", tags="Главная")
async def main(request: Request, user_check = Depends(check_user_exists)):
    if isinstance(user_check, RedirectResponse):
        return user_check
        
    if request.cookies.get("id"):
        return templates.TemplateResponse("main.html", {"request": request,
                                                        "username": function.decrypt(request.cookies.get("username")),
                                                        "name": function.decrypt(request.cookies.get("name")),
                                                        "id": request.cookies.get("id"),})
    else:
        return templates.TemplateResponse("main.html", {"request": request,
                                                        "username": None,
                                                        "name": None,})

@app.get("/question/{note_id}", tags=["Страница вопроса"])
async def question_page(request: Request, note_id: int):
    try:
        # Проверяем, авторизован ли пользователь
        user_id = request.cookies.get("id")

        with Session(init.engine) as conn:
            # Получаем данные вопроса
            stmt = select(
                init.Question.owner,
                init.Question.owner_name,
                init.Question.owner_id,
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.id,
                init.Question.created_at,
                init.Question.image_path,
                init.Question.edited,
            ).where(init.Question.id == note_id)
            question_data = conn.execute(stmt).fetchone()

            # Если вопрос не найден — редиректим
            if not question_data:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            # Распаковываем результат в список
            result = [
                question_data.owner,
                question_data.owner_name,
                question_data.subject,
                question_data.grade,
                question_data.description,
                question_data.id,
                question_data.created_at,
                question_data.image_path,
                question_data.edited,
                question_data.owner_id,
                ]

            # 🔹 Обрабатываем изображения (если несколько — через запятую)
            image_urls = []
            if question_data.image_path:
                # храним только "images/filename.png"
                image_urls = [p.split("/static/")[-1] for p in question_data.image_path.split(",")]

        # --- Если пользователь авторизован ---
        if user_id:
            with Session(init.engine) as conn:
                # Получаем данные аккаунта автора вопроса
                stmt = select(
                    init.User.id,
                    init.User.name,
                    init.User.title,
                    init.User.background,
                    init.User.is_admin,
                ).where(init.User.username == result[0])
                data = conn.execute(stmt).fetchone()

                account = [
                    data.id,
                    data.name,
                    result[0],
                    data.title,
                    data.background,
                    data.is_admin,
                ]

                # Получаем комментарии
                stmt = select(
                    init.Comment.owner,
                    init.Comment.owner_id,
                    init.Comment.description
                ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
                comment_data = conn.execute(stmt).fetchall()

                comments = [
                    {"owner": row.owner, "description": row.description, "owner_id": row.owner_id,}
                    for row in comment_data
                ]
            return templates.TemplateResponse("answer.html", {
                "request": request,
                "id": request.cookies.get("id"),
                "username": function.decrypt(request.cookies.get("username")),
                "name": function.decrypt(request.cookies.get("name")),
                "account": account,
                "result": result,
                "comments": comments,
                "images": image_urls,
            })

        # --- Если пользователь не авторизован ---
        else:
            with Session(init.engine) as conn:
                stmt = select(
                    init.Comment.owner,
                    init.Comment.owner_id,
                    init.Comment.description
                ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
                comment_data = conn.execute(stmt).fetchall()

                comments = [
                    {"owner": row.owner, "description": row.description, "owner_id": row.owner_id}
                    for row in comment_data
                ]
            return templates.TemplateResponse("answer.html", {
                "request": request,
                "result": result,
                "comments": comments,
                "images": image_urls,
            })

    except Exception as e:
        raise HTTPException(status_code=422, detail="Некоректный ввод")
   
# @app.get("/profile/{username}", tags=["Профиль"])
# async def profile(request: Request, username: str):
#     cookie_username = request.cookies.get("username")
#     user_is_admin = False  # по умолчанию гость не админ

#     if cookie_username:
#         try:
#             decrypted_username = function.decrypt(cookie_username)
#         except:
#             decrypted_username = None
#     else:
#         decrypted_username = None

#     with Session(init.engine) as conn:

#         # Если пользователь авторизован — узнаём, он админ или нет
#         if decrypted_username:
#             stmt = select(init.User.is_admin).where(init.User.username == decrypted_username)
#             result = conn.execute(stmt).fetchone()
#             if result:
#                 user_is_admin = result.is_admin

#         # Получаем данные профиля, на который заходим
#         stmt = select(
#             init.User.id,
#             init.User.name,
#             init.User.title,
#             init.User.background,
#             init.User.is_admin,
#         ).where(init.User.username == username)

#         data = conn.execute(stmt).fetchone()
#         if not data:
#             raise HTTPException(status_code=404, detail="Пользователь не найден")

#         account = [data.id, data.name, username, data.title, data.background, data.is_admin]

#         # вопросы пользователя
#         stmt = select(
#             init.Question.id,
#             init.Question.owner,
#             init.Question.owner_name,
#             init.Question.subject,
#             init.Question.grade,
#             init.Question.description,
#             init.Question.created_at,
#         ).where(init.Question.owner == username).order_by(init.Question.id.desc())

#         questions_raw = conn.execute(stmt).fetchall()

#         questions = [
#             {
#                 "id": row.id,
#                 "username": row.owner,
#                 "name": row.owner_name,
#                 "subject": row.subject,
#                 "grade": row.grade,
#                 "text": row.description,
#                 "created_at": row.created_at.isoformat() if row.created_at else None,
#             }
#             for row in questions_raw
#         ]

#     # Рендер: если авторизован
#     if cookie_username:
#         return templates.TemplateResponse(
#             "profile.html",
#             {
#                 "request": request,
#                 "account": account,
#                 "questions": questions,
#                 "name": function.decrypt(request.cookies.get("name")),
#                 "username": decrypted_username,
#                 "id": request.cookies.get("id"),
#                 "admin": user_is_admin,
#             }
#         )

#     # Рендер для гостя
#     return templates.TemplateResponse(
#         "profile.html",
#         {
#             "request": request,
#             "account": account,
#             "questions": questions,
#         }
#     )

@app.get("/profile/{id}", tags=["Профиль"])
async def profile(request: Request, id: int):
    # Узнаем id зашедшего в профиль человека и ставим флаг что изначально человек зашедший в профиль
    # не админ
    guest_id = request.cookies.get("id")
    user_is_admin = False

    if guest_id:
        guest_username = function.decrypt(request.cookies.get("username"))
        with Session(init.engine) as conn:
            # Проверяем админ ли пользователь
            stmt = select(init.User.is_admin).where(init.User.id == guest_id)
            result = conn.execute(stmt).fetchone()
            if result:
                user_is_admin = result.is_admin
        
        # Достаем из бд данные о владельце профиля 
        stmt = select(
            init.User.username,
            init.User.name,
            init.User.title,
            init.User.background,
            init.User.is_admin,
        ).where(init.User.id == id)

        data = conn.execute(stmt).fetchone()
        if not data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        account = [id, data.name, data.username, data.title, data.background, data.is_admin]            

        # Доставем из бд вопросы влыдельце пользователя
        stmt = select(
            init.Question.id,
            init.Question.owner,
            init.Question.owner_name,
            init.Question.subject,
            init.Question.grade,
            init.Question.description,
            init.Question.created_at,
        ).where(init.Question.owner == account[2]).order_by(init.Question.id.desc())

        data = conn.execute(stmt).fetchall()

        questions = [
            {
                "id": row.id,
                "username": row.owner,
                "name": row.owner_name,
                "subject": row.subject,
                "grade": row.grade,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in data
        ]
    
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "account": account,
                "questions": questions,
                "name": function.decrypt(request.cookies.get("name")),
                "username": guest_username,
                "id": guest_id,
                "admin": user_is_admin,
            }
        )
    return templates.TemplateResponse(
    "profile.html",
    {
        "request": request,
        "account": account,
        "questions": questions,
    }
)
if __name__ == "__main__":
    init.Base.metadata.create_all(init.engine)
    uvicorn.run("main:app", reload=True)