from dotenv import load_dotenv
load_dotenv()

import os

from openai import AsyncOpenAI


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is required to initialize the OpenAI client.")

# Central shared OpenAI client instance
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
