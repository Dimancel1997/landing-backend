from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error_code: str = Field(..., examples=["validation_error"])
    message: str = Field(..., examples=["Invalid request payload"])
    details: list[dict] | None = None
