from datetime import datetime

from sqlalchemy import (
	DateTime,
	Float,
	ForeignKey,
	Integer,
	String,
	Text,
	func,
)

from sqlalchemy.orm import (
	Mapped,
	mapped_column,
	relationship,
)

from .database import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True
	)

	user_id: Mapped[str] = mapped_column(
		String(80),
		unique=True,
		index=True,
		nullable=False
	)

	name: Mapped[str] = mapped_column(
		String(120),
		nullable=False
	)

	age: Mapped[int] = mapped_column(
		Integer,
		nullable=False
	)

	weight: Mapped[float] = mapped_column(
		Float,
		nullable=False
	)

	goal: Mapped[str] = mapped_column(
		String(40),
		nullable=False
	)

	intensity: Mapped[str] = mapped_column(
		String(20),
		nullable=False
	)

	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		server_default=func.now(),
		nullable=False
	)

	plan: Mapped["Plan | None"] = relationship(
		back_populates="user",
		cascade="all, delete-orphan",
		uselist=False
	)


class Plan(Base):
	__tablename__ = "plans"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True
	)

	user_id: Mapped[int] = mapped_column(
		ForeignKey(
			"users.id",
			ondelete="CASCADE"
		),
		unique=True,
		nullable=False
	)

	original_plan: Mapped[str] = mapped_column(
		Text,
		nullable=False
	)

	updated_plan: Mapped[str | None] = mapped_column(
		Text,
		nullable=True
	)

	nutrition_tip: Mapped[str] = mapped_column(
		Text,
		nullable=False
	)

	last_feedback: Mapped[str | None] = mapped_column(
		Text,
		nullable=True
	)

	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False
	)

	user: Mapped[User] = relationship(
		back_populates="plan"
	)