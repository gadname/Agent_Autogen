from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str  # ユーザーの要件や設計に関する質問
    max_turns: Optional[int] = 8  # 会話の最大ターン数


class ChatResponse(BaseModel):
    conversation: str  # フォーマットされた会話履歴
