"""
CommandClassifier: Predicts which specific command a user is requesting.
Loads a fine-tuned transformers sequence classification model and exposes a `predict(text)` method.
This classifier is for my bot it can be completely ignored if you want just the conversation model.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class CommandClassifier:
    """
    Loads a pretrained transformers-based classifier and exposes  `predict(text)` method
    to return one of the supported intents. The classifier expects a directory containing a
    HuggingFace-compatible tokenizer and model.
    """
    # Order of labels as trained by the model. The prediction index maps directly into this list.
    LABELS = [
        "buy", "sell", "open", "shop", "check",
        "start_race", "bet", "play", "smelt", "upgrade",
        "unlock", "leaderboard", "info", "ping", "solve_wordle",
        "quest", "create_listing", "load_marketplace",
        "buy_from_marketplace", "delete_listing", "wordle_hint",
        "commandhelp", "transfer_item", "transfer_gold", "helloveyra",
        "battle", "use", "flipcoin", "work", "introduction", "loadout"
    ]

    def __init__(self):
        # Load tokenizer and model from the local directory.
        self.tokenizer = AutoTokenizer.from_pretrained("./command_model")
        self.model = AutoModelForSequenceClassification.from_pretrained("./command_model")
        # Set model to evaluation mode since we're only running inference here.
        self.model.eval()

    def predict(self, text):
        """
        Predicts the intent of a given text string.

        Args:
            text (str): The input text to classify.

        Returns:
            str: One of the intent labels defined in LABELS.
        """
        # Tokenize and batch the input for the model.
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        # Take the highest-scoring label from the model's logits.
        pred = torch.argmax(outputs.logits, dim=1).item()
        return self.LABELS[pred]