import re
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator

PHONE_PATTERN = re.compile(r"^\+?[0-9\s\-()]{10,20}$")


class Sentiment(StrEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    unknown = "unknown"


class ContactRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=80,
        examples=["Иван Петров"],
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=20,
        examples=["+7 999 123-45-67"],
    )
    email: EmailStr = Field(
        ...,
        examples=["ivan@example.com"],
    )
    comment: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        examples=["Здравствуйте! Хочу узнать подробнее о вашем продукте."],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())

        if not normalized:
            raise ValueError("Name cannot be empty.")

        if any(char.isdigit() for char in normalized):
            raise ValueError("Name must not contain digits.")

        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip()

        if not PHONE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "Phone must contain 10-20 characters and may include digits, "
                "spaces, '+', '-', parentheses."
            )

        digits_count = sum(char.isdigit() for char in normalized)
        if digits_count < 10:
            raise ValueError("Phone must contain at least 10 digits.")

        return normalized

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        normalized = value.strip()

        if len(normalized) < 10:
            raise ValueError("Comment must contain at least 10 characters.")

        return normalized


class AIAnalysis(BaseModel):
    sentiment: Sentiment = Sentiment.unknown
    category: str | None = None
    suggested_reply: str | None = None
    is_available: bool = False


class ContactRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    phone: str
    email: EmailStr
    comment: str
    ai_analysis: AIAnalysis
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContactResponse(BaseModel):
    id: UUID
    status: str = Field(examples=["accepted"])
    message: str
    ai_analysis: AIAnalysis | None = None
