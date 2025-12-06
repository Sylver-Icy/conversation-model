# 🧠 Conversation Model — Modular Agentic Dialogue Engine

A plug‑and‑play cognitive framework for powering personality‑driven AI characters, NPCs, and agent assistants.

This system doesn’t just “generate replies” — it **routes, reasons, remembers, and reacts** before speaking.

---

## ✨ Core Capabilities

### 🔹 Intent Classification
DistilBERT‑based classifier determines whether a message is:
- **Chit‑chat**
- **Command**
- **Out‑of‑lore / real‑world query**

### 🔹 Command Classification
Second classifier identifies which command was invoked (30+ supported).

### 🔹 Mood Engine
LLM‑based affect extraction + numeric mood state allows characters to:
- Change tone dynamically
- Become irritated, warm, flirty, sad, etc.
- Maintain emotional continuity across conversation

### 🔹 Semantic Memory Retrieval
Embeddings + cosine‑similarity selection surfaces relevant past dialogue or lore for contextual replies.

### 🔹 Persona Prompt Composer
Injects:
- friendship level
- mood state
- chat history
- retrieved memory
- lore rules

Result = short, non‑repetitive, in‑character responses.

### 🔹 Lore‑Aware Decline System
If the user asks real‑world / factual questions, the system produces **in‑character refusal replies** instead of hallucinating.

---

## 🚀 Architecture Overview

```
User Message
   ↓
Intent Classifier → (Chitchat / Command / Decline)
   ↓
Command Classifier (if applicable)
   ↓
Mood Engine Update
   ↓
Semantic Context Retrieval
   ↓
Persona Prompt Builder
   ↓
LLM Reply Generation
   ↓
Final In‑Character Response / Routed Command
```

---

## 🏗 Tech Stack

- **DistilBERT** for classifiers
- **FastAPI** backend
- **Embeddings + cosine similarity** for context memory
- **LLM orchestration** for mood + persona reasoning

Models are trained via custom JSONL datasets and fully re‑trainable.

---

## 📦 Training

```bash
python classifiers/train_intent.py
python classifiers/train_command.py
```

Models saved under:

```
intent_model/
command_model/
```

GPU recommended for training (Mac/CPU okay for inference).

---

## 📂 Dataset Format

Example JSONL row:

```json
{"text": "buy 3 apples", "label": "buy"}
```

Add new rows and retrain anytime.

---

## 🔨 Example Usage

```python
from engine.msg_gen_engine import Engine

engine = Engine()
reply = await engine.respond(
    text="yo hello?",
    frndship_title="Friend",
    user_id="u123",
    user_name="Sylver",
    message_history=[]
)
print(reply)
```
> ⚠️ NOTE: You must train the models first — don’t expect replies without running the training scripts.

---

## 🛠 Status

✔ Stable routing
✔ Mood + memory logic
✔ Command gating + decline handling
✔ Persona‑aligned replies

🚧 Next steps:
- Argument extraction
- Inference optimisation
- Cross‑persona spawning

---

## 📌 Notes

- Models are intentionally ignored in Git.
- Built as the engine powering **Veyra**
- `requirements.txt` is not fully maintained — development was split across macOS and Windows, so install missing packages manually if something errors.