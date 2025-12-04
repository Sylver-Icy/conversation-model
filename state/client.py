from openai import OpenAI
import os

# Central shared OpenAI client instance
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
