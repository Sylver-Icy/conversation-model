from logger import logger

import json

from state.client import client


class EmotionModel:
    """
    Extracts mood deltas from a user message using a lightweight OpenAI model.
    Updates Veyra's emotional state by producing numeric changes for:
    happy, angry, irritated, sad, flirty.
    """

    def __init__(self):
        self.client = client


        # Internal persistent mood state (modifiable by engine)
        self.mood_state = {
            "happy": 0.0,
            "angry": 0.0,
            "irritated": 0.0,
            "sad": 0.0,
            "flirty": 0.0
        }

    async def extract_deltas(self, message: str, req_id: str) -> dict:
        """
        Calls a small llm to extract integer mood deltas.
        Returns a dict like:
        {"happy": 1, "angry": 0, "irritated": 0.5, "sad": 0, "flirty": -1}
        """

        prompt = (
            "You are an emotion-analysis model for a fantasy NPC.\n\n"
            f"User message: '{message}'\n\n"
            "Your task: Output ONLY a JSON dictionary with numeric deltas for these moods:\n"
            "happy, angry, irritated, sad, flirty.\n\n"
            "Rules:\n"
            "- Deltas must be integers or floats.\n"
            "- Positive = increases that mood.\n"
            "- Negative = decreases that mood.\n"
            "- No explanations. No extra text.\n\n"
            "Examples:\n"
            "Message: 'you're so fat lol'\n"
            "Output: {\"happy\": -1, \"angry\": 2, \"irritated\": 1, \"sad\": +0.4, \"flirty\": -2}\n\n"
            "Message: 'omg you are so cute'\n"
            "Output: {\"happy\": 2, \"angry\": -1, \"irritated\": 0, \"sad\": 0, \"flirty\": 3}\n\n"
            "Now output the JSON for the user message above."
        )

        response = await self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You classify emotion deltas for mood analysis. Respond ONLY with JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content

        try:
            deltas = json.loads(raw)
        except:
            # fallback if model adds fluff
            try:
                import re
                json_str = re.search(r"\{.*\}", raw, re.S).group(0)
                deltas = json.loads(json_str)
            except:
                # worst-case zero deltas
                deltas = {
                    "happy": 0,
                    "angry": 0,
                    "irritated": 0,
                    "sad": 0,
                    "flirty": 0
                }

        logger.info(f"[REQ {req_id}] [Mood Delta] Mood change coz of {message} -> {deltas}")
        return deltas

    def update_mood(self, deltas: dict):
        """
        Applies extracted deltas to existing mood state.
        """

        for mood, change in deltas.items():
            if mood in self.mood_state:
                self.mood_state[mood] += float(change)

        #clamp values to avoid infinite growth
        for mood in self.mood_state:
            self.mood_state[mood] = max(-10, min(10, self.mood_state[mood]))

    def decay_mood(self, factor: float = 0.95):
        """
        Slowly reduce mood intensity over time.
        factor=0.95 → each mood reduces to 95% of previous value.
        """

        for mood in self.mood_state:
            self.mood_state[mood] *= factor

    def get_active_mood(self) -> str:
        """
        Determines which mood is currently dominant.
        Returns the mood name with highest value.
        """

        return max(self.mood_state, key=self.mood_state.get)
