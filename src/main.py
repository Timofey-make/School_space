from fastapi import FastAPI, Request, Form, Response, requests
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote
from datetime import datetime
from sqlalchemy import delete as sql_delete, and_
from sqlalchemy.orm import Session
import time
from requests import session
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import update
import uuid
import shutil
from fastapi import UploadFile, File

from . import init
from . import function
import sqlite3
import uvicorn

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

app = FastAPI()
from fastapi.staticfiles import StaticFiles
import os

init.Base.metadata.create_all(init.engine)
# Абсолютный путь до папки static
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Проверим на всякий случай, что папка существует
if not os.path.exists(static_dir):
    print("⚠️ Папка static не найдена по пути:", static_dir)

# Подключаем статику
app.mount("/static", StaticFiles(directory=static_dir), name="static")

BASE_DIR = Path(__file__).resolve().parent
# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")



@app.get("/logout", tags="Выход")
async def logout(request: Request):
    # Создаем редирект-ответ
    redirect = RedirectResponse(url="/", status_code=303)
    # Устанавливаем куки
    redirect.delete_cookie(key="id")
    redirect.delete_cookie(key="name")
    redirect.delete_cookie(key="username")
    return redirect

@app.get("/register", tags="Регистрация")
async def register(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("register.html", {"request": request})

@app.post("/doregister", tags="Регистрация")
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

@app.get("/login", tags="Логин")
async def login(request: Request):
    if request.cookies.get("id"):
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("auth.html", {"request": request})

@app.post("/dologin", tags="Логин")
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

@app.get("/add", tags="Добавить вопрос")
async def add(request: Request):
    if request.cookies.get("id"):
        return templates.TemplateResponse("add_question.html", {"request": request})
    else:
        return RedirectResponse(url="/login", status_code=303)

import os
import uuid
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session


@app.post("/doadd", tags=["Добавить вопрос"])
async def doadd(
    request: Request,
    subject: str = Form(...),
    grade: str = Form(...),
    description: str = Form(""),
    images: list[UploadFile] = File(None)
):
    try:
        # Проверка на пустой вопрос
        if not description.strip() and (not images or len(images) == 0):
            return RedirectResponse(url="/?error=empty_content", status_code=303)

        saved_paths = []

        # Создаем папку для изображений, если не существует
        # вместо "./SchoolProject/src/static/images"
        save_dir = os.path.join(static_dir, "images")
        os.makedirs(save_dir, exist_ok=True)


        # Обрабатываем каждое изображение
        if images:
            for image in images:
                if not image.filename:
                    continue

                # Проверяем тип файла
                if not image.content_type.startswith("image/"):
                    continue

                # Генерируем уникальное имя файла
                ext = image.filename.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                filepath = os.path.join(save_dir, filename)

                # Сохраняем файл
                with open(filepath, "wb") as f:
                    f.write(await image.read())

                # Добавляем путь в список
                saved_paths.append(f"/static/images/{filename}")

        # Можно хранить пути как JSON, список или строку через запятую
        image_paths_str = ",".join(saved_paths) if saved_paths else None

        # Добавляем запись в базу
        with Session(init.engine) as conn:
            question = init.Question(
                owner=function.decrypt(request.cookies.get("username")),
                owner_name=function.decrypt(request.cookies.get("name")),
                subject=subject,
                grade=grade,
                description=description.strip(),
                image_path=image_paths_str
            )
            conn.add(question)
            conn.commit()

            # Повышение уровня пользователя и т.п.
            function.upgrade(request.cookies.get("id"))
            function.upgrade_title(request.cookies.get("id"))

        # Успешный редирект
        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        print(f"Ошибка при добавлении вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)


@app.get("/api/answers", tags=["API"])
async def get_answers():
    with Session(init.engine) as conn:
        stmt = select(
            init.Comment.id,
            init.Comment.question_id,
            init.Comment.owner,
            init.Comment.description,
            init.Comment.created_at,
            init.Comment.image_filename,
        ).order_by(init.Comment.id.desc())
        data = conn.execute(stmt).fetchall()

        questions = []
        for row in data:
            stmt = select(init.User.name).where(init.User.username == row.owner)
            data = conn.execute(stmt).fetchall()
            questions.append({
                "id": row.id,
                "question_id": row.question_id,
                "name": data[0].name,
                "username": row.owner,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "images": row.image_filename,
            })
        return JSONResponse(content=questions)

@app.get("/api/like", tags=["API"])
async def get_like():
    with Session(init.engine) as conn:
        stmt = select(
            init.Like.question_id,
            init.Like.who,
        ).order_by(init.Question.id.desc())
        data = conn.execute(stmt).fetchall()

        like = []
        for row in data:
            like.append({
                "question_id": row.question_id,
                "who": row.who,
            })
        return JSONResponse(content=like)

from fastapi.responses import JSONResponse
from sqlalchemy import select
import json

@app.get("/api/questions", tags=["API"])
async def get_questions():
    with Session(init.engine) as conn:
        stmt = select(
            init.Question.id,
            init.Question.owner,
            init.Question.owner_name,
            init.Question.subject,
            init.Question.grade,
            init.Question.description,
            init.Question.created_at,
            init.Question.like,
            init.Question.image_path,  # <-- добавляем поле с путями
        ).order_by(init.Question.id.desc())
        data = conn.execute(stmt).fetchall()

        questions = []
        for row in data:
            # если image_path хранится как строка с запятыми — превращаем в массив
            image_list = []
            if row.image_path:
                image_list = [img.strip() for img in row.image_path.split(",") if img.strip()]

            questions.append({
                "id": row.id,
                "username": row.owner,
                "name": row.owner_name,
                "subject": row.subject,
                "grade": row.grade,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like": row.like,
                "images": image_list,  # <-- теперь тут массив путей
            })

        return JSONResponse(content=questions)

    
@app.get("/api/users", tags=["API"])
async def get_users():
    with Session(init.engine) as conn:
        stmt = select(
            init.User.id,
            init.User.username,
            init.User.name,
            init.User.min_points,
            init.User.title,
            init.User.background
        )
        data = conn.execute(stmt).fetchall()

        users = []
        for row in data:
            users.append({
                "id": row.id,
                "username": row.username,
                "name": row.name,
                "min_points": row.min_points,
                "title": row.title,
                "background": row.background
            })
        return JSONResponse(content=users)


@app.get("/", tags="Главная")
async def main(request: Request):
        if request.cookies.get("id"):
            return templates.TemplateResponse("main.html", {"request": request,
                                                            "username": function.decrypt(request.cookies.get("username")),
                                                            "name": function.decrypt(request.cookies.get("name")),})
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
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.id,
                init.Question.created_at,
                init.Question.image_path,
            ).where(init.Question.id == note_id)
            question_data = conn.execute(stmt).fetchone()

            # Если вопрос не найден — редиректим
            if not question_data:
                return RedirectResponse(url="/", status_code=303)

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
                    init.Comment.description
                ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
                comment_data = conn.execute(stmt).fetchall()

                comments = [
                    {"owner": row.owner, "description": row.description}
                    for row in comment_data
                ]

            return templates.TemplateResponse("answer.html", {
                "request": request,
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
                    init.Comment.description
                ).where(init.Comment.question_id == note_id).order_by(init.Comment.id.desc())
                comment_data = conn.execute(stmt).fetchall()

                comments = [
                    {"owner": row.owner, "description": row.description}
                    for row in comment_data
                ]

            return templates.TemplateResponse("answer.html", {
                "request": request,
                "result": result,
                "comments": comments,
                "images": image_urls,
            })

    except Exception as e:
        print(f"Ошибка при загрузке страницы вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

@app.post("/addcomment", tags=["Добавить комментарий"])
async def addcomment(
    request: Request,
    comment: str = Form(...),
    id: int = Form(...),
    images: list[UploadFile] = File(None),
):
    try:
        # Убираем пробелы и переводы строк
        clean_comment = comment.strip()

        # Если комментарий пустой после очистки и нет картинок — не добавляем
        if not clean_comment and (not images or not any(img.filename for img in images)):
            return RedirectResponse(url=f'/question/{id}', status_code=303)

        saved_paths = []
        
        # Обрабатываем загруженные картинки, если они есть
        if images:
            # Создаем папку для изображений комментариев
            save_dir = os.path.join(static_dir, "images", "comments")
            os.makedirs(save_dir, exist_ok=True)

            for image in images:
                if not image.filename:
                    continue
                
                # Проверяем, что это действительно изображение
                if not image.content_type.startswith('image/'):
                    continue
                
                # Генерируем уникальное имя файла
                ext = image.filename.split('.')[-1]
                filename = f"comment_{uuid.uuid4()}.{ext}"
                filepath = os.path.join(save_dir, filename)
                
                # Сохраняем файл
                with open(filepath, "wb") as f:
                    f.write(await image.read())
                
                # Добавляем путь в список
                saved_paths.append(f"/static/images/comments/{filename}")

        # Преобразуем список путей в строку для хранения в БД
        image_paths_str = ",".join(saved_paths) if saved_paths else None

        with Session(init.engine) as conn:
            comments = init.Comment(
                question_id=id,
                owner=function.decrypt(request.cookies.get("username")),
                description=clean_comment,
                image_filename=image_paths_str,  # Сохраняем пути к изображениям
            )
            conn.add(comments)
            conn.commit()
        
        # Повышение уровня пользователя
        function.upgrade(request.cookies.get("id"))
        function.upgrade_title(request.cookies.get("id"))

        return RedirectResponse(url=f'/question/{id}', status_code=303)
    
    except Exception as e:
        print(f"Ошибка при добавлении комментария: {e}")
        return RedirectResponse(url=f'/question/{id}?error=server_error', status_code=303)
    
@app.get("/profile/{username}", tags=["Профиль"])
async def profile(request: Request, username: str):
    with Session(init.engine) as conn:
            stmt = select(
                init.User.id,
                init.User.name,
                init.User.title,
                init.User.background,
                init.User.is_admin,
            ).where(init.User.username == username)
            data = conn.execute(stmt).fetchall()
            account = [data[0].id, data[0].name, username, data[0].title, data[0].background, data[0].is_admin,]
            stmt = select(
                init.Question.id,
                init.Question.owner,
                init.Question.owner_name,
                init.Question.subject,
                init.Question.grade,
                init.Question.description,
                init.Question.created_at,
            ).where(init.Question.owner == username).order_by(init.Question.id.desc())
            data = conn.execute(stmt).fetchall()

            questions = []
            for row in data:
                questions.append({
                    "id": row.id,
                    "username": row.owner,
                    "name": row.owner_name,
                    "subject": row.subject,  
                    "grade": row.grade,
                    "text": row.description,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                })
    if request.cookies.get('id'):
        return templates.TemplateResponse(
            "profile.html", 
            {"request": request, "account": account, "questions": questions, "name": function.decrypt(request.cookies.get("name")), "username": function.decrypt(request.cookies.get("username")), "id": request.cookies.get("id")}
        )
    return templates.TemplateResponse(
    "profile.html", 
    {"request": request, "account": account, "questions": questions})


@app.post("/delete", tags=["Удаление вопроса"])
async def delete_question(
    request: Request,
    owner: str = Form(...),
    question_id: str = Form(...),
):
    print(question_id)
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = sql_delete(init.Question).where(
                and_(
                    init.Question.owner == current_user,
                    init.Question.id == question_id, 
                )
            )
            session.execute(stmt)
            stmt = sql_delete(init.Comment).where(
                and_(
                    init.Comment.question_id == question_id,
                )
            )
            session.execute(stmt)
            session.commit()  # Не забывайте скобки!
        
        return RedirectResponse("/", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/change", tags=["Изменение вопроса"])
async def change_question(
    request: Request,
    subject: str = Form(...),
    grade: str = Form(...),
    new_description: str = Form(...),
    id: int = Form(...),
    images: list[UploadFile] = File(None)
):
    try:
        current_user = function.decrypt(request.cookies.get("username"))
        
        with Session(init.engine) as session:
            # Получаем текущий вопрос для проверки владельца
            question = session.query(init.Question).filter(
                init.Question.id == id
            ).first()
            
            if not question or question.owner != current_user:
                return RedirectResponse("/", status_code=303)
            
            # Подготавливаем данные для обновления
            update_data = {
                "grade": grade,
                "subject": subject
            }
            
            # Обновляем описание только если оно не пустое
            if new_description.strip():
                update_data["description"] = new_description.strip()
            
            # Обрабатываем изображения только если они переданы
            if images is not None and any(image.filename for image in images if image.filename):
                saved_paths = []
                
                # Создаем папку для изображений, если не существует
                save_dir = os.path.join(static_dir, "images")
                os.makedirs(save_dir, exist_ok=True)
                
                # Обрабатываем каждое изображение
                for image in images:
                    if not image.filename:
                        continue
                    
                    # Проверяем тип файла
                    if not image.content_type.startswith("image/"):
                        continue
                    
                    # Генерируем уникальное имя файла
                    ext = image.filename.split('.')[-1]
                    filename = f"{uuid.uuid4()}.{ext}"
                    filepath = os.path.join(save_dir, filename)
                    
                    # Сохраняем файл
                    with open(filepath, "wb") as f:
                        f.write(await image.read())
                    
                    # Добавляем путь в список
                    saved_paths.append(f"/static/images/{filename}")
                
                # Обновляем пути к изображениям только если есть сохраненные файлы
                if saved_paths:
                    update_data["image_path"] = ",".join(saved_paths)
                else:
                    # Если файлы не прошли валидацию, удаляем изображения
                    update_data["image_path"] = None
            else:
                # Если изображения не переданы, удаляем их
                update_data["image_path"] = None
            
            # Обновление вопроса
            stmt = update(init.Question).where(
                init.Question.id == id
            ).values(**update_data)
            
            session.execute(stmt)
            session.commit()
        
        return RedirectResponse(f"/question/{id}", status_code=303)
    
    except Exception as e:
        print(f"Ошибка при изменении вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

@app.post("/delete_answer", tags=["Удаление вопроса"])
async def delete_answer(
    request: Request,
    owner: str = Form(None),
    id: str = Form(None),
    questionId: str = Form(None),
):
    current_user = function.decrypt(request.cookies.get("username"))
    if current_user == owner:
        with Session(init.engine) as session:
            # Правильное использование delete
            stmt = sql_delete(init.Comment).where(
                and_(
                    init.Comment.owner == current_user,
                    init.Comment.id == id, 
                )
            )
            session.execute(stmt)
            session.commit()  # Не забывайте скобки!
        
        return RedirectResponse(f"/question/{questionId}", status_code=303)    
    else:
        return RedirectResponse("/", status_code=303)

@app.post("/change_answer", tags=["Изменение комментария"])
async def change_answer(
    request: Request,
    comment: str = Form(...),
    owner: str = Form(...),
    id: int = Form(...),
    questionId: int = Form(...),
    images: list[UploadFile] = File(None),
):
    try:
        current_user = function.decrypt(request.cookies.get("username"))
        if current_user != owner:
            return RedirectResponse(f"/question/{questionId}", status_code=303)
        
        with Session(init.engine) as session:
            # Получаем текущий комментарий
            comment_obj = session.query(init.Comment).filter(
                init.Comment.id == id,
                init.Comment.owner == current_user
            ).first()
            
            if not comment_obj:
                return RedirectResponse(f"/question/{questionId}", status_code=303)
            
            # Подготавливаем данные для обновления
            update_data = {}
            
            # Обновляем описание только если оно не пустое
            if comment.strip():
                update_data["description"] = comment.strip()
            
            # Обрабатываем изображения
            if images is not None and any(image.filename for image in images if image.filename):
                saved_paths = []
                
                # Создаем папку для изображений комментариев
                save_dir = os.path.join(static_dir, "images", "comments")
                os.makedirs(save_dir, exist_ok=True)

                # Обрабатываем каждое изображение
                for image in images:
                    if not image.filename:
                        continue
                    
                    # Проверяем тип файла
                    if not image.content_type.startswith("image/"):
                        continue
                    
                    # Генерируем уникальное имя файла
                    ext = image.filename.split('.')[-1]
                    filename = f"comment_{uuid.uuid4()}.{ext}"
                    filepath = os.path.join(save_dir, filename)
                    
                    # Сохраняем файл
                    with open(filepath, "wb") as f:
                        f.write(await image.read())
                    
                    # Добавляем путь в список
                    saved_paths.append(f"/static/images/comments/{filename}")
                
                # Обновляем пути к изображениям только если есть сохраненные файлы
                if saved_paths:
                    update_data["image_filename"] = ",".join(saved_paths)
                else:
                    # Если файлы не прошли валидацию, удаляем изображения
                    update_data["image_filename"] = None
            else:
                # Если изображения не переданы, удаляем их
                update_data["image_filename"] = None
            
            # Если есть что обновлять
            if update_data:
                stmt = update(init.Comment).where(
                    init.Comment.id == id,
                    init.Comment.owner == current_user
                ).values(**update_data)
                
                session.execute(stmt)
                session.commit()
        
        return RedirectResponse(f"/question/{questionId}", status_code=303)
    
    except Exception as e:
        print(f"Ошибка при изменении комментария: {e}")
        return RedirectResponse(f"/question/{questionId}?error=server_error", status_code=303)

@app.post("/report_question", tags=["репорты"])
async def report_question(
    request: Request,
    questionId: str = Form(None),
    reson: str = Form(None),
):
    print(questionId, reson)
    if not request.cookies.get("id"):
        return RedirectResponse("/login", status_code=303)
    
    with Session(init.engine) as conn:
        # Проверяем, существует ли уже такой репорт
        stmt = select(init.Reportq).where(
            init.Reportq.question_id == questionId, 
            init.Reportq.reason == reson
        )
        data = conn.execute(stmt).first()
        
        if data:
            return RedirectResponse(f"/question/{questionId}", status_code=303)
        else:
            # Получаем вопрос из таблицы Question
            stmt = select(init.Question).where(init.Question.id == questionId)
            question_result = conn.execute(stmt).first()
            
            if not question_result:
                print(f"Вопрос с ID {questionId} не найден")
                return RedirectResponse(f"/question/{questionId}")
            
            question = question_result[0]  # получаем объект Question
            
            # Создаем репорт - используем правильные поля из модели Question
            reportq = init.Reportq(
                question_id=questionId,  
                reason=reson,
                description=question.description,  # ← это поле есть в Question
                image=question.image_path if question.image_path else ""  # ← используем image_path из Question
            )
            conn.add(reportq)
            conn.commit()
            print(f"Репорт создан для вопроса {questionId}")
    
    return RedirectResponse(f"/question/{questionId}", status_code=303)

@app.post("/report_answer", tags=["репорты"])
async def report_answer(
    request: Request,
    answerId: str = Form(None),
    questionId: str = Form(None),
    complaint_type: str = Form(None),
):
    print(questionId, complaint_type)
    if not request.cookies.get("id"):
        return RedirectResponse("/login", status_code=303)
    
    with Session(init.engine) as conn:
        stmt = select(init.Reporta).where(init.Reporta.answer_id == answerId, init.Reporta.reason == complaint_type)
        data = conn.execute(stmt).first()
        if data:
            return RedirectResponse(f"/question/{questionId}", status_code=303)
        else:
        # ПРАВИЛЬНО: получаем вопрос из таблицы Question
            stmt = select(init.Comment).where(init.Comment.id == answerId)
            question = conn.execute(stmt).first()
            
            if not question:
                print(f"Вопрос с ID {questionId} не найден")
                return RedirectResponse(f"/question/{questionId}")
            
            # Создаем репорт
            reporta = init.Reporta(
                answer_id=answerId,  
                reason=complaint_type,
                image=question[0].image_filename, 
                description=question[0].description,  # description из вопроса
            )
            conn.add(reporta)
            conn.commit()
            print(f"Репорт создан для otveta {answerId}")
    
    return RedirectResponse(f"/question/{questionId}", status_code=303)

@app.get("/admin/panel", tags=["Админ панель"])
async def adminpanel(request: Request):
    user_id = request.cookies.get("id")
    username = function.decrypt(request.cookies.get("username"))

    with Session(init.engine) as conn:
        # Получаем пользователя
        stmt = select(init.User).where(init.User.id == int(user_id))
        user = conn.scalar(stmt)

        # Проверяем права доступа
        if not user or (user.id != 1 and not user.is_admin):
            return RedirectResponse("/", status_code=303)

        # Получаем все жалобы на вопросы
        stmt = select(init.Reportq)
        report_questions = conn.scalars(stmt).all()
        questions = [
            {
                "id": r.id,
                "qid": r.question_id,
                "reson": r.reason,
                "text": r.description,
                "image": r.image,
            }
            for r in report_questions
        ]

        # Получаем все жалобы на ответы
        stmt = select(init.Reporta)
        report_answers = conn.scalars(stmt).all()
        answers = [
            {
                "id": r.id,
                "aid": r.answer_id,
                "reson": r.reason,
                "text": r.description,
                "image": r.image,
            }
            for r in report_answers
        ]

        return templates.TemplateResponse(
            "admin_reports.html",
            {
                "request": request,
                "questions": questions,
                "answers": answers,
                "username": username,
                "name": function.decrypt(request.cookies.get("name")),
            },
        )

@app.post("/admin/deletequestion")
async def deletequestion(
    request: Request,
    id: str = Form(None),
):
    with Session(init.engine) as conn:
        # Получаем пользователя
        stmt = select(init.User).where(init.User.id == int(request.cookies.get("id")))
        user = conn.scalar(stmt)

        # Проверяем права доступа
        if not user or (user.id != 1 and not user.is_admin):
            return RedirectResponse("/", status_code=303)
        id = int(id)
        print(type(id))
    with Session(init.engine) as session:
        stmt = sql_delete(init.Question).where(
            and_(
                init.Question.id == id, 
            )
        )
        session.execute(stmt)
        stmt = sql_delete(init.Reportq).where(
            and_(
                init.Reportq.question_id == id,
            )
        )
        session.execute(stmt)
        stmt = sql_delete(init.Comment).where(
            and_(
                init.Comment.question_id == id,
            )
        )
        session.execute(stmt)
        session.commit() 
    return RedirectResponse("/admin/panel", status_code=303)

@app.post("/admin/deleteanswer")
async def deletequestion(
    request: Request,
    id: str = Form(None),
):
    with Session(init.engine) as conn:
        # Получаем пользователя
        stmt = select(init.User).where(init.User.id == int(request.cookies.get("id")))
        user = conn.scalar(stmt)

        # Проверяем права доступа
        if not user or (user.id != 1 and not user.is_admin):
            return RedirectResponse("/", status_code=303)
        id = int(id)
        print(type(id))
    with Session(init.engine) as session:
        stmt = sql_delete(init.Comment).where(
                and_(
                    init.Comment.id == id, 
                )
            )
        session.execute(stmt)
        stmt = sql_delete(init.Reporta).where(
                and_(
                    init.Reporta.answer_id == id, 
                )
            )
        session.execute(stmt)
        session.commit()
    return RedirectResponse("/admin/panel", status_code=303)

@app.post("/admin/resolvequestion")
async def resolvequestion(
    request: Request,
    id: str = Form(...)
):
    with Session(init.engine) as conn:
        # Получаем пользователя
        stmt = select(init.User).where(init.User.id == int(request.cookies.get("id")))
        user = conn.scalar(stmt)

        # Проверяем права доступа
        if not user or (user.id != 1 and not user.is_admin):
            return RedirectResponse("/", status_code=303)
        id = int(id)
        print(type(id))
    with Session(init.engine) as session:
        stmt = sql_delete(init.Reportq).where(
                and_(
                    init.Reportq.question_id == id, 
                )
            )
        session.execute(stmt)
        session.commit()
    return RedirectResponse("/admin/panel", status_code=303)

@app.post("/admin/resolveanswer")
async def resolveanswer(
    request: Request,
    id: str = Form(...)
):
    with Session(init.engine) as conn:
        # Получаем пользователя
        stmt = select(init.User).where(init.User.id == int(request.cookies.get("id")))
        user = conn.scalar(stmt)

        # Проверяем права доступа
        if not user or (user.id != 1 and not user.is_admin):
            return RedirectResponse("/", status_code=303)
        id = int(id)
        print(type(id))
    with Session(init.engine) as session:
        stmt = sql_delete(init.Reporta).where(
                and_(
                    init.Reporta.answer_id == id, 
                )
            )
        session.execute(stmt)
        session.commit()
    return RedirectResponse("/admin/panel", status_code=303)
    
#@app.post("/like_question", tags=["Лайки"])
#async def like_questions(
#    request: Request,
#    question_id: str = Form(...), 
#):
#    if request.cookies.get("id"):
#        current_user = function.decrypt(request.cookies.get("username"))
#        with Session(init.engine) as conn:
#            stmt = select(init.Like).where(init.Like.question_id == question_id, init.Like.who == current_user)
#            data = conn.scalars(stmt).all()
#            print(data)
#            if data:
#                return RedirectResponse(f"/question/{question_id}")
#            like = init.Like(
#                question_id=question_id,
#                who=current_user,
#            )
#            conn.add(like)
#            stmt = select(init.Question.like).where(init.Question.id == question_id)
#            data = conn.scalars(stmt).all()
#            if data[0] == None:
#               new = 1
#            else:
#                new = data[0] + 1
#            stmt = update(init.Question).where(
#                and_(
#                    init.Question.id == question_id,
#                )
#                ).values(like=new)
#            conn.execute(stmt)
#            conn.commit()
#    return RedirectResponse(f"/question/{question_id}", status_code=303)

@app.post("/admin/add", tags=["Admin"])
async def add_admin(
    request: Request,
    target_username: str = Form(...),
):
    # Получаем username из куков
    actor_username_encrypted = request.cookies.get("username")
    if not actor_username_encrypted:
        return JSONResponse(content={"error": "Неавторизован"}, status_code=401)

    actor_username = function.decrypt(actor_username_encrypted)

    with Session(init.engine) as session:
        # Ищем актёра (того, кто пытается добавить админа)
        actor = session.execute(
            select(init.User).where(init.User.username == actor_username)
        ).scalar_one_or_none()

        # Ищем цель (кого хотим сделать админом)
        target = session.execute(
            select(init.User).where(init.User.username == target_username)
        ).scalar_one_or_none()

        # Проверяем, что оба существуют
        if not actor or not target:
            return JSONResponse(
                content={"error": "Пользователь не найден"}, status_code=404
            )

        # Проверяем права: либо id == 1, либо is_admin == True
        if actor.id != 1 and not actor.is_admin:
            return JSONResponse(
                content={"error": "Недостаточно прав"}, status_code=403
            )

        # Делаем пользователя админом
        session.execute(
            update(init.User)
            .where(init.User.username == target_username)
            .values(is_admin=True)
        )
        session.commit()

        return RedirectResponse("/admin/panel", status_code=303)

if __name__ == "__main__":
    init.Base.metadata.create_all(init.engine)
    uvicorn.run("main:app", reload=True)