from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.responses import JSONResponse
from sqlalchemy import select
import json
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import delete as sql_delete, and_
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update
from src import init
from src import function
import os
import uuid

router = APIRouter(
    prefix="/api",
    tags=["api"]
)
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/answers", tags=["API"])
async def get_answers():
    with Session(init.engine) as conn:
        # Получаем все комментарии
        stmt = select(
            init.Comment.id,
            init.Comment.question_id,
            init.Comment.owner,
            init.Comment.owner_id,
            init.Comment.description,
            init.Comment.created_at,
            init.Comment.image_filename,
            init.Comment.edited,
        ).order_by(init.Comment.id.desc())
        
        comments = conn.execute(stmt).fetchall()
        questions = []
        
        # Предварительно получаем всех пользователей для оптимизации
        users_stmt = select(init.User.username, init.User.name)
        users = conn.execute(users_stmt).fetchall()
        user_dict = {username: name for username, name in users}
        
        for row in comments:
            # Получаем имя пользователя из словаря, или используем username как fallback
            name = user_dict.get(row.owner, row.owner)
            
            questions.append({
                "id": row.id,
                "question_id": row.question_id,
                "owner_id": row.owner_id,
                "name": name,  # теперь это строка, а не список
                "username": row.owner,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "images": row.image_filename,
                "edited": row.edited,
            })
        
        return JSONResponse(content=questions)
    
@router.get("/like", tags=["API"])
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

@router.get("/questions", tags=["API"])
async def get_questions():
    with Session(init.engine) as conn:
        stmt = select(
            init.Question.id,
            init.Question.owner,
            init.Question.owner_name,
            init.Question.owner_id,
            init.Question.subject,
            init.Question.grade,
            init.Question.description,
            init.Question.created_at,
            init.Question.like,
            init.Question.image_path,
            init.Question.edited,  # <-- добавляем поле с путями
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
                "owner_id": row.owner_id,
                "subject": row.subject,
                "grade": row.grade,
                "text": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "like": row.like,
                "images": image_list,
                "edited": row.edited,  # <-- теперь тут массив путей
            })

        return JSONResponse(content=questions)

@router.get("/users", tags=["API"])
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
