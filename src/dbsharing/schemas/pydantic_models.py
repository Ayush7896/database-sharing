from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    model_name: str
    max_p: float
    max_tem: float
    max_tokens: int

class DownloadButtonConfig(BaseModel):
    session_id: str
    format: str = "docx"

class ChatRequest(BaseModel):
    session_id: str


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str 


class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length = 4)