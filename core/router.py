"""
Simple router utility that exposes a classify_intent() function.
It loads the IntentClassifier once and reuses it for all predictions.
Intended to keep the routing layer clean and minimal.
"""

from classifiers.intent_classifier import IntentClassifier

# Initialize the intent classifier once so it isn't reloaded on every call.
clf = IntentClassifier()

def classify_intent(message: str):
    """
    Runs the intent classifier on a message and returns the predicted label.

    Args:
        message (str): User input to classify.

    Returns:
        str: One of the intent categories produced by the classifier.
    """
    return clf.predict(message)