"""
Lightweight routing utility for testing.
Loads the intent and command classifiers once and exposes simple functions
to classify a message at a high level (intent) and at a command level.
"""
from logger import logger

from classifiers.intent_classifier import IntentClassifier
from classifiers.command_classifier import CommandClassifier


# Initialize the  classifiers once so it isn't reloaded on every call.
intent_clf = IntentClassifier()
cmd_clf = CommandClassifier()


def main_router(message: str, req_id: str):
    """
    Routes the message through the intent classifier.
    If the intent is 'command', it runs the command classifier.

    Args:
        message (str): User input to route.

    Returns:
        str: Either an intent label or a command label.
    """
    intent = classify_intent(message)
    if intent == "command":
        cmd = classify_command(message)
        logger.info(f"[REQ {req_id}] [Intent] [{message} was classiefier as {cmd}]")
        return ("command", cmd)

    logger.info(f"[REQ {req_id}] [Intent] [{message} was classiefier as {intent}]")
    return ("intent", intent)


def classify_intent(message: str):
    """
    Runs the intent classifier on a message and returns the predicted label.

    Args:
        message (str): User input to classify.

    Returns:
        str: One of the intent categories produced by the classifier.
    """
    return intent_clf.predict(message)


def classify_command(message: str):
    """
    Runs the command classifier on a message and returns the predicted label.

    Args:
        message (str): User input to classify.

    Returns:
        str: The predicted command label.
    """
    return cmd_clf.predict(message)
