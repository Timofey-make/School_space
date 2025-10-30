from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import os


class Base(DeclarativeBase):
    pass

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    background: Mapped[str] = mapped_column(String(30))
    min_points: Mapped[int]

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)  # 🟢 флажок админа

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, username={self.username!r}, "
            f"password={self.password!r}, title={self.title!r}, background={self.background!r}, "
            f"min_points={self.min_points!r}, is_admin={self.is_admin!r})"
        )


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(30))
    owner_name: Mapped[str] = mapped_column(String(30))
    grade: Mapped[int]
    subject: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(1000))
    like: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    image_path: Mapped[str] = mapped_column(String(500), nullable=True)  # Добавьте это поле
    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, owner={self.owner!r}, owner_name={self.owner_name!r}, subject={self.subject!r}, title={self.title!r}, description={self.description!r}, created={self.created_at!r}, image_path={self.image_path!r})"

class Comment(Base):
    __tablename__ = "Comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int]
    owner: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, owner={self.owner!r}, question_id={self.question_id!r}, description={self.description!r}, created_at={self.created_at!r})"
    
class Reportq(Base):
    __tablename__ = "ReportsQ"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int]
    reason: Mapped[str] = mapped_column(String(500))
    description: Mapped[str]
    image = Mapped[str]
    
    def __repr__(self) -> str:
        return f"Reportq(id={self.id!r}, question_id={self.question_id!r}, reason={self.reason!r}, description={self.description!r}, image={self.image!r})"
    
class Reportq(Base):
    __tablename__ = "ReportsQ"
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int]
    reason: Mapped[str] = mapped_column(String(500))
    description: Mapped[str]
    image = Mapped[str]
    
    def __repr__(self) -> str:
        return f"Reportq(id={self.id!r}, question_id={self.question_id!r}, reason={self.reason!r}, description={self.description!r})"

class Reporta(Base):
    __tablename__ = "ReportsA"
    id: Mapped[int] = mapped_column(primary_key=True)
    answer_id: Mapped[int]
    reason: Mapped[str] = mapped_column(String(500))
    description: Mapped[str]
    
    def __repr__(self) -> str:
        return f"Reporta(id={self.id!r}, answer_id={self.answer_id!r}, reason={self.reason!r}, description={self.description!r})"

class Like(Base):
    __tablename__ = "Like_question"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int]
    who: Mapped[str]
    def __repr__(self) -> str:
        return f"Like(id={self.id!r}, question_id={self.question_id!r}, who={self.who!r}"

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'users.db')
engine = create_engine(f'sqlite:///{db_path}')