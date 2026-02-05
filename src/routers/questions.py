from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
    prefix="/questions",
    tags=["Questions"]
)

BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/add", tags="Добавить вопрос")
async def add(request: Request):
    if request.cookies.get("id"):
        return templates.TemplateResponse("add_question.html", {"request": request})
    else:
        return RedirectResponse(url="/login", status_code=303)

@router.post("/doadd", tags=["Добавить вопрос"])
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