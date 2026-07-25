import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: str = "auto",
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def vision(self, image_url: str, prompt: str, max_tokens: int = 1000) -> str:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = model

    async def chat(self, messages: list[dict[str, Any]], tools=None, tool_choice: str = "auto") -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or None,
            tool_choice=tool_choice if tools else None,
        )
        message = response.choices[0].message
        return {
            "content": message.content,
            "tool_calls": self._serialize_tool_calls(message.tool_calls or []) or None,
        }

    @staticmethod
    def _serialize_tool_calls(tool_calls: list[Any]) -> list[dict[str, Any]]:
        """Keep provider-specific metadata required when the call is replayed.

        Gemini's OpenAI-compatible endpoint adds
        ``extra_content.google.thought_signature`` to a tool call. That value
        must be sent back unchanged along with the tool result on the next
        request; dropping it makes Gemini 3 reject the conversation.
        """
        serialized_calls: list[dict[str, Any]] = []
        for call in tool_calls:
            serialized_call: dict[str, Any] = {
                "id": call.id,
                "type": call.type,
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }

            # The OpenAI SDK stores provider extension fields as model extras.
            extra_content = getattr(call, "extra_content", None)
            if extra_content is None:
                model_extra = getattr(call, "model_extra", None) or {}
                extra_content = model_extra.get("extra_content")
            if extra_content:
                serialized_call["extra_content"] = extra_content

            serialized_calls.append(serialized_call)
        return serialized_calls

    async def vision(self, image_url: str, prompt: str, max_tokens: int = 1000) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}},
                    ],
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str) -> None:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no esta configurada.")
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def chat(self, messages: list[dict[str, Any]], tools=None, tool_choice: str = "auto") -> dict:
        system = "\n\n".join(message["content"] for message in messages if message["role"] == "system")
        chat_messages = self._to_anthropic_messages(messages)
        anthropic_tools = [
            {
                "name": tool["function"]["name"],
                "description": tool["function"].get("description", ""),
                "input_schema": tool["function"]["parameters"],
            }
            for tool in tools or []
        ]
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=chat_messages,
            tools=anthropic_tools or None,
        )
        content = "".join(block.text for block in response.content if block.type == "text")
        tool_calls = [
            {"id": block.id, "function": {"name": block.name, "arguments": json.dumps(block.input)}}
            for block in response.content
            if block.type == "tool_use"
        ]
        return {"content": content or None, "tool_calls": tool_calls or None}

    @staticmethod
    def _to_anthropic_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for message in messages:
            if message["role"] == "system":
                continue
            if message["role"] == "tool":
                result.append(
                    {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": message["tool_call_id"], "content": message["content"]}],
                    }
                )
            elif message.get("tool_calls"):
                result.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": call["id"],
                                "name": call["function"]["name"],
                                "input": json.loads(call["function"]["arguments"]),
                            }
                            for call in message["tool_calls"]
                        ],
                    }
                )
            else:
                result.append({"role": message["role"], "content": message["content"]})
        return result

    async def vision(self, image_url: str, prompt: str, max_tokens: int = 1000) -> str:
        import base64
        import httpx

        async with httpx.AsyncClient() as client:
            image = await client.get(image_url)
            image.raise_for_status()
        media_type = "image/png" if image_url.lower().endswith(".png") else "image/jpeg"
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64.b64encode(image.content).decode()}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return response.content[0].text


class GoogleProvider(OpenAIProvider):
    def __init__(self, model: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=os.environ["GOOGLE_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.model = model


def get_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o")
    if provider == "openai":
        return OpenAIProvider(model)
    if provider == "anthropic":
        return AnthropicProvider(model)
    if provider == "google":
        return GoogleProvider(model)
    raise ValueError(f"Provider no soportado: {provider}")
