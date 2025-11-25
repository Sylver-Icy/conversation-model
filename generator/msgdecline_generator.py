from dotenv import load_dotenv
import os

from openai import OpenAI

from prompts.msg_decline import lore_decline_prompt

load_dotenv()  # loads .env


class MsgDeclineGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, msg: str) -> str:
        prompt = lore_decline_prompt(msg)
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content