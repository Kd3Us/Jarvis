from groq import Groq
import base64
from dotenv import load_dotenv
import os
from pathlib import Path


class ConversationAgent:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.conversation_history = [
                {
                    "role": "system",
                    "content": self.read_file(file_path=Path(__file__).parent / "prompts" / "system.md")
                }
            ]


    @staticmethod
    def read_file(file_path):
        with open(file_path, "r") as file:
            return file.read()


    @staticmethod
    def encode_image(image):
        return base64.b64encode(image).decode('utf-8')


    def get_conversation_history(self):
        return self.conversation_history[1: ]


    @staticmethod
    def build_content(text_interaction, image=None):
        content = []
        if text_interaction:
            content.append({
                            "type": "text",
                            "text": text_interaction
                        })
        if image :
            content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{ConversationAgent.encode_image(image)}",
                            },
                        })

        return content


    def update_conversation_history(self, role, text_interaction, image=None):
        self.conversation_history.append(
            {
            "role": role,
            "content": self.build_content(text_interaction, image),
            }
        )



    def transcribe(self, audio_interaction):
 
        transcription = self.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_interaction),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            timestamp_granularities = ["word", "segment"], 
            temperature=0.0
        )

        return transcription.text




    def ask_llm(self, text_interaction, image):

        self.update_conversation_history(role="user", text_interaction=text_interaction, image=image)

        response = self.groq_client.chat.completions.create(
            messages=self.conversation_history,
            model="qwen/qwen3.8-27b",
            include_reasoning=False,
        ).choices[0].message.content


        self.update_conversation_history(role="assistant", text_interaction=response)





























if __name__ == "__main__":
    question = input("Pose ta question :\n")
    response = ask_llm(question)
    print("\n")
    print(response)