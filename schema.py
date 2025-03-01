from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    max_turns: Optional[int] = 5


class ChatResponse(BaseModel):
    conversation: str
