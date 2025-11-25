# 🧠 Conversation Model (WIP)

A modular mini-NLP system for routing user messages.
Right now it does 2 things:

### 1. Intent Classification
Figures out if the message is:
- a **command**
- **chitchat**
- **study/outside knowledge**

### 2. Command Classification
If it's a command, the model predicts **which command** it is
(from 30+ commands like buy, sell, smelt, ping, play, etc.)

Both models are trained using DistilBERT + custom JSONL datasets.

---

## 🚀 Training (WIP)

To train:

```bash
python classifiers/train_intent.py
python classifiers/train_command.py
```

Models will be saved into:

```
intent_model/
command_model/
```

Training should be done on a PC with an NVIDIA GPU (much faster).
Mac is fine for inference only.

---

## 📦 Dataset

Both datasets live in `/data/` in JSONL format:

```json
{"text": "buy 3 apples", "label": "buy"}
```

You can add more examples and retrain anytime.

---

## 🧩 Usage (very simple example)

```python
from classifiers.intent_classifier import IntentClassifier
from classifiers.command_classifier import CommandClassifier

intent = intent_model.predict(msg)

if intent == "command":
    cmd = command_model.predict(msg)
    print(cmd)
```

Argument extraction + actual command execution is still WIP.

---

## 🛠 Notes

- This project is still under construction.
- Models are NOT included in Git (ignored on purpose).
- Real user messages will be used later to improve classification.

---

## 📜 Status
WIP. Basic routing works.
Next steps: argument extraction + command runner.