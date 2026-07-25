import unittest
from unittest.mock import patch

from backend.agent.service import RenovationAgentService


class FakeProvider:
    async def chat(self, _messages, _tools=None, tool_choice="auto"):
        return {"content": "Necesito las dimensiones del baño antes de recomendar productos.", "tool_calls": None}


class AgentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_creates_a_session_and_returns_the_llm_response(self) -> None:
        with patch("backend.agent.service.get_provider", return_value=FakeProvider()):
            result = await RenovationAgentService().chat("Quiero remodelar mi baño", db=None)

        self.assertTrue(result["session_id"])
        self.assertEqual(result["response"], "Necesito las dimensiones del baño antes de recomendar productos.")


if __name__ == "__main__":
    unittest.main()
