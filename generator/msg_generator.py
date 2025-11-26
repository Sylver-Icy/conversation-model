from dotenv import load_dotenv
import os

from openai import OpenAI

from prompts.character_profile import create_character_prompt
from regulators.emotion_model import EmotionModel

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

        system_prompt = create_character_prompt(
            user_name="Sylver",
            frndship_lvl=3,
            mood=mood,
            recent_chat=[],
            user_memory_context=[]
        )

        response = self.client.chat.completions.create(
            model="gpt-5-chat-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )
        return response.choices[0].message.content