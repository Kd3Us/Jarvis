import streamlit as st 
from llm_agent import ConversationAgent
import base64

class UserInterface:
	def __init__(self):
		st.set_page_config(page_title="Jarvis")
		st.title("Jarvis")
		self.conversation_agent_object = self.get_persistant_conversation_agent()


	def get_persistant_conversation_agent(self):
		
		if "conversation_agent_object" not in st.session_state:
			st.session_state.conversation_agent_object = ConversationAgent()

		return st.session_state.conversation_agent_object



	@staticmethod
	def display_image(base64_image):
		image_bytes = base64.b64decode(base64_image.split(",", 1)[1])
		st.image(image_bytes, width=150)


	@staticmethod
	def display_message(message):
		with st.chat_message(message["role"]):
			for content in message["content"]:
				if content["type"] == "text":
					st.markdown(content["text"])
				elif content["type"] == "image_url":
					UserInterface.display_image(content["image_url"]["url"])


	def show_discussion_history(self):
		for message in self.conversation_agent_object.get_conversation_history():
			self.display_message(message)


	def run(self):
		user_interaction = st.chat_input(
			"Que veux tu moussaillon ?",
			accept_file=True,
			accept_audio=True,
			file_type=["jpg", "jpeg", "png"],
			)

		if user_interaction :
			if user_interaction.audio:
				text_interaction = self.conversation_agent_object.transcribe(user_interaction.audio.getvalue())
			else:
				text_interaction = user_interaction.text

			image = user_interaction.files[0].getvalue() if user_interaction.files else None

			self.conversation_agent_object.ask_llm(text_interaction, image)
			self.show_discussion_history()



if __name__ == "__main__":
	user_interface_object = UserInterface()
	user_interface_object.run()








































	# response = ask_llm(user_input)
	# with st.chat_message("user"):
	# 	st.markdown(user_input)

	# with st.chat_message("system"):
	# 	st.markdown(response)


