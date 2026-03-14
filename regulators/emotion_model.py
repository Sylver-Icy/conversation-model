from logger import logger


class EmotionModel:
    """
    Manages Veyra's persistent emotional state.
    Mood deltas are supplied externally (from the action planner),
    so this class is a pure state manager with no LLM dependency.
    """

    def __init__(self):
        self.mood_state = {
            "happy": 0.0,
            "angry": 0.0,
            "irritated": 0.0,
            "sad": 0.0,
            "flirty": 0.0,
        }

    def update_mood(self, deltas: dict):
        """Apply a dict of mood deltas to the current state."""
        for mood, change in deltas.items():
            if mood in self.mood_state:
                self.mood_state[mood] += float(change)

        for mood in self.mood_state:
            self.mood_state[mood] = max(-10.0, min(10.0, self.mood_state[mood]))

    def decay_mood(self, factor: float = 0.97):
        """
        Gradually reduce all mood intensities toward zero.
        factor=0.97 means each mood is 97% of its previous value per message.
        """
        for mood in self.mood_state:
            self.mood_state[mood] *= factor

    def get_active_mood(self) -> str:
        """Return the name of the currently dominant mood."""
        return max(self.mood_state, key=self.mood_state.get)

    def log_state(self, req_id: str):
        logger.info("[REQ:%s] [Mood] %s", req_id, self.mood_state)
