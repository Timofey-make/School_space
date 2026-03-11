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
    prefix="/answers",
    tags=["Answers"]
)
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.post("/addcomment", tags=["Добавить комментарий"])
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
                owner_id=request.cookies.get("id"),
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
    
@router.post("/delete_answer", tags=["Удаление вопроса"])
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

@router.post("/change_answer", tags=["Изменение комментария"])
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
            update_data = {
                "edited": True,
            }
            
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
            stmt = select(init.Reporta).where(
                init.Reporta.answer_id == id
            )
            data = session.execute(stmt).fetchall()
            if data:
                stmt = update(init.Reporta).where(init.Reporta.answer_id == id).values({
                    "edited":True,
                })    
            session.execute(stmt)
            session.commit()
        
        return RedirectResponse(f"/question/{questionId}", status_code=303)
    
    except Exception as e:
        print(f"Ошибка при изменении комментария: {e}")
        return RedirectResponse(f"/question/{questionId}?error=server_error", status_code=303)

@router.post("/report_answer", tags=["репорты"])
async def report_answer(
    request: Request,
    answerId: str = Form(None),
    questionId: str = Form(None),
    complaint_type: str = Form(None),
):
    print(questionId, complaint_type)
    if not request.cookies.get("id"):
        return RedirectResponse("/users/login", status_code=303)
    
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
