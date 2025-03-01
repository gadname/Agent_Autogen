from fastapi import HTTPException
from schema import ChatRequest, ChatResponse
from services.group_chat import software_design_group
from fastapi import APIRouter

router = APIRouter()


@router.post("/design_discussion", response_model=ChatResponse)
async def design_discussion(request: ChatRequest):
    """
    ユーザーの要件に基づいて設計議論を開始するエンドポイント
    """
    try:
        # 設計議論を開始
        result = software_design_group.start_software_design_discussion(
            user_message=request.message,
            max_turns=request.max_turns or 30,
        )
        return ChatResponse(conversation=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
