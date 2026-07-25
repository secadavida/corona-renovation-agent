from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.agent.service import RenovationAgentService
from backend.db.session import get_db
from backend.schemas.agent import AgentChatRequest, AgentChatResponse


router = APIRouter(prefix="/api/agent", tags=["Renovation Agent"])
agent_service = RenovationAgentService()


@router.post("/chat", response_model=AgentChatResponse, status_code=status.HTTP_200_OK)
async def chat(payload: AgentChatRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return await agent_service.chat(
            message=payload.message,
            session_id=payload.session_id,
            image_url=payload.image_url,
            db=db,
        )
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
