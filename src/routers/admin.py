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
import uuid

router = APIRouter(
    prefix="/admin",
    tags=["Admins"]
)
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/panel", tags=["Админ панель"])
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
                "edited": r.edited,
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
                "edited": r.edited,
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

@router.post("/deletequestion")
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

@router.post("/deleteanswer")
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

@router.post("/resolvequestion")
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

@router.post("/resolveanswer")
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

@router.post("/add", tags=["Admin"])
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