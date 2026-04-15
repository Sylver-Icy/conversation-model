from prompts.character_profile import create_character_prompt

from regulators.emotion_model import EmotionModel
from regulators.context_model import fetch_context, add_to_history

from state.client import client

veyra = EmotionModel()

class ChatGenerator:
    def __init__(self):
        self.client = client

    async def generate(
        self,
        user_msg: str,
        user_id: int,
        user_name: str = "Player",
        frndship_title: str = "Stranger",
        game_events: list | None = None,
        mood: str = "neutral",
        chat_history: list | None = None,
        req_id: str = "000",
    ) -> str:
        # get context
        context = await fetch_context(user_msg, user_id, req_id)

        system_prompt = create_character_prompt(
            user_name=user_name,
            frndship_title=frndship_title,
            mood=mood,
            chat_context=context,
            chat_history=chat_history or [],
            req_id=req_id,
            game_events=game_events or [],
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-chat-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                max_completion_tokens=60,
                temperature=0.9,
                top_p=0.95,
                frequency_penalty=0.2,
                presence_penalty=0.1
            )
            reply = response.choices[0].message.content
            await add_to_history(reply, role="assistant", user_id=user_id)
            return reply

        except Exception:
            return "ugh—my brain lagged, say that again?"
