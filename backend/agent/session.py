import uuid
from typing import Any, Optional


class ConversationSession:
    """In-memory conversation history for a single agent session."""

    def __init__(self, session_id: Optional[str] = None, max_history: int = 30) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: list[dict[str, Any]] = []
        self.max_history = max_history

    def add_user_message(self, content: str, image_url: Optional[str] = None) -> None:
        if image_url:
            message: dict[str, Any] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": content},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        else:
            message = {"role": "user", "content": content}
        self.messages.append(message)
        self._trim()

    def add_context(self, content: str) -> None:
        """Add tool-derived context that the model must treat as evidence."""
        self.messages.append({"role": "system", "content": content})
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def add_assistant_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
        normalized_calls = [
            {"id": call["id"], "type": "function", "function": call["function"]}
            for call in tool_calls
        ]
        self.messages.append({"role": "assistant", "content": None, "tool_calls": normalized_calls})

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})

    def get_messages_for_llm(self, system_prompt: str) -> list[dict[str, Any]]:
        return [{"role": "system", "content": system_prompt}, *self.messages]

    def _trim(self) -> None:
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]


_sessions: dict[str, ConversationSession] = {}


def get_session(session_id: Optional[str] = None) -> ConversationSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    session = ConversationSession(session_id)
    _sessions[session.session_id] = session
    return session


def delete_session(session_id: str) -> bool:
    return _sessions.pop(session_id, None) is not None
