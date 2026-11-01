from services.history import ConversationHistory, MessageBuilder

def make_history_with_images(n=3):
    history = ConversationHistory("prompt système")
    for i in range(n):
        history.add_message(MessageBuilder.build_message("user", f"q{i}", f"data:image/jpeg;base64,IMG{i}"))
        history.add_message(MessageBuilder.build_message("assistant", f"r{i}"))
    return history


def count_images(messages):
    return sum(
        1
        for m in messages
        if isinstance(m["content"], list)
        for block in m["content"]
        if block["type"] == "image_url"
    )


def test_message_format_role_and_blocks():
    message = MessageBuilder.build_message("user", "salut", "data:image/png;base64,AAA")
    assert message["role"] == "user"
    assert [b["type"] for b in message["content"]] == ["text", "image_url"]


def test_no_image_block_when_no_image():
    message = MessageBuilder.build_message("user", "salut")
    assert [b["type"] for b in message["content"]] == ["text"]


def test_only_last_image_kept_for_model():
    history = make_history_with_images(3)
    messages = history.messages_for_model()
    assert count_images(messages) == 1
    assert "IMG2" in str(messages)
    assert str(messages).count(ConversationHistory.IMAGE_PLACEHOLDER) == 2


def test_followup_without_reupload_keeps_image():
    history = make_history_with_images(1)
    history.add_message(MessageBuilder.build_message("user", "et le total ?"))
    assert count_images(history.messages_for_model()) == 1


def test_messages_for_model_returns_a_copy():
    history = make_history_with_images(3)
    history.messages_for_model()[1]["content"].clear()
    assert count_images(history.get_display_messages()) == 3


def test_reset_keeps_only_system():
    history = make_history_with_images(2)
    history.reset()
    assert history.messages == [{"role": "system", "content": "prompt système"}]