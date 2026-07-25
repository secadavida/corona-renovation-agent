from typing import Optional

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: Optional[str] = None
    image_url: Optional[str] = None


class AgentChatResponse(BaseModel):
    session_id: str
    response: str
