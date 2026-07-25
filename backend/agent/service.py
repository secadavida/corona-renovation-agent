import json
from typing import Optional

from sqlalchemy.orm import Session

from backend.agent.llm_provider import get_provider
from backend.agent.session import get_session
from backend.agent.system_prompt import SYSTEM_PROMPT
from backend.agent.tools import TOOL_DEFINITIONS, execute_tool


class RenovationAgentService:
    """Coordinates the LLM, conversation state, and grounded tool execution."""

    async def chat(self, message: str, db: Session, session_id: Optional[str] = None, image_url: Optional[str] = None) -> dict:
        session = get_session(session_id)
        provider = get_provider()
        session.add_user_message(message, image_url)

        if image_url:
            analysis = await execute_tool("analizarImagen", {"image_url": image_url}, db, provider)
            session.add_context(f"Analisis visual obtenido con analizarImagen:\n{analysis}")

        for _ in range(4):
            response = await provider.chat(session.get_messages_for_llm(SYSTEM_PROMPT), TOOL_DEFINITIONS)
            tool_calls = response.get("tool_calls")
            if not tool_calls:
                content = response.get("content") or "No pude generar una respuesta."
                session.add_assistant_message(content)
                return {"session_id": session.session_id, "response": content}

            session.add_assistant_tool_calls(tool_calls)
            for tool_call in tool_calls:
                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    result = json.dumps({"error": "Argumentos de herramienta invalidos."}, ensure_ascii=False)
                else:
                    result = await execute_tool(tool_call["function"]["name"], arguments, db, provider)
                session.add_tool_result(tool_call["id"], result)

        response = await provider.chat(session.get_messages_for_llm(SYSTEM_PROMPT), tool_choice="none")
        content = response.get("content") or "No pude completar la recomendacion con la informacion disponible."
        session.add_assistant_message(content)
        return {"session_id": session.session_id, "response": content}
