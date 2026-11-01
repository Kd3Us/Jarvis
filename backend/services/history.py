import copy


class MessageBuilder:
    @staticmethod
    def text_block(text):
        return {"type": "text", "text": text}

    @staticmethod
    def image_block(image_url):
        return {"type": "image_url", "image_url": {"url": image_url}}

    @staticmethod
    def build_message(role, text=None, image_url=None):
        content = []
        if text:
            content.append(MessageBuilder.text_block(text))
        if image_url:
            content.append(MessageBuilder.image_block(image_url))
        return {"role": role, "content": content}


class ConversationHistory:
    IMAGE_PLACEHOLDER = "[image envoyée précédemment]"

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.reset()

    def add_message(self, message):
        self.messages.append(message)

    def get_display_messages(self):
        return self.messages[1:] 

    def reset(self):
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def messages_for_model(self):
        messages = copy.deepcopy(self.messages)  
        image_already_seen = False

        for message in reversed(messages): 
            if isinstance(message["content"], str): 
                continue
            for i, block in enumerate(message["content"]):
                if block["type"] == "image_url":
                    if image_already_seen: 
                        message["content"][i] = MessageBuilder.text_block(self.IMAGE_PLACEHOLDER)
                    image_already_seen = True

        return messages