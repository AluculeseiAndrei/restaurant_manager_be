from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    authentication_successful: str = Field(alias="Authentication successful")

    model_config = {"populate_by_name": True}


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    email: str
    password: str = Field(min_length=8)
    code: int = Field(ge=1000, le=9999)
