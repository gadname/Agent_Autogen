from fastapi import HTTPException
from schema import ChatRequest, ChatResponse
from services.group_chat import software_design_group
from fastapi import APIRouter

router = APIRouter()


@router.post("/software_design_discussion", response_model=ChatResponse)
async def software_design_discussion(request: ChatRequest):
    """
    ユーザーの要件に基づいて設計議論を開始するエンドポイント
    """
    try:
        result = software_design_group.start_software_design_discussion(
            user_message=request.message,
            max_turns=request.max_turns or 30,
        )
        return ChatResponse(conversation=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
