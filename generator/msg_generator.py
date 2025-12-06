from prompts.character_profile import create_character_prompt

from regulators.emotion_model import EmotionModel
from regulators.context_model import fetch_context, add_to_history

from state.client import client

veyra = EmotionModel()

class ChatGenerator:
    def __init__(self):
        self.client = client

    async def generate(self, user_msg: str,user_id: int, user_name: str = "Player", frndship_title: str = "Stranger", chat_history: list = [], req_id: str = "000" ) -> str:
        #do mood stuff
        deltas = await veyra.extract_deltas(user_msg, req_id)
        veyra.update_mood(deltas)
        mood = veyra.get_active_mood()

        #get context
        context = await fetch_context(user_msg, user_id, req_id)

        system_prompt = create_character_prompt(
            user_name=user_name,
            frndship_title=frndship_title,
            mood=mood,
            chat_context=context,
            chat_history=chat_history,
            req_id=req_id
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-chat-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=60,
                temperature=0.9,
                top_p=0.95,
                frequency_penalty=0.5,
                presence_penalty=0.1
            )
            reply = response.choices[0].message.content
            add_to_history(reply)
            return reply

        except Exception:
            return "ugh—my brain lagged, say that again?"
