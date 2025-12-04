from prompts.character_profile import create_character_prompt

from regulators.emotion_model import EmotionModel
from regulators.context_model import fetch_context, add_to_history

from state.client import client

veyra = EmotionModel()

class ChatGenerator:
    def __init__(self):
        self.client = client

    def generate(self, user_msg: str, user_name: str = "Player", frndship_lvl: int = 3) -> str:
        #do mood stuff
        deltas = veyra.extract_deltas(user_msg)
        veyra.update_mood(deltas)
        mood = veyra.get_active_mood()

        #get context
        context = fetch_context(user_msg, user_name)

        system_prompt = create_character_prompt(
            user_name=user_name,
            frndship_lvl=frndship_lvl,
            mood=mood,
            recent_chat=context,
            user_memory_context=[]
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-chat-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            reply = response.choices[0].message.content
            add_to_history(reply)
            return reply

        except Exception:
            return "ugh—my brain lagged, say that again?"
