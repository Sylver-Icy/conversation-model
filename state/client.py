from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
import os

# Central shared OpenAI client instance
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
