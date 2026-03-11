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
        return RedirectResponse(url="/users/login", status_code=303)

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
                owner_id=request.cookies.get("id"),
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
    
@router.post("/delete", tags=["Удаление вопроса"])
async def delete_question(
    request: Request,
    owner: str = Form(...),
    question_id: str = Form(...),
):
    print(f"Удаление вопроса {question_id}")
    current_user = function.decrypt(request.cookies.get("username"))
    
    if current_user == owner:
        with Session(init.engine) as session:
            # Сначала получаем все комментарии к этому вопросу, чтобы знать их ID
            comments_stmt = select(init.Comment.id).where(init.Comment.question_id == question_id)
            comments = session.execute(comments_stmt).all()
            comment_ids = [comment[0] for comment in comments]
            
            # Удаляем репорты на комментарии (если есть комментарии)
            if comment_ids:
                stmt_reports_comments = sql_delete(init.Reporta).where(
                    init.Reporta.answer_id.in_(comment_ids)
                )
                session.execute(stmt_reports_comments)
                print(f"Удалены репорты для комментариев: {comment_ids}")
            
            # Удаляем репорты на сам вопрос
            stmt_reports_question = sql_delete(init.Reportq).where(
                init.Reportq.question_id == question_id
            )
            session.execute(stmt_reports_question)
            print(f"Удалены репорты для вопроса {question_id}")
            
            # Удаляем комментарии к вопросу
            stmt_comments = sql_delete(init.Comment).where(
                init.Comment.question_id == question_id
            )
            session.execute(stmt_comments)
            print(f"Удалены комментарии для вопроса {question_id}")
            
            # Удаляем сам вопрос
            stmt_question = sql_delete(init.Question).where(
                and_(
                    init.Question.owner == current_user,
                    init.Question.id == question_id, 
                )
            )
            session.execute(stmt_question)
            
            session.commit()
            print(f"Вопрос {question_id} и все связанные данные успешно удалены")
        
        return RedirectResponse("/", status_code=303)    
    else:
        print(f"Ошибка: пользователь {current_user} не является владельцем вопроса")
        return RedirectResponse("/", status_code=303)
    
@router.post("/change", tags=["Изменение вопроса"])
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
                "subject": subject,
                "edited": True,
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
            stmt = select(init.Reportq).where(
                init.Reportq.question_id == id
            )
            data = session.execute(stmt).fetchall()
            if data:
                stmt = update(init.Reportq).where(init.Reportq.question_id == id).values({
                    "edited":True,
                })    
            session.execute(stmt)
            session.commit()
        
        return RedirectResponse(f"/question/{id}", status_code=303)
    
    except Exception as e:
        print(f"Ошибка при изменении вопроса: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)
    
@router.post("/report_question", tags=["репорты"])
async def report_question(
    request: Request,
    questionId: str = Form(None),
    reson: str = Form(None),
):
    print(questionId, reson)
    if not request.cookies.get("id"):
        return RedirectResponse("/users/login", status_code=303)
    
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
                owner_id=question.owner_id, 
                reason=reson,
                description=question.description,  # ← это поле есть в Question
                image=question.image_path if question.image_path else ""  # ← используем image_path из Question
            )
            conn.add(reportq)
            conn.commit()
            print(f"Репорт создан для вопроса {questionId}")
    
    return RedirectResponse(f"/question/{questionId}", status_code=303)

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