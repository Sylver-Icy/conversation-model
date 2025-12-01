from dotenv import load_dotenv
import os

from openai import OpenAI

from prompts.character_profile import create_character_prompt

from regulators.emotion_model import EmotionModel
from regulators.context_model import fetch_context, add_to_history

load_dotenv()  # loads .env

veyra = EmotionModel()

class ChatGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, user_msg: str) -> str:
        #do mood stuff
        deltas = veyra.extract_deltas(user_msg)
        veyra.update_mood(deltas)
        mood = veyra.get_active_mood()

        #get context
        context = fetch_context(user_msg)

        system_prompt = create_character_prompt(
            user_name="Sylver",
            frndship_lvl=3,
            mood=mood,
            recent_chat=context,
            user_memory_context=[]
        )

        response = self.client.chat.completions.create(
            model="gpt-5-chat-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )
        add_to_history(response.choices[0].message.content)
        return response.choices[0].message.content

if __name__ == "__main__":
    gen = ChatGenerator()
    print("\nLive Veyra test. Type 'exit' to quit.\n")

    while True:
        user_msg = input("You: ")
        if user_msg.lower() == "exit":
            break

        reply = gen.generate(user_msg)
        print("Veyra:", reply)
        print("\n---\n")