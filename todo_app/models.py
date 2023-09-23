from typing import Optional
import uuid
from datetime import datetime
from sqlalchemy import (
    Text,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from todo_app.utils import utcnow
from todo_app import db


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    password: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=utcnow())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=utcnow())

    tasklists: Mapped[list["TaskList"]] = relationship(back_populates="user")


class BlackListToken(db.Model):
    __tablename__ = "blacklisttokens"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    expire: Mapped[Optional[datetime]]

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=utcnow())


class TaskList(db.Model):
    __tablename__ = "tasklists"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    title: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="tasklists")
    tasks: Mapped[list["Task"]] = relationship(back_populates="tasklist")

    order: Mapped[Optional[int]] = mapped_column(default=0)

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=utcnow())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=utcnow())


class Task(db.Model):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )
    title: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tasklist_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tasklists.id", ondelete="CASCADE"), nullable=True
    )
    tasklist: Mapped["TaskList"] = relationship(back_populates="tasks")
    steps: Mapped[list["Step"]] = relationship(back_populates="task")
    is_completed: Mapped[bool] = mapped_column(default=False)

    reminder: Mapped[Optional[datetime]]
    due_date: Mapped[Optional[datetime]]

    order: Mapped[Optional[int]] = mapped_column(default=0)

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=utcnow())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=utcnow())


class Step(db.Model):
    __tablename__ = "steps"
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )

    title: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False)

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE")
    )
    task: Mapped["Task"] = relationship(back_populates="steps")

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=utcnow())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=utcnow())
