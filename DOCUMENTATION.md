# 🧠 Conversation Model — Complete Technical Documentation

> **Last Updated:** February 2026  
> **Repository:** `Sylver-Icy/conversation-model`  
> **Version:** 1.0.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Folder & File Structure](#3-folder--file-structure)
4. [System Architecture](#4-system-architecture)
5. [Setup & Installation](#5-setup--installation)
6. [Configuration](#6-configuration)
7. [Core Features](#7-core-features)
8. [API / Functions Reference](#8-api--functions-reference)
9. [Error Handling](#9-error-handling)

---

## 1. Project Overview

### What the Project Does

The **Conversation Model** is a modular agentic dialogue engine designed to power personality-driven AI characters, NPCs, and agent assistants. Unlike simple chatbot systems that merely generate replies, this system:

- **Routes** messages through intent classification
- **Reasons** about context using semantic memory
- **Remembers** past interactions via embedding-based retrieval
- **Reacts** emotionally with a dynamic mood system
- **Responds** with personality-consistent, in-character messages

The primary use case is powering **Veyra**, a sassy, witty, magical character from a fantasy realm called Natlade who interacts with users through Discord.

### Why It Exists

Traditional chatbots lack:
- **Emotional continuity** across conversations
- **Memory of past interactions**
- **Command routing** for multi-purpose bots
- **Persona consistency** when refusing out-of-scope questions

This project solves these problems by creating a layered cognitive framework that processes messages through multiple stages before generating a final response.

### Core Goals

1. **Intent Classification**: Determine if a message is chitchat, a command, or an out-of-lore question
2. **Command Routing**: Identify which specific bot command the user wants
3. **Emotional State Management**: Track and update mood across conversations
4. **Semantic Memory**: Retrieve relevant past conversations for context
5. **Persona-Consistent Responses**: Generate short, in-character replies that never break immersion
6. **Lore-Safe Declines**: Reject real-world questions in-character without hallucinating

### High-Level Architecture Explanation

The system uses a pipeline architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER MESSAGE                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     INTENT CLASSIFIER (DistilBERT)                       │
│                  Outputs: "chitchat" | "command" | "study"               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
        ┌──────────┐         ┌──────────┐         ┌──────────┐
        │ CHITCHAT │         │ COMMAND  │         │  STUDY   │
        │ PIPELINE │         │ PIPELINE │         │ (DECLINE)│
        └──────────┘         └──────────┘         └──────────┘
              │                     │                     │
              ▼                     ▼                     ▼
        ┌──────────┐         ┌──────────┐         ┌──────────┐
        │ Mood     │         │ Command  │         │ Lore     │
        │ Engine   │         │ Classifier│        │ Decline  │
        └──────────┘         └──────────┘         │ Generator│
              │                     │              └──────────┘
              ▼                     │
        ┌──────────┐                │
        │ Context  │                │
        │ Retrieval│                │
        └──────────┘                │
              │                     │
              ▼                     ▼
        ┌──────────┐         ┌──────────┐
        │ Persona  │         │ Command  │
        │ Prompt   │         │ Decline  │
        │ Builder  │         │ or Label │
        └──────────┘         └──────────┘
              │
              ▼
        ┌──────────┐
        │ LLM      │
        │ Response │
        └──────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FINAL RESPONSE                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack

### Languages

| Language | Version | Purpose |
|----------|---------|---------|
| Python   | 3.10+   | Primary language for all modules |

### Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| FastAPI   | Latest  | HTTP API server for receiving chat requests |
| Transformers | 4.36.2 | HuggingFace library for DistilBERT classifiers |
| PyTorch   | Latest  | Deep learning backend for model inference |

### Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `transformers` | 4.36.2 | Loading and running DistilBERT models |
| `datasets` | 2.14.5 | Loading JSONL training data |
| `torch` | Latest | Tensor operations, model inference |
| `tqdm` | Latest | Progress bars during training |
| `accelerate` | Latest | Distributed/mixed-precision training |
| `uvicorn` | Latest | ASGI server to run FastAPI |
| `pydantic` | Latest | Data validation for API request/response models |
| `python-dotenv` | Latest | Loading environment variables from `.env` |
| `openai` | Latest | AsyncOpenAI client for LLM calls |
| `numpy` | Latest | Numerical operations for embeddings |

### Tools

| Tool | Purpose |
|------|---------|
| **DistilBERT** | Lightweight BERT variant for fast intent/command classification |
| **OpenAI GPT API** | LLM for mood extraction, persona responses, and decline messages |
| **OpenAI Embeddings API** | `text-embedding-3-small` model for semantic memory |

### Why Each Technology Was Chosen

- **FastAPI**: Async-native, automatic OpenAPI docs, excellent performance for real-time chat
- **DistilBERT**: 40% smaller than BERT with 97% performance; fast inference on CPU
- **Transformers**: Industry-standard for loading HuggingFace models
- **OpenAI API**: High-quality LLM responses with JSON mode support
- **Pydantic**: Type safety and validation for API contracts
- **NumPy**: Efficient cosine similarity calculations for context retrieval

---

## 3. Folder & File Structure

```
conversation-model/
├── .gitignore              # Git ignore rules for models, envs, logs
├── readme.md               # Project overview and quick start
├── requirements.txt        # Python dependencies
├── main.py                 # FastAPI application entry point
├── logger.py               # Centralized logging configuration
│
├── core/                   # Core routing logic
│   └── router.py           # Intent → Command routing
│
├── engine/                 # Main orchestration engine
│   └── msg_gen_engine.py   # Engine class coordinating all generators
│
├── generator/              # Response generation modules
│   ├── msg_generator.py           # Chitchat response generation
│   ├── msgdecline_generator.py    # Lore-based decline generation
│   └── commanddecline_generator.py # Command decline generation
│
├── classifiers/            # ML classification models
│   ├── intent_classifier.py   # Intent classification inference
│   ├── command_classifier.py  # Command classification inference
│   ├── train_intent.py        # Intent model training script
│   └── train_command.py       # Command model training script
│
├── regulators/             # State management modules
│   ├── emotion_model.py    # Mood tracking and delta extraction
│   └── context_model.py    # Semantic memory and context retrieval
│
├── prompts/                # LLM prompt templates
│   ├── character_profile.py   # Main persona prompt builder
│   ├── command_decline.py     # Command decline prompt builder
│   └── msg_decline.py         # Lore decline prompt builder
│
└── state/                  # Shared state and clients
    └── client.py           # AsyncOpenAI client singleton
```

### Detailed File Explanations

#### Root Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with `/chat` endpoint. Receives messages, calls Engine, returns responses. Handles API key authentication. |
| `logger.py` | Configures Python logging with console (DEBUG) and file (`conversation.log`, INFO) handlers. Timestamps all log entries. |
| `requirements.txt` | Lists Python dependencies. Note: Not fully maintained; may need manual package installation. |
| `readme.md` | Quick project overview, architecture diagram, training instructions, example usage. |
| `.gitignore` | Excludes model weights, checkpoints, virtual environments, logs, and macOS files. |

#### `core/router.py`

The **routing hub** that determines message flow:
- Loads both classifiers once at module import
- `main_router()`: Classifies intent; if "command", also classifies the command
- Returns tuple: `("intent", label)` or `("command", cmd_label)`

#### `engine/msg_gen_engine.py`

The **orchestration layer** that coordinates all generators:
- `Engine` class holds instances of all three generators
- `respond()` method routes to correct generator based on classification
- Handles chitchat → mood → context → LLM pipeline
- Handles command decline vs direct command return

#### `generator/` Directory

| File | Class | Purpose |
|------|-------|---------|
| `msg_generator.py` | `ChatGenerator` | Full chitchat pipeline: mood update → context fetch → persona prompt → LLM call |
| `msgdecline_generator.py` | `MsgDeclineGenerator` | Generates in-character declines for real-world questions |
| `commanddecline_generator.py` | `CommandDeclineGenerator` | Generates syntax correction messages for invalid commands |

#### `classifiers/` Directory

| File | Purpose |
|------|---------|
| `intent_classifier.py` | Loads `./intent_model` and predicts one of: `["command", "study", "chitchat"]` |
| `command_classifier.py` | Loads `./command_model` and predicts specific command labels |
| `train_intent.py` | Training script for intent model using `data/intent.jsonl` |
| `train_command.py` | Training script for command model using `data/commands.jsonl` |

#### `regulators/` Directory

| File | Purpose |
|------|---------|
| `emotion_model.py` | Tracks mood state (happy, angry, irritated, sad, flirty). Uses LLM to extract deltas from messages. |
| `context_model.py` | In-memory semantic history. Embeds messages, retrieves by cosine similarity. |

#### `prompts/` Directory

| File | Function | Purpose |
|------|----------|---------|
| `character_profile.py` | `create_character_prompt()` | Builds main persona system prompt with mood, friendship, history, context |
| `command_decline.py` | `create_command_decline_prompt()` | Builds decline prompt for invalid/multi-arg commands |
| `msg_decline.py` | `lore_decline_prompt()` | Builds decline prompt for real-world questions |

#### `state/` Directory

| File | Purpose |
|------|---------|
| `client.py` | Singleton `AsyncOpenAI` client shared across all modules. Loads API key from environment. |

---

## 4. System Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HTTP REQUEST                                    │
│                           POST /chat                                         │
│    { text, frndship_title, user_id, user_name, message_history }            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              main.py                                         │
│                                                                              │
│  1. Validate API key (CONVO_MODEL_API_KEY)                                  │
│  2. Generate request ID (uuid)                                               │
│  3. Log incoming message                                                     │
│  4. Call Engine.respond()                                                    │
│  5. Log reply and duration                                                   │
│  6. Return reply                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Engine.respond()                                     │
│                     engine/msg_gen_engine.py                                 │
│                                                                              │
│  1. Call main_router(message) → (route_type, label)                         │
│  2. Branch based on route_type:                                              │
│     - "intent" + "chitchat" → ChatGenerator.generate()                      │
│     - "intent" + "study"    → MsgDeclineGenerator.generate()                │
│     - "command" + valid cmd → return command label directly                  │
│     - "command" + LABEL_8   → CommandDeclineGenerator.generate()            │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│ ChatGenerator     │    │ MsgDeclineGen     │    │ CommandDeclineGen │
│                   │    │                   │    │                   │
│ 1. Extract mood   │    │ 1. Build lore     │    │ 1. Build command  │
│    deltas (LLM)   │    │    decline prompt │    │    decline prompt │
│ 2. Update mood    │    │ 2. Call LLM       │    │ 2. Call LLM       │
│    state          │    │ 3. Return decline │    │ 3. Return decline │
│ 3. Get active     │    │                   │    │                   │
│    mood           │    └───────────────────┘    └───────────────────┘
│ 4. Fetch context  │
│    (embeddings)   │
│ 5. Build persona  │
│    prompt         │
│ 6. Call LLM       │
│ 7. Add to history │
│ 8. Return reply   │
└───────────────────┘
```

### Module Interaction Diagram

```
                    ┌─────────────────────────────────────┐
                    │              main.py                │
                    │           (FastAPI App)             │
                    └──────────────┬──────────────────────┘
                                   │
                                   │ imports
                                   ▼
                    ┌─────────────────────────────────────┐
                    │         Engine (engine/)            │
                    │       msg_gen_engine.py             │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   core/router   │     │   generator/    │     │   state/client  │
│                 │     │                 │     │                 │
│ - main_router() │     │ - ChatGenerator │     │ - AsyncOpenAI   │
│ - classify_*()  │     │ - MsgDecline    │     │   client        │
└────────┬────────┘     │ - CmdDecline    │     └────────┬────────┘
         │              └────────┬────────┘              │
         │                       │                       │
         ▼                       ▼                       │
┌─────────────────┐     ┌─────────────────┐              │
│   classifiers/  │     │   regulators/   │              │
│                 │     │                 │              │
│ - IntentClf     │     │ - EmotionModel  │◄─────────────┤
│ - CommandClf    │     │ - context_model │◄─────────────┤
└─────────────────┘     └────────┬────────┘              │
                                 │                       │
                                 ▼                       │
                        ┌─────────────────┐              │
                        │    prompts/     │              │
                        │                 │              │
                        │ - char_profile  │              │
                        │ - cmd_decline   │              │
                        │ - msg_decline   │              │
                        └─────────────────┘              │
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │     OpenAI API      │
                                              │                     │
                                              │ - Chat completions  │
                                              │ - Embeddings        │
                                              └─────────────────────┘
```

### Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           IN-MEMORY HISTORY                                  │
│                        (regulators/context_model.py)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   history = [                                                                │
│     {                                                                        │
│       "content": "hello veyra",         # Original message text             │
│       "embedding": np.array([...]),     # 1536-dim embedding vector         │
│       "role": "user",                   # "user" or "assistant"             │
│       "user_id": 12345                  # User identifier (nullable)        │
│     },                                                                       │
│     ...                                                                      │
│   ]                                                                          │
│                                                                              │
│   Max entries: 150 (FIFO eviction)                                          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   RETRIEVAL ALGORITHM:                                                       │
│                                                                              │
│   1. Embed query message                                                     │
│   2. Split history into PERSONAL (same user_id) and GLOBAL (other users)   │
│   3. Score each item by cosine similarity (+0.05 boost for personal)        │
│   4. Take top 10 from each pool                                              │
│   5. Merge and re-rank                                                       │
│   6. Filter by threshold (0.35)                                              │
│   7. Return top 7 contexts                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mood State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MOOD STATE                                         │
│                     (regulators/emotion_model.py)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   mood_state = {                                                             │
│     "happy":     0.0,    # Range: [-10, 10]                                 │
│     "angry":     0.0,    # Range: [-10, 10]                                 │
│     "irritated": 0.0,    # Range: [-10, 10]                                 │
│     "sad":       0.0,    # Range: [-10, 10]                                 │
│     "flirty":    0.0     # Range: [-10, 10]                                 │
│   }                                                                          │
│                                                                              │
│   OPERATIONS:                                                                │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│   │ extract_deltas  │ ──► │  update_mood    │ ──► │ get_active_mood │       │
│   │ (LLM call)      │     │ (apply + clamp) │     │ (max value)     │       │
│   └─────────────────┘     └─────────────────┘     └─────────────────┘       │
│                                                                              │
│   DECAY:                                                                     │
│   decay_mood(0.95) → each mood *= 0.95 (gradual return to neutral)          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Setup & Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **OpenAI API key** (for LLM and embeddings)
- **GPU** (recommended for training; CPU works for inference)

### Step-by-Step Local Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Sylver-Icy/conversation-model.git
cd conversation-model
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The `requirements.txt` may be incomplete. Install additional packages as needed:

```bash
pip install fastapi uvicorn python-dotenv openai numpy pydantic
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following variables:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
CONVO_MODEL_API_KEY=your-secret-api-key-for-authentication
```

#### 5. Prepare Training Data

Create a `data/` directory with JSONL files:

```bash
mkdir data
```

**`data/intent.jsonl`** (example):
```jsonl
{"text": "hello how are you", "label": "chitchat"}
{"text": "buy 3 apples", "label": "command"}
{"text": "what is python", "label": "study"}
```

**`data/commands.jsonl`** (example):
```jsonl
{"text": "check my wallet", "label": "check_wallet"}
{"text": "buy a sword", "label": "other_command"}
{"text": "flip a coin", "label": "flip_coin"}
```

#### 6. Train Classification Models

```bash
# Train intent classifier
python classifiers/train_intent.py

# Train command classifier
python classifiers/train_command.py
```

Models are saved to `./intent_model/` and `./command_model/`.

#### 7. Run the Server

```bash
python main.py
```

The server starts at `http://127.0.0.1:8000`.

#### 8. Test the API

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "api_key: your-secret-api-key" \
  -d '{
    "text": "hello veyra!",
    "frndship_title": "Friend",
    "user_id": 12345,
    "user_name": "Player",
    "message_history": []
  }'
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key for GPT and embeddings |
| `CONVO_MODEL_API_KEY` | Yes | Secret key for API authentication; requests without this are rejected with 403 |

---

## 6. Configuration

### Model Configuration

#### Intent Classifier (`classifiers/train_intent.py`)

| Setting | Value | Description |
|---------|-------|-------------|
| `model_name` | `"distilbert-base-uncased"` | Base model for fine-tuning |
| `num_labels` | `3` | Number of intent classes |
| `batch_size` | `8` | Training batch size |
| `epochs` | `5` | Number of training epochs |
| `learning_rate` | `4e-5` | Learning rate for optimizer |
| `output_dir` | `"./intent_model"` | Save location for trained model |

**Intent Labels:**
```python
labels = {"command": 0, "study": 1, "chitchat": 2}
```

#### Command Classifier (`classifiers/train_command.py`)

| Setting | Value | Description |
|---------|-------|-------------|
| `model_name` | `"distilbert-base-uncased"` | Base model for fine-tuning |
| `num_labels` | `9` | Number of command classes |
| `batch_size` | `8` | Training batch size |
| `epochs` | `5` | Number of training epochs |
| `learning_rate` | `4e-5` | Learning rate for optimizer |
| `output_dir` | `"./command_model"` | Save location for trained model |

**Command Labels:**
```python
labels = {
    "check_wallet": 0,
    "check_exp": 1,
    "check_energy": 2,
    "check_inventory": 3,
    "quest": 4,
    "shop": 5,
    "start_race": 6,
    "flip_coin": 7,
    "other_command": 8
}
```

### Inference Configuration

#### Intent Classifier Threshold (`classifiers/intent_classifier.py`)

```python
if max_prob.item() < 0.35:
    return "chitchat"  # Default to chitchat if confidence is low
```

#### Context Retrieval Parameters (`regulators/context_model.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_k` | `7` | Maximum contexts to return |
| `per_group` | `10` | Top entries from personal/global pools |
| `max_history` | `150` | Maximum entries in memory before FIFO eviction |
| `threshold` | `0.35` | Minimum cosine similarity to include context |
| `personal_boost` | `+0.05` | Similarity boost for same-user messages |

#### LLM Generation Parameters (`generator/msg_generator.py`)

```python
model="gpt-5-chat-latest"
max_tokens=60
temperature=0.9
top_p=0.95
frequency_penalty=0.2
presence_penalty=0.1
```

#### Mood State Bounds (`regulators/emotion_model.py`)

```python
# Clamp values to avoid infinite growth
for mood in self.mood_state:
    self.mood_state[mood] = max(-10, min(10, self.mood_state[mood]))
```

### Friendship Levels (`prompts/character_profile.py`)

```python
FRNDSHIP_MAP = {
    "Stranger": "cold, distant, dismissive, teasing with suspicion",
    "Acquaintance": "slightly polite but still mocking and uninterested",
    "Casual": "light teasing, playful sarcasm, mild smugness",
    "Friend": "supportive sass, playful banter, soft approval",
    "Close Friend": "warm teasing, insider jokes, occasional praise",
    "Bestie": "affectionate bullying, chaotic energy, admiration mixed with dominance",
    "Veyra's favourite 💖": "overprotective, dominant flirty energy, high praise and possessive affection"
}
```

### Command Map (`prompts/command_decline.py`)

```python
COMMAND_MAP = {
    "buy": "!buy — Purchase items from the shop",
    "sell": "!sell — Sell items the shop accepts",
    "open": "!open — Open a lootbox",
    "bet": "!bet — Bet on an ongoing race",
    "play": "!play — Number-guessing game",
    "smelt": "/smelt — Smelt ores into bars",
    "upgrade": "!upgrade — Upgrade a building",
    "unlock": "!unlock — Unlock a building",
    "leaderboard": "/leaderboard — View top players",
    "info": "!info — Item information lookup",
    "ping": "!ping — Check bot latency",
    "solve_wordle": "!solve_wordle — Start Wordle solver session",
    "wordle_hint": "/wordle_hint — Get next Wordle hint",
    "help": "/help — Opens main help menu",
    "commandhelp": "!commandhelp — Detailed help for any command",
    "transfer_item": "/transfer_item — Transfer an item to a user",
    "transfer_gold": "/transfer_gold — Transfer gold to a user",
    "battle": "/battle — Challenge someone to a duel",
    "work": "!work — Do a job to earn gold",
    "load_marketplace": "/load_marketplace — View marketplace listings",
    "create_listing": "/create_listing — Create a marketplace listing",
    "buy_from_marketplace": "/buy_from_marketplace — Buy a marketplace listing",
    "delete_listing": "/delete_listing — Delete your listing",
    "use": "!use — Use a consumable item",
    "loadout": "/loadout — Edit your equipment loadout",
    "introduction": "/introduction — Open intro form",
}
```

### Logging Configuration (`logger.py`)

```python
logger.setLevel(logging.DEBUG)           # Logger level
console_handler.setLevel(logging.DEBUG)  # Console shows all logs
file_handler.setLevel(logging.INFO)      # File only shows INFO and above
```

**Log format:**
```
[HH:MM:SS] [LEVEL] ConversationModel: message
```

**Log file:** `conversation.log`

---

## 7. Core Features

### 7.1 Intent Classification

**What it does:** Categorizes incoming messages into three high-level intents.

**How it works internally:**
1. User message is normalized (stripped, lowercased)
2. Tokenized using DistilBERT tokenizer
3. Passed through fine-tuned classification model
4. Softmax applied to logits to get probabilities
5. If max probability < 0.35, defaults to "chitchat"
6. Otherwise, returns the label with highest probability

**Which files implement it:**
- `classifiers/intent_classifier.py` — Inference
- `classifiers/train_intent.py` — Training
- `core/router.py` — Integration

**Intent labels:**
| Label | Description |
|-------|-------------|
| `chitchat` | Casual conversation, greetings, banter |
| `command` | User wants to execute a bot command |
| `study` | Real-world/factual question (decline) |

---

### 7.2 Command Classification

**What it does:** Identifies which specific command the user wants to execute.

**How it works internally:**
1. Only runs if intent is classified as "command"
2. Message normalized and tokenized
3. Passed through command classifier
4. Uses `id2label` mapping from model config
5. Returns predicted command label

**Which files implement it:**
- `classifiers/command_classifier.py` — Inference
- `classifiers/train_command.py` — Training
- `core/router.py` — Integration

**Command labels:**
| Label | Description |
|-------|-------------|
| `check_wallet` | View currency balance |
| `check_exp` | View experience points |
| `check_energy` | View energy status |
| `check_inventory` | View items |
| `quest` | Quest-related actions |
| `shop` | Shop-related actions |
| `start_race` | Racing game |
| `flip_coin` | Coin flip game |
| `other_command` | Multi-argument command (requires decline) |

---

### 7.3 Mood Engine

**What it does:** Tracks and updates character emotional state across conversations.

**How it works internally:**
1. For each chitchat message, calls LLM to extract mood deltas
2. LLM returns JSON with numeric changes for each mood dimension
3. Deltas are applied to persistent mood state
4. Values are clamped to [-10, 10] range
5. Active mood (highest value) influences response tone

**Which files implement it:**
- `regulators/emotion_model.py` — Core logic
- `generator/msg_generator.py` — Integration

**Mood dimensions:**
| Mood | Range | Effect |
|------|-------|--------|
| `happy` | -10 to 10 | Friendlier, more playful |
| `angry` | -10 to 10 | Sharper, more confrontational |
| `irritated` | -10 to 10 | Shorter, more dismissive |
| `sad` | -10 to 10 | Softer, more subdued |
| `flirty` | -10 to 10 | More teasing, suggestive |

---

### 7.4 Semantic Memory Retrieval

**What it does:** Retrieves relevant past messages to provide conversation context.

**How it works internally:**
1. Incoming message is embedded using OpenAI's text-embedding-3-small
2. History is split into personal (same user_id) and global pools
3. Each item scored by cosine similarity (personal gets +0.05 boost)
4. Top 10 from each pool merged and re-ranked
5. Items below 0.35 similarity threshold filtered out
6. Top 7 contexts returned for prompt injection
7. New message added to history (if > 3 chars)
8. History capped at 150 entries (FIFO eviction)

**Which files implement it:**
- `regulators/context_model.py` — Core logic
- `generator/msg_generator.py` — Integration

---

### 7.5 Persona Prompt Builder

**What it does:** Constructs the system prompt that defines character behavior.

**How it works internally:**
1. Receives user name, friendship level, mood, context, and history
2. Maps friendship level to behavioral description
3. Builds multi-section prompt with:
   - Character identity
   - Social dynamics rules
   - Lore rules
   - Memory/context rules
   - Style rules
4. Returns complete system prompt for LLM

**Which files implement it:**
- `prompts/character_profile.py` — Main prompt builder
- `generator/msg_generator.py` — Integration

---

### 7.6 Lore-Safe Decline System

**What it does:** Rejects real-world questions in-character without breaking immersion.

**How it works internally:**
1. Triggered when intent is classified as "study"
2. Builds decline prompt with user's question
3. Instructs LLM to act confused/dismissive
4. Returns short, in-character refusal

**Which files implement it:**
- `prompts/msg_decline.py` — Prompt builder
- `generator/msgdecline_generator.py` — Generator class
- `engine/msg_gen_engine.py` — Routing

---

### 7.7 Command Decline System

**What it does:** Handles commands that require specific syntax or arguments.

**How it works internally:**
1. Triggered when command is classified as "LABEL_8" (other_command)
2. Looks up command in COMMAND_MAP
3. If found, builds prompt to correct syntax
4. If not found, builds prompt to roast and redirect to /help
5. Returns short, sassy correction message

**Which files implement it:**
- `prompts/command_decline.py` — Prompt builder with COMMAND_MAP
- `generator/commanddecline_generator.py` — Generator class
- `engine/msg_gen_engine.py` — Routing

---

## 8. API / Functions Reference

### 8.1 FastAPI Endpoints

#### `POST /chat`

**Purpose:** Main endpoint for receiving user messages and returning character responses.

**File:** `main.py`

**Request Model:**
```python
class Message(BaseModel):
    text: str                # User's message text
    frndship_title: str      # Friendship level key
    user_id: int             # Unique user identifier
    user_name: str           # Display name for the user
    message_history: list    # Recent chat history for context
```

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `api_key` | Yes | Must match `CONVO_MODEL_API_KEY` env var |

**Response:** `str` — Character's reply message

**Side Effects:**
- Updates mood state
- Adds message to semantic memory
- Writes to log file

**Example Usage:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "api_key: your-secret-key" \
  -d '{
    "text": "hey veyra!",
    "frndship_title": "Friend",
    "user_id": 12345,
    "user_name": "Player",
    "message_history": ["Player: hi", "Veyra: hey~"]
  }'
```

---

### 8.2 Core Router Functions

#### `main_router(message: str, req_id: str) -> tuple`

**Purpose:** Routes messages through intent and command classification.

**File:** `core/router.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `message` | `str` | User's input message |
| `req_id` | `str` | Request identifier for logging |

**Returns:** `tuple[str, str]` — `("intent", label)` or `("command", cmd)`

**Side Effects:** Logs classification results

**Example:**
```python
route_type, label = main_router("buy 3 apples", "abc123")
# Returns: ("command", "check_wallet") or similar
```

---

#### `classify_intent(message: str) -> str`

**Purpose:** Runs intent classifier on a message.

**File:** `core/router.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `message` | `str` | User's input message |

**Returns:** `str` — One of `["command", "study", "chitchat"]`

**Side Effects:** None

---

#### `classify_command(message: str) -> str`

**Purpose:** Runs command classifier on a message.

**File:** `core/router.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `message` | `str` | User's input message |

**Returns:** `str` — Command label from model config

**Side Effects:** None

---

### 8.3 Engine Class

#### `class Engine`

**Purpose:** Main orchestration class coordinating all generators.

**File:** `engine/msg_gen_engine.py`

**Constructor:**
```python
def __init__(self):
    self.chat = ChatGenerator()      # Chitchat generator
    self.cmd_dlcn = CommandDeclineGenerator()  # Command decline
    self.msg_dlcn = MsgDeclineGenerator()      # Lore decline
```

---

#### `Engine.respond(...) -> str`

**Purpose:** Main entry point for generating responses.

**File:** `engine/msg_gen_engine.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `message` | `str` | User's input message |
| `user_id` | `int` | Unique user identifier |
| `user_name` | `str` | Display name |
| `frndship_title` | `str` | Friendship level key |
| `chat_history` | `list` | Recent message history |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — Generated response

**Side Effects:**
- Updates mood state (for chitchat)
- Adds to semantic memory (for chitchat)
- Logs all operations

**Internal Logic:**
```python
route_type, label = main_router(message, req_id)

if route_type == "intent":
    if label == "chitchat":
        return await self.chat.generate(...)
    else:  # study
        return await self.msg_dlcn.generate(...)

if route_type == "command":
    if label != "LABEL_8":
        return label  # Direct command return
    else:
        return await self.cmd_dlcn.generate(...)
```

---

### 8.4 Generator Classes

#### `class ChatGenerator`

**Purpose:** Generates chitchat responses with mood and context.

**File:** `generator/msg_generator.py`

**Constructor:**
```python
def __init__(self):
    self.client = client  # AsyncOpenAI
```

---

#### `ChatGenerator.generate(...) -> str`

**Purpose:** Full chitchat pipeline from mood to LLM response.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `user_msg` | `str` | Required | User's message |
| `user_id` | `int` | Required | User identifier |
| `user_name` | `str` | `"Player"` | Display name |
| `frndship_title` | `str` | `"Stranger"` | Friendship level |
| `chat_history` | `list` | `[]` | Recent history |
| `req_id` | `str` | `"000"` | Request ID |

**Returns:** `str` — Generated in-character response

**Side Effects:**
- Calls `veyra.extract_deltas()` and `veyra.update_mood()`
- Calls `fetch_context()` and `add_to_history()`
- Makes OpenAI API call

**Error Handling:** Returns `"ugh—my brain lagged, say that again?"` on exception

---

#### `class MsgDeclineGenerator`

**Purpose:** Generates lore-based decline messages.

**File:** `generator/msgdecline_generator.py`

---

#### `MsgDeclineGenerator.generate(msg: str, req_id: str) -> str`

**Purpose:** Creates in-character refusal for real-world questions.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `msg` | `str` | The real-world question |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — In-character decline message

**Side Effects:** Makes OpenAI API call

**Error Handling:** Returns `"my brain glitched—ask again?"` on exception

---

#### `class CommandDeclineGenerator`

**Purpose:** Generates command syntax correction messages.

**File:** `generator/commanddecline_generator.py`

---

#### `CommandDeclineGenerator.generate(command: str, req_id: str) -> str`

**Purpose:** Creates sassy syntax correction for invalid commands.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `command` | `str` | The detected command key |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — Syntax correction message

**Side Effects:** Makes OpenAI API call

**Error Handling:** Returns `"ugh—my brain lagged. ask properly again."` on exception

---

### 8.5 Classifier Classes

#### `class IntentClassifier`

**Purpose:** DistilBERT-based intent classification.

**File:** `classifiers/intent_classifier.py`

**Class Attributes:**
```python
LABELS = ["command", "study", "chitchat"]
```

**Constructor:**
```python
def __init__(self):
    self.tokenizer = AutoTokenizer.from_pretrained("./intent_model")
    self.model = AutoModelForSequenceClassification.from_pretrained("./intent_model")
    self.model.eval()
```

---

#### `IntentClassifier.predict(text: str) -> str`

**Purpose:** Predicts intent of a message.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Input text to classify |

**Returns:** `str` — One of `["command", "study", "chitchat"]`

**Side Effects:** None

**Internal Logic:**
1. Normalize: `text.strip().lower()`
2. Tokenize with truncation/padding
3. Run model inference
4. Apply softmax to logits
5. If max probability < 0.35, return "chitchat"
6. Otherwise, return label at argmax index

---

#### `class CommandClassifier`

**Purpose:** DistilBERT-based command classification.

**File:** `classifiers/command_classifier.py`

**Constructor:**
```python
def __init__(self):
    self.tokenizer = AutoTokenizer.from_pretrained("./command_model")
    self.model = AutoModelForSequenceClassification.from_pretrained("./command_model")
    self.model.eval()
    self.id2label = self.model.config.id2label
```

---

#### `CommandClassifier.predict(text: str) -> str`

**Purpose:** Predicts which command the message refers to.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Input text to classify |

**Returns:** `str` — Command label (e.g., `"check_wallet"`, `"flip_coin"`)

**Side Effects:** None

---

### 8.6 Regulator Classes and Functions

#### `class EmotionModel`

**Purpose:** Mood tracking and delta extraction.

**File:** `regulators/emotion_model.py`

**Instance Attributes:**
```python
self.client = client  # AsyncOpenAI
self.mood_state = {
    "happy": 0.0,
    "angry": 0.0,
    "irritated": 0.0,
    "sad": 0.0,
    "flirty": 0.0
}
```

---

#### `EmotionModel.extract_deltas(message: str, req_id: str) -> dict`

**Purpose:** Uses LLM to determine how a message affects mood.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `message` | `str` | User's message |
| `req_id` | `str` | Request ID for logging |

**Returns:** `dict` — Mood deltas like `{"happy": 1, "angry": 0, ...}`

**Side Effects:**
- Makes OpenAI API call
- Logs extracted deltas

**Error Handling:**
- Tries JSON parsing
- Falls back to regex extraction
- Worst case: returns zero deltas

---

#### `EmotionModel.update_mood(deltas: dict) -> None`

**Purpose:** Applies deltas to mood state.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `deltas` | `dict` | Mood changes from `extract_deltas()` |

**Returns:** `None`

**Side Effects:** Modifies `self.mood_state`, clamps to [-10, 10]

---

#### `EmotionModel.decay_mood(factor: float = 0.95) -> None`

**Purpose:** Gradually reduces mood intensity over time.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `factor` | `float` | `0.95` | Multiplicative decay factor |

**Returns:** `None`

**Side Effects:** Modifies `self.mood_state`

---

#### `EmotionModel.get_active_mood() -> str`

**Purpose:** Returns the dominant mood.

**Returns:** `str` — Mood name with highest value

**Side Effects:** None

---

#### `embed_text(text: str) -> np.ndarray`

**Purpose:** Creates embedding vector for text.

**File:** `regulators/context_model.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Text to embed |

**Returns:** `np.ndarray` — 1536-dimensional embedding vector

**Side Effects:** Makes OpenAI API call

---

#### `cosine(a: np.ndarray, b: np.ndarray) -> float`

**Purpose:** Computes cosine similarity between two vectors.

**File:** `regulators/context_model.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `a` | `np.ndarray` | First embedding vector |
| `b` | `np.ndarray` | Second embedding vector |

**Returns:** `float` — Cosine similarity in range [-1, 1]

**Side Effects:** None

---

#### `fetch_context(message: str, user_id: int, req_id: str, top_k=7, per_group=10, max_history=150) -> list`

**Purpose:** Retrieves relevant past messages for context.

**File:** `regulators/context_model.py`

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | Required | Query message |
| `user_id` | `int` | Required | User identifier |
| `req_id` | `str` | Required | Request ID |
| `top_k` | `int` | `7` | Max contexts to return |
| `per_group` | `int` | `10` | Top entries per pool |
| `max_history` | `int` | `150` | History size limit |

**Returns:** `list[str]` — List of relevant context strings

**Side Effects:**
- Makes embedding API call
- Adds message to global `history`
- May evict oldest entries
- Logs retrieved contexts

---

#### `add_to_history(message: str, role="assistant", user_id=None, max_history=150) -> None`

**Purpose:** Adds a message to semantic history.

**File:** `regulators/context_model.py`

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | Required | Message content |
| `role` | `str` | `"assistant"` | Message role |
| `user_id` | `int\|None` | `None` | User identifier |
| `max_history` | `int` | `150` | History size limit |

**Returns:** `None`

**Side Effects:**
- Makes embedding API call
- Modifies global `history` list

---

### 8.7 Prompt Builder Functions

#### `create_character_prompt(...) -> str`

**Purpose:** Builds the main persona system prompt.

**File:** `prompts/character_profile.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `user_name` | `str` | User's display name |
| `frndship_title` | `str` | Friendship level key |
| `mood` | `str` | Active mood from EmotionModel |
| `chat_context` | `list` | Retrieved semantic contexts |
| `chat_history` | `list` | Recent message history |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — Complete system prompt

**Side Effects:** Logs the generated prompt at DEBUG level

---

#### `create_command_decline_prompt(key: str, req_id: str) -> str`

**Purpose:** Builds command syntax correction prompt.

**File:** `prompts/command_decline.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `key` | `str` | Detected command key |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — Prompt for generating decline message

**Side Effects:** Logs the prompt at DEBUG level

**Internal Logic:**
- If key in COMMAND_MAP: instructs to correct syntax
- If key not in COMMAND_MAP: instructs to roast and redirect to /help

---

#### `lore_decline_prompt(question: str, req_id: str) -> str`

**Purpose:** Builds lore-based decline prompt for real-world questions.

**File:** `prompts/msg_decline.py`

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `question` | `str` | User's real-world question |
| `req_id` | `str` | Request ID for logging |

**Returns:** `str` — Prompt for generating in-character refusal

**Side Effects:** Logs the prompt at DEBUG level

---

### 8.8 Logging

#### `logger`

**Purpose:** Centralized logger for all modules.

**File:** `logger.py`

**Configuration:**
```python
logger = logging.getLogger("ConversationModel")
logger.setLevel(logging.DEBUG)

# Console handler: DEBUG level, shows all logs
# File handler: INFO level, writes to conversation.log
```

**Usage:**
```python
from logger import logger

logger.debug("Detailed debug info")
logger.info("Informational message")
logger.error("Error message", exc_info=True)
```

---

### 8.9 Client Singleton

#### `client`

**Purpose:** Shared AsyncOpenAI client instance.

**File:** `state/client.py`

**Configuration:**
```python
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Usage:**
```python
from state.client import client

response = await client.chat.completions.create(...)
embedding = await client.embeddings.create(...)
```

---

## 9. Error Handling

### Common Errors and Solutions

#### 1. Missing Model Files

**Error:**
```
OSError: Can't load tokenizer for './intent_model'. Make sure that:
- './intent_model' is a correct model identifier
```

**Origin:** `classifiers/intent_classifier.py` or `classifiers/command_classifier.py`

**Cause:** Models have not been trained yet.

**Solution:**
```bash
python classifiers/train_intent.py
python classifiers/train_command.py
```

---

#### 2. Missing Environment Variables

**Error:**
```
openai.AuthenticationError: No API key provided
```

**Origin:** `state/client.py`

**Cause:** `OPENAI_API_KEY` not set in `.env` file.

**Solution:**
1. Create `.env` file in project root
2. Add: `OPENAI_API_KEY=sk-your-key-here`

---

#### 3. API Key Authentication Failure

**Error:**
```json
{"detail": "Unauthorized"}
```

**Origin:** `main.py`, line 39

**Cause:** Request missing `api_key` header or wrong value.

**Solution:**
1. Ensure `CONVO_MODEL_API_KEY` is set in `.env`
2. Include header: `api_key: your-secret-key`

---

#### 4. Invalid Friendship Title

**Error:**
```
KeyError: 'InvalidTitle'
```

**Origin:** `prompts/character_profile.py`, line 40

**Cause:** `frndship_title` not in `FRNDSHIP_MAP`.

**Solution:** Use one of these valid titles:
- `"Stranger"`
- `"Acquaintance"`
- `"Casual"`
- `"Friend"`
- `"Close Friend"`
- `"Bestie"`
- `"Veyra's favourite 💖"`

---

#### 5. LLM Generation Failure

**Error:** Function returns fallback message like:
```
"ugh—my brain lagged, say that again?"
```

**Origin:** `generator/msg_generator.py`, line 50

**Cause:** OpenAI API call failed (rate limit, network error, etc.)

**Solution:**
1. Check OpenAI API status
2. Verify API key has sufficient credits
3. Check network connectivity
4. Review logs for detailed error

---

#### 6. JSON Parsing Error in Mood Extraction

**Error:** Falls back to zero deltas (no visible error)

**Origin:** `regulators/emotion_model.py`, lines 64-80

**Cause:** LLM returned malformed JSON.

**Internal Handling:**
1. Tries standard `json.loads()`
2. Falls back to regex extraction
3. Worst case: returns `{"happy": 0, ...}` (neutral deltas)

**Solution:** This is handled automatically; no action needed.

---

#### 7. Missing Training Data

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/intent.jsonl'
```

**Origin:** `classifiers/train_intent.py` or `train_command.py`

**Cause:** Training data files not created.

**Solution:**
```bash
mkdir data

# Create data/intent.jsonl with format:
# {"text": "hello", "label": "chitchat"}

# Create data/commands.jsonl with format:
# {"text": "buy sword", "label": "other_command"}
```

---

#### 8. Low Confidence Classification

**Behavior:** Returns "chitchat" even for non-chitchat messages.

**Origin:** `classifiers/intent_classifier.py`, lines 47-49

**Cause:** Model confidence below 0.35 threshold.

**Solution:**
1. Add more training data for the misclassified intent
2. Retrain the model
3. Optionally lower the threshold (not recommended)

---

#### 9. Context Memory Full

**Behavior:** Oldest messages silently removed.

**Origin:** `regulators/context_model.py`, lines 77-78

**Cause:** History exceeds 150 entries.

**Solution:** This is expected FIFO behavior. Increase `max_history` if needed:
```python
# In fetch_context() call
context = await fetch_context(msg, uid, req_id, max_history=300)
```

---

#### 10. Embedding Dimension Mismatch

**Error:**
```
ValueError: shapes not aligned
```

**Origin:** `regulators/context_model.py`, `cosine()` function

**Cause:** Embeddings from different models have different dimensions.

**Solution:** Clear history and ensure consistent embedding model:
```python
# In context_model.py
history = []  # Reset to clear old embeddings
```

---

## Appendix: Quick Reference

### File → Primary Purpose Map

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server, `/chat` endpoint |
| `logger.py` | Logging configuration |
| `core/router.py` | Intent/command routing |
| `engine/msg_gen_engine.py` | Response orchestration |
| `generator/msg_generator.py` | Chitchat generation |
| `generator/msgdecline_generator.py` | Lore decline generation |
| `generator/commanddecline_generator.py` | Command decline generation |
| `classifiers/intent_classifier.py` | Intent classification |
| `classifiers/command_classifier.py` | Command classification |
| `classifiers/train_intent.py` | Intent model training |
| `classifiers/train_command.py` | Command model training |
| `regulators/emotion_model.py` | Mood state management |
| `regulators/context_model.py` | Semantic memory |
| `prompts/character_profile.py` | Main persona prompt |
| `prompts/command_decline.py` | Command decline prompt |
| `prompts/msg_decline.py` | Lore decline prompt |
| `state/client.py` | OpenAI client singleton |

### Environment Variables Summary

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `CONVO_MODEL_API_KEY` | Server API authentication |
| `TOKENIZERS_PARALLELISM` | Set to `"false"` to suppress warnings |

### Model Paths

| Model | Path | Training Script |
|-------|------|-----------------|
| Intent | `./intent_model/` | `classifiers/train_intent.py` |
| Command | `./command_model/` | `classifiers/train_command.py` |

---

*End of Documentation*
