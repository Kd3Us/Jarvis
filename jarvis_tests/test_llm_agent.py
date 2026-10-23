import base64
from unittest.mock import MagicMock

import pytest

from llm_agent import ConversationAgent


@pytest.fixture
def agent(monkeypatch):
    # Fake key: no network call is made when the client is created
    monkeypatch.setenv("GROQ_KEY", "fake-key")
    return ConversationAgent()


def test_system_prompt_is_loaded(agent):
    first = agent.conversation_history[0]
    assert first["role"] == "system"
    assert first["content"].strip() != ""


def test_history_hides_system_prompt(agent):
    assert agent.get_conversation_history() == []


def test_build_content_text_only():
    content = ConversationAgent.build_content("hello")
    assert content == [{"type": "text", "text": "hello"}]


def test_build_content_with_image():
    content = ConversationAgent.build_content("look", image=b"abc")
    assert content[0]["type"] == "text"
    expected = base64.b64encode(b"abc").decode("utf-8")
    assert content[1]["image_url"]["url"] == f"data:image/jpeg;base64,{expected}"


def test_ask_llm_stores_user_and_assistant_messages(agent):
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Ahoy"))
    ]
    agent.groq_client = fake_client

    agent.ask_llm("hi", None)

    history = agent.get_conversation_history()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[1]["content"][0]["text"] == "Ahoy"