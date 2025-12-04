"""
IntentClassifier: A lightweight wrapper around a transformers sequence classification model
used to categorize user messages into high-level intents such as 'command', 'study', or 'chitchat'.
This module is fully modular and can be reused in any conversation engine project.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

class IntentClassifier:
    """
    Loads a pretrained transformers-based classifier and exposes  `predict(text)` method
    to return one of the supported intents. The classifier expects a directory containing a
    HuggingFace-compatible tokenizer and model.
    """
    # Order of labels as trained by the model. The prediction index maps directly into this list.
    LABELS = ["command", "study", "chitchat"]

    def __init__(self):
        # Load tokenizer and model from the local directory.
        self.tokenizer = AutoTokenizer.from_pretrained("./intent_model")
        self.model = AutoModelForSequenceClassification.from_pretrained("./intent_model")
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
        # Normalize input text
        text = text.strip().lower()

        # Tokenize and batch the input for the model.
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)

        # Convert logits to probabilities
        probs = F.softmax(outputs.logits, dim=1)
        max_prob, pred_idx = torch.max(probs, dim=1)

        # Apply threshold: return 'chitchat' if confidence is too low
        if max_prob.item() < 0.15:
            return "chitchat"

        return self.LABELS[pred_idx.item()]