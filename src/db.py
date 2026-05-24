from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from sqlalchemy import JSON, DateTime, ForeignKey, SmallInteger, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def normalize_database_url(raw_url: str | None) -> str | None:
    if not raw_url:
        return None

    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)

    if raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return raw_url


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL"))
ENGINE = create_engine(DATABASE_URL, future=True, pool_pre_ping=True) if DATABASE_URL else None
SESSION_FACTORY = sessionmaker(bind=ENGINE, expire_on_commit=False) if ENGINE else None


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class Cv(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    proficiency: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="cv")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


def init_database() -> None:
    if ENGINE and os.getenv("AUTO_CREATE_TABLES", "true").lower() in {"1", "true", "yes"}:
        Base.metadata.create_all(ENGINE)


@contextmanager
def session_scope() -> Iterator[Session]:
    if SESSION_FACTORY is None:
        raise RuntimeError("DATABASE_URL is not configured.")

    session = SESSION_FACTORY()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_or_create_demo_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.email == "demo@skillmap.local"))

    if user is None:
        user = User(name="Demo User", email="demo@skillmap.local")
        session.add(user)
        session.flush()
    else:
        user.name = "Demo User"
        session.flush()

    return user


def get_or_create_skill(session: Session, skill_name: str) -> Skill:
    skill = session.scalar(select(Skill).where(Skill.name == skill_name))
    if skill is None:
        skill = Skill(name=skill_name)
        session.add(skill)
        session.flush()
    return skill


def save_cv_analysis(
    *,
    file_name: str,
    extracted_skills: list[str],
    skill_gap: list[str],
    recommendation: list[str],
    confidence: float,
):
    if SESSION_FACTORY is None:
        return None

    with session_scope() as session:
        user = get_or_create_demo_user(session)

        cv_record = Cv(user_id=user.id, file_url=f"/uploads/{file_name}", file_name=file_name)
        session.add(cv_record)
        session.flush()

        for skill_name in extracted_skills:
            skill = get_or_create_skill(session, skill_name)
            session.merge(UserSkill(user_id=user.id, skill_id=skill.id, proficiency=2, source="cv"))

        session.add(
            LearningPath(
                user_id=user.id,
                recommendation={
                    "extractedSkills": extracted_skills,
                    "skillGap": skill_gap,
                    "recommendation": recommendation,
                    "confidence": confidence,
                },
            )
        )

        return {"userId": user.id, "cvId": cv_record.id}


def save_quiz_result(*, score: int, result: dict):
    if SESSION_FACTORY is None:
        return None

    with session_scope() as session:
        user = get_or_create_demo_user(session)
        session.add(QuizAttempt(user_id=user.id, score=score, result=result))
        return {"userId": user.id, "score": score}
