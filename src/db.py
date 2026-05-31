from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from sqlalchemy import JSON, DateTime, ForeignKey, SmallInteger, String, Text, create_engine, func, select, text
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
CONNECT_ARGS = {"sslmode": "require"} if os.getenv("DATABASE_SSL", "").lower() in {"1", "true", "yes"} else {}
ENGINE = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=CONNECT_ARGS) if DATABASE_URL else None
SESSION_FACTORY = sessionmaker(bind=ENGINE, expire_on_commit=False) if ENGINE else None


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    auth_provider: Mapped[str] = mapped_column(String(40), nullable=False, default="local")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class Cv(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
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


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


def init_database() -> None:
    if ENGINE and os.getenv("AUTO_CREATE_TABLES", "true").lower() in {"1", "true", "yes"}:
        Base.metadata.create_all(ENGINE)
        with ENGINE.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS external_id VARCHAR(80) UNIQUE"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(40) NOT NULL DEFAULT 'local'"))
            conn.execute(text("ALTER TABLE cvs ADD COLUMN IF NOT EXISTS analysis JSONB"))


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


def get_or_create_system_user(session: Session) -> User:
    default_name = os.getenv("DEFAULT_USER_NAME", "SkillMap User")
    default_email = os.getenv("DEFAULT_USER_EMAIL", "local-user@skillmap.internal")
    user = session.scalar(select(User).where(User.email == default_email))

    if user is None:
        user = User(name=default_name, email=default_email)
        session.add(user)
        session.flush()
    else:
        user.name = default_name
        session.flush()

    return user


def get_or_create_authenticated_user(session: Session, user_context: dict | None) -> User:
    if not user_context or not user_context.get("external_id"):
        return get_or_create_system_user(session)

    external_id = str(user_context["external_id"])
    email = str(user_context.get("email") or f"{external_id}@supabase.local").lower()
    name = str(user_context.get("name") or email.split("@")[0] or "SkillMap User")
    provider = str(user_context.get("provider") or "supabase")

    user = session.scalar(select(User).where(User.external_id == external_id))
    if user is None and email:
        user = session.scalar(select(User).where(User.email == email))

    if user is None:
        user = User(name=name, email=email, external_id=external_id, auth_provider=provider)
        session.add(user)
        session.flush()
    else:
        user.name = name
        user.email = email
        user.external_id = external_id
        user.auth_provider = provider
        session.flush()

    return user


def get_or_create_skill(session: Session, skill_name: str) -> Skill:
    skill = session.scalar(select(Skill).where(Skill.name == skill_name))
    if skill is None:
        skill = Skill(name=skill_name)
        session.add(skill)
        session.flush()
    return skill
