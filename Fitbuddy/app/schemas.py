from typing import Literal

from pydantic import BaseModel, Field


Goal = Literal[
	"weight loss",
	"muscle gain",
	"general wellness",
	"flexibility"
]


Intensity = Literal[
	"low",
	"medium",
	"high"
]


class UserInput(BaseModel):

	name: str = Field(
		min_length=2,
		max_length=120
	)

	user_id: str = Field(
		min_length=2,
		max_length=80,
		pattern=r"^[A-Za-z0-9_-]+$"
	)

	age: int = Field(
		ge=13,
		le=100
	)

	weight: float = Field(
		gt=20,
		le=300
	)

	goal: Goal

	intensity: Intensity


class FeedbackRequest(BaseModel):

	user_id: str = Field(
		min_length=2,
		max_length=80
	)

	feedback: str = Field(
		min_length=3,
		max_length=2000
	)