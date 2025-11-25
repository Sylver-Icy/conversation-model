"""
Minimal test runner for the intent classification system.
Reads user input from the console and prints the predicted intent.
This file is just a quick  check for the classifier.
"""
from core.router import classify_intent

# Simple REPL loop to manually test the classifier.
while True:
    # Read user input from the console.
    msg = input("You: ")
    # Run the classifier and display the predicted intent.
    print("Intent:", classify_intent(msg))