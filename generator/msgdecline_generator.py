from prompts.msg_decline import lore_decline_prompt

from state.client import client

class MsgDeclineGenerator:
    def __init__(self):
        self.client = client

    async def generate(self, msg: str) -> str:
        prompt = lore_decline_prompt(msg)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except Exception:
            return "my brain glitched—ask again?"