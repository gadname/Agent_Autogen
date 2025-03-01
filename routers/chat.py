from fastapi import HTTPException
from schema import ChatRequest, ChatResponse
from services.group_chat import counseling_group
from fastapi import APIRouter

router = APIRouter()


@router.post("/therapist_discussion", response_model=ChatResponse)
async def therapist_discussion(request: ChatRequest):
    """
    ユーザーの悩みに基づいてセラピスト間の議論を開始するエンドポイント
    """
    try:
        # セラピスト間の議論を開始
        result = counseling_group.start_therapist_discussion(
            user_message=request.message,
            max_turns=request.max_turns or 15,  # デフォルトは15ターン
        )
        return ChatResponse(conversation=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
