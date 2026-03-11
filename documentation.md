# Project Documentation — Conversation Model: Modular Agentic Dialogue Engine

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Core Systems](#core-systems)
5. [Modules / Packages](#modules--packages)
6. [Data Models](#data-models)
7. [APIs / Commands / Interfaces](#apis--commands--interfaces)
8. [System Interactions](#system-interactions)
9. [Internal Workflows](#internal-workflows)
10. [Developer Reference](#developer-reference)
11. [Design Decisions](#design-decisions)
12. [Future Improvements](#future-improvements)

---

## Overview

The **Conversation Model** is a modular, production-grade agentic dialogue engine designed to power personality-driven AI characters. Its primary application is **Veyra** — a sassy, dominant supernatural being from the fictional magical realm of **Natlade** — deployed as a Discord bot companion. However, the engine is intentionally constructed to be plug-and-play, meaning any persona or character can be swapped in by replacing the prompt layer and training data.

Unlike a naive chatbot that simply forwards user text to a language model, this system does **not** generate responses blindly. Instead, it applies a disciplined multi-stage cognitive pipeline before any text is produced:

1. **Intent Classification** — Determine whether the user is chatting, issuing a game command, or asking a real-world (out-of-lore) question.
2. **Command Classification** — If the message is a command, pinpoint exactly which one was intended.
3. **Mood Engine Update** — Extract the emotional impact of the user's message and update the character's running emotional state.
4. **Semantic Context Retrieval** — Find the most relevant past dialogue turns using vector similarity, surfacing memories that make replies feel personal and continuous.
5. **Persona Prompt Construction** — Assemble a rich system prompt that encodes the character's identity, current mood, friendship tier with the user, relevant memories, and conversation history.
6. **LLM Response Generation** — Call a large language model with the fully composed prompt to produce an in-character reply.
7. **Specialised Decline Handling** — When the user asks something outside the character's reality (real-world facts) or issues a command syntactically incorrectly, a dedicated decline generator produces a brief, persona-consistent rejection instead.

The result is a system that **routes, reasons, remembers, and reacts** before producing any output — generating replies that feel genuinely built on history, mood, and relationship context rather than stateless one-shot generation.

### Goals

- Deliver immersive, non-repetitive, in-character conversational responses.
- Maintain dynamic emotional states that evolve across a conversation.
- Route user input to specialised handlers instead of forwarding everything to a single LLM call.
- Keep all persona logic in explicitly editable prompt files, making the character fully customisable without touching engine code.
- Provide a clean REST interface so any client (Discord bot, web front-end, mobile app) can consume it over HTTP.

### Main Capabilities

| Capability | Description |
|---|---|
| Intent Classification | DistilBERT classifier distinguishes chitchat, commands, and out-of-lore queries |
| Command Classification | Secondary DistilBERT classifier identifies 9 specific command intents |
| Mood Engine | LLM-backed delta extraction drives a persistent 5-axis emotional state |
| Semantic Memory | Per-user and global embedding pools with cosine-similarity retrieval |
| Persona Prompt Composer | Injects mood, friendship tier, history, and context into every system prompt |
| Lore-Aware Decline | In-character refusals for real-world questions, keeping the fiction intact |
| Command Correction | Persona-consistent roast messages directing users to correct command syntax |
| REST API | FastAPI endpoint with API-key authentication, ready for production deployment |

---

## Architecture

### Overview Diagram

```
                         ┌─────────────────────────────────────────────┐
                         │               FastAPI  (main.py)             │
                         │   POST /chat  ←  { text, user_id, … }        │
                         └──────────────────────┬──────────────────────┘
                                                │
                                                ▼
                         ┌─────────────────────────────────────────────┐
                         │              Engine (msg_gen_engine.py)       │
                         │  Orchestrates all subsystems, returns reply   │
                         └──┬──────────────────┬──────────────────┬────┘
                            │                  │                  │
                    route_type="intent"  route_type="command"  (error)
                            │                  │
              ┌─────────────┴──┐      ┌────────┴──────────────┐
              │                │      │                        │
         label=              label=  label ≠ LABEL_8      label = LABEL_8
        "chitchat"           "study"  (known command)     (unknown cmd)
              │                │           │                   │
              ▼                ▼           ▼                   ▼
       ChatGenerator   MsgDecline   return label str    CmdDecline
                       Generator                        Generator
              │
    ┌─────────┴──────────────────────┐
    │                                │
    ▼                                ▼
EmotionModel                  context_model
(extract deltas,              (fetch_context via
 update mood,                  embeddings + cosine
 get_active_mood)              similarity)
    │                                │
    └──────────┬─────────────────────┘
               ▼
    character_profile.py
    (build full system prompt)
               │
               ▼
    AsyncOpenAI (gpt-5-chat-latest)
               │
               ▼
    add_to_history() → in-memory embedding store
               │
               ▼
           reply string
```

### Major Modules

| Module | Role |
|---|---|
| `main.py` | FastAPI application, HTTP API entry-point, request/response lifecycle |
| `engine/msg_gen_engine.py` | Central orchestrator — owns router + generator instances, drives the pipeline |
| `core/router.py` | Two-stage classification: intent → (optionally) command |
| `classifiers/intent_classifier.py` | DistilBERT wrapper for 3-class intent prediction |
| `classifiers/command_classifier.py` | DistilBERT wrapper for 9-class command prediction |
| `generator/msg_generator.py` | Full-path chitchat generation with mood + memory |
| `generator/commanddecline_generator.py` | LLM-based command correction messages |
| `generator/msgdecline_generator.py` | LLM-based lore-refusal messages |
| `regulators/emotion_model.py` | 5-axis emotional state, delta extraction, mood clamping and decay |
| `regulators/context_model.py` | In-memory semantic store — embedding, retrieval, history management |
| `prompts/character_profile.py` | Main system-prompt builder, encodes all persona rules |
| `prompts/command_decline.py` | Command-correction prompt builder with a COMMAND_MAP lookup |
| `prompts/msg_decline.py` | Lore-refusal prompt builder |
| `state/client.py` | Singleton `AsyncOpenAI` client shared across all generators |
| `logger.py` | Dual-output (console + file) structured logger |
| `classifiers/train_intent.py` | Training script — intent DistilBERT fine-tune |
| `classifiers/train_command.py` | Training script — command DistilBERT fine-tune |
| `data/intent.jsonl` | Labelled training data for intent classifier |
| `data/commands.jsonl` | Labelled training data for command classifier |

### Dependency Relationships

```
main.py
  └── engine/msg_gen_engine.py
        ├── core/router.py
        │     ├── classifiers/intent_classifier.py  ←  intent_model/
        │     └── classifiers/command_classifier.py ←  command_model/
        ├── generator/msg_generator.py
        │     ├── regulators/emotion_model.py  ←  state/client.py
        │     ├── regulators/context_model.py  ←  state/client.py
        │     └── prompts/character_profile.py
        ├── generator/commanddecline_generator.py
        │     └── prompts/command_decline.py
        └── generator/msgdecline_generator.py
              └── prompts/msg_decline.py

state/client.py  ←  .env (OPENAI_API_KEY)
logger.py        →  conversation.log
```

### Design Patterns

- **Strategy Pattern** — The three generators (`ChatGenerator`, `CommandDeclineGenerator`, `MsgDeclineGenerator`) are interchangeable responders. The `Engine` selects which one to call based on routing outcome.
- **Singleton** — `intent_clf`, `cmd_clf` (router), `veyra` (engine), and `client` (state) are instantiated once at module load time and reused across all requests, avoiding expensive repeated model loading.
- **Pipeline / Chain of Responsibility** — Each request passes through sequentially: classify intent → optionally classify command → update mood → retrieve context → build prompt → generate reply → store to history.
- **Prompt as Configuration** — All persona behaviour lives in `prompts/`, separating character logic from engine mechanics. Swapping a character requires editing prompt files only.
- **In-Memory Vector Store** — Context memory uses a plain Python list of dicts with NumPy embedding vectors rather than a vector database, keeping the stack minimal while providing semantic retrieval.

---

## Getting Started

### Prerequisites

- Python 3.10 or later
- An OpenAI API key
- (Optional) A CUDA-capable GPU for faster model training; CPU/MPS inference works fine

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd "conversation model"

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# or
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
# Also install FastAPI runtime dependencies (not in requirements.txt):
pip install fastapi uvicorn python-dotenv openai numpy
```

> **Note:** `requirements.txt` covers the training-time dependencies (transformers, datasets, torch, tqdm, accelerate). Runtime dependencies (fastapi, uvicorn, openai, python-dotenv, numpy) were developed across multiple machines and are not fully listed. Install them manually if any import fails.

### Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
CONVO_MODEL_API_KEY=your-secret-api-key-here
```

- `OPENAI_API_KEY` — used by `state/client.py` to authenticate all OpenAI calls (embeddings, mood extraction, chat generation).
- `CONVO_MODEL_API_KEY` — used by `main.py` to authenticate inbound requests to `POST /chat`. Clients must send this as the `api-key` header.

### Training the Classifiers

The two DistilBERT models must be trained before the server can run. Pre-trained model weights are gitignored and not committed.

```bash
# Train the intent classifier (3 classes: command / study / chitchat)
python classifiers/train_intent.py

# Train the command classifier (9 classes: check_wallet, check_exp, etc.)
python classifiers/train_command.py
```

Training artefacts are written to `intent_model/` and `command_model/` respectively, including the final model weights (`model.safetensors`), tokenizer files, and `config.json`.

**Training configuration:**

| Setting | Intent Model | Command Model |
|---|---|---|
| Base model | `distilbert-base-uncased` | `distilbert-base-uncased` |
| Labels | 3 | 9 |
| Epochs | 5 | 5 |
| Batch size | 8 | 8 |
| Learning rate | 4e-5 | 4e-5 |
| Output dir | `./intent_model` | `./command_model` |

### Running the Server

```bash
python main.py
# Server starts at http://127.0.0.1:8000
```

Or via uvicorn directly:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Quick Programmatic Usage

```python
import asyncio
from engine.msg_gen_engine import Engine

engine = Engine()

reply = asyncio.run(engine.respond(
    message="yo hello?",
    frndship_title="Friend",
    user_id=123,
    user_name="Sylver",
    chat_history=[],
    req_id="test01"
))
print(reply)
```

---

## Core Systems

### 1. Intent Classification System

**Purpose:** The first gate that every user message passes through. Its job is to assign a high-level intent category so the engine knows which pipeline branch to activate.

**Components:**
- `classifiers/intent_classifier.py` — inference wrapper
- `classifiers/train_intent.py` — fine-tuning script
- `data/intent.jsonl` — labelled training corpus
- `intent_model/` — fine-tuned model artefacts

**Internal Logic:**

The `IntentClassifier` loads `distilbert-base-uncased` fine-tuned on `data/intent.jsonl`. On each call to `predict(text)`, it:

1. Normalises the input by stripping whitespace and lower-casing.
2. Tokenises the text (truncation + padding to model max).
3. Runs a forward pass through the seq-classification head.
4. Applies `softmax` over the 3-class logit vector to obtain probabilities.
5. Takes `argmax` to find the predicted class; but crucially, if the top probability is **below 0.35**, the model falls back to returning `"chitchat"` regardless of the argmax. This threshold prevents the classifier from confidently assigning `"command"` or `"study"` to ambiguous messages.

**Labels:**

| ID | Label | Meaning |
|---|---|---|
| 0 | `command` | User is trying to trigger a game/bot command |
| 1 | `study` | User is asking a real-world / factual question |
| 2 | `chitchat` | General conversation, banter, small talk |

**Interaction with other systems:** The result is passed to `core/router.py` which decides whether to also run the command classifier.

---

### 2. Command Classification System

**Purpose:** A secondary narrower classifier that fires only when the intent classifier returns `"command"`. It identifies which specific command the user intended from a 9-class vocabulary.

**Components:**
- `classifiers/command_classifier.py` — inference wrapper
- `classifiers/train_command.py` — fine-tuning script
- `data/commands.jsonl` — labelled training corpus
- `command_model/` — fine-tuned model artefacts

**Internal Logic:**

The `CommandClassifier` loads `distilbert-base-uncased` fine-tuned on `data/commands.jsonl`. Unlike the intent classifier, it does **not** apply a confidence threshold — it always returns the `argmax` label from the model's `id2label` config mapping.

**Labels:**

| ID | Label | Meaning |
|---|---|---|
| 0 | `check_wallet` | Show the user's gold/currency balance |
| 1 | `check_exp` | Show the user's experience points / level |
| 2 | `check_energy` | Show the user's stamina/energy stat |
| 3 | `check_inventory` | Show the user's item inventory |
| 4 | `quest` | Open the quest panel |
| 5 | `shop` | Open the shop |
| 6 | `start_race` | Initiate a race event |
| 7 | `flip_coin` | Run a coin-flip game |
| 8 | `other_command` | Anything not in the above 8 classes |

**`LABEL_8` routing:** When the command classifier returns `LABEL_8` (other_command), the engine routes to `CommandDeclineGenerator`, which produces a sassy message telling the user to use the correct syntax. For labels 0–7, the raw label string is returned directly to the caller — the expectation is that downstream bot code (not this engine) handles the actual command execution.

---

### 3. Routing System

**Purpose:** Acts as the central traffic controller, holding references to both classifiers and exposing a single `main_router()` function that the engine calls.

**Components:**
- `core/router.py`

**Internal Logic:**

```
main_router(message) →
  intent = classify_intent(message)  # always runs
  if intent == "command":
    cmd = classify_command(message)
    return ("command", cmd)
  else:
    return ("intent", intent)
```

Both classifiers are instantiated once as module-level singletons:

```python
intent_clf = IntentClassifier()
cmd_clf = CommandClassifier()
```

This ensures models are loaded into memory only once when the module is first imported, not on every HTTP request.

---

### 4. Emotion / Mood System

**Purpose:** Gives the character a dynamic, evolving emotional state that directly influences tone, word choice, and patience level in responses.

**Components:**
- `regulators/emotion_model.py` — `EmotionModel` class

**Internal Logic:**

The `EmotionModel` maintains a **5-axis mood state** as a dictionary of floats:

```python
mood_state = {
    "happy":     0.0,
    "angry":     0.0,
    "irritated": 0.0,
    "sad":       0.0,
    "flirty":    0.0
}
```

On each chitchat-routed message, the engine calls `extract_deltas(message)`, which sends the raw user message to `gpt-5-mini` with a structured prompt asking for a JSON dictionary of integer/float deltas for each axis. The response format is enforced via `response_format={"type": "json_object"}`.

After extraction, `update_mood(deltas)` applies each delta to the corresponding axis and **clamps all values to the range [-10, 10]** — preventing any single mood from dominating infinitely.

`get_active_mood()` simply returns the key with the highest current value, giving the `ChatGenerator` a single dominant mood label to inject into the persona prompt.

The `decay_mood(factor=0.95)` method provides a mechanism to slowly reduce emotional intensity over time (multiplying each axis by 0.95 per call), although this is not currently wired into the request cycle — it is available for developers to call on a schedule or between sessions.

**Key properties:**

| Method | Description |
|---|---|
| `extract_deltas(message, req_id)` | Async — calls `gpt-5-mini` to get JSON mood deltas |
| `update_mood(deltas)` | Applies deltas, clamps to [-10, 10] |
| `decay_mood(factor=0.95)` | Reduces all mood values toward 0 |
| `get_active_mood()` | Returns the dominant mood name |

**Error handling:** If the LLM response is not valid JSON, the code uses a regex fallback to extract a JSON object. If that also fails, it falls back to zero-deltas, ensuring the pipeline never crashes due to a malformed emotion response.

---

### 5. Semantic Context / Memory System

**Purpose:** Replaces a naive "send last N messages" approach with a vector-similarity-based retrieval system that surfaces the most semantically relevant past messages for constructing the response.

**Components:**
- `regulators/context_model.py` — `fetch_context()`, `add_to_history()`, `embed_text()`, `cosine()`

**Internal Logic:**

All messages (user and assistant) are stored in a module-level Python list called `history`. Each entry is a dictionary:

```python
{
    "content":   str,        # the message text
    "embedding": np.array,   # 1536-d float vector from text-embedding-3-small
    "role":      str,        # "user" or "assistant"
    "user_id":   int | None  # for user messages; None for assistant messages
}
```

**Retrieval algorithm (`fetch_context`):**

1. Embed the incoming query message using `text-embedding-3-small`.
2. Split the history into a **personal pool** (entries from the same `user_id`) and a **global pool** (all other entries).
3. Score each entry in both pools via cosine similarity against the query embedding.
4. Apply a **+0.05 personal bonus** to personal pool scores to weight the user's own history slightly higher.
5. Take the top `per_group=10` results from each pool.
6. Merge and re-rank the 20 candidates by score.
7. Filter to entries with similarity ≥ 0.35 (configurable `threshold`).
8. Return the top `top_k=7` content strings.

After retrieval, the query message is appended to `history` as a new entry (if it is longer than 3 characters). History is capped at `max_history=150` entries; the oldest entry is evicted when the cap is exceeded (FIFO).

**Memory is in-process.** There is no database or persistent store. History is lost when the server restarts.

---

### 6. Persona Prompt System

**Purpose:** Assembles the full system prompt that encodes who the character is, how she should behave, and what she knows before generating any reply.

**Components:**
- `prompts/character_profile.py` — `create_character_prompt()`
- `prompts/command_decline.py` — `create_command_decline_prompt()`
- `prompts/msg_decline.py` — `lore_decline_prompt()`

**`create_character_prompt` logic:**

Takes `user_name`, `frndship_title`, `mood`, `chat_context` (list of relevant memories), `chat_history` (recent turns), and `req_id`. Builds a multi-section string:

| Section | Content |
|---|---|
| Identity | Veyra's persona — magical woman from Natlade, not an AI |
| Social Dynamics | Current mood label; friendship title and its behavioural descriptor from `FRNDSHIP_MAP` |
| Lore Rules | Never break character or reference real-world knowledge |
| Context + Memory | Injected `chat_history` and retrieved `chat_context` |
| Memory Safety | Instructions on how to use context without inventing false memories |
| Hard Character Rules | Tone consistency, dominance, emotional reactivity |
| Style Rules | Short replies (1–2 sentences), human-chat style, avoid repetitive action tags |

**Friendship tiers (`FRNDSHIP_MAP`):**

| Title | Behavioural Descriptor |
|---|---|
| Stranger | Cold, distant, dismissive, teasing with suspicion |
| Acquaintance | Slightly polite but still mocking and uninterested |
| Casual | Light teasing, playful sarcasm, mild smugness |
| Friend | Supportive sass, playful banter, soft approval |
| Close Friend | Warm teasing, insider jokes, occasional praise |
| Bestie | Affectionate bullying, chaotic energy, admiration mixed with dominance |
| Veyra's favourite 💖 | Overprotective, dominant flirty energy, high praise and possessive affection |

---

### 7. Response Generation System

**Purpose:** Three generators handle the three possible output paths, each making async OpenAI API calls with tailored prompts.

#### `ChatGenerator` (`generator/msg_generator.py`)

The main generator, used for all `chitchat`-routed messages. It:

1. Calls `EmotionModel.extract_deltas()` and `update_mood()` to refresh the mood state.
2. Calls `fetch_context()` to retrieve relevant memories.
3. Calls `create_character_prompt()` to build the full system prompt.
4. Sends a `chat.completions.create` call to `gpt-5-chat-latest` with:
   - The system prompt.
   - The user's raw message as the user turn.
   - `max_tokens=60` (short replies).
   - `temperature=0.9`, `top_p=0.95` (creative but bounded).
   - `frequency_penalty=0.2`, `presence_penalty=0.1` (discourage repetition).
5. Calls `add_to_history()` to store the assistant reply with its embedding.
6. Returns the reply text; on any exception, returns a safe fallback string.

#### `CommandDeclineGenerator` (`generator/commanddecline_generator.py`)

Fires when the command classifier returns `LABEL_8` (unrecognised or multi-argument command). It:

1. Calls `create_command_decline_prompt(command, req_id)` which looks up the command keyword in `COMMAND_MAP`. If found, it instructs the LLM to tell the user the correct syntax. If not found, it instructs the LLM to roast the user for inventing a fake command.
2. Sends to `gpt-5-mini` (cheaper, faster — this is a short utility message).
3. Returns a sassy one-liner; falls back to a static string on exception.

#### `MsgDeclineGenerator` (`generator/msgdecline_generator.py`)

Fires when the intent is `"study"` (real-world question). It:

1. Calls `lore_decline_prompt(msg, req_id)` which builds a prompt instructing Veyra to act confused and in-lore, rejecting the question as if the topic doesn't exist in Natlade.
2. Sends to `gpt-5-mini`.
3. Returns a short snarky refusal; falls back to a static string on exception.

---

## Modules / Packages

### `main.py`

**Location:** `/main.py`  
**Responsibility:** FastAPI application entry point. Defines the HTTP API, handles authentication, request lifecycle logging, and delegates to the `Engine`.

**Key elements:**

```python
class Message(BaseModel):
    text: str
    frndship_title: str
    user_id: int
    user_name: str
    message_history: list
```

The `Message` Pydantic model validates and deserialises all incoming request bodies. Only these 5 fields are accepted.

**`POST /chat` endpoint:**

- Reads `api-key` from the `Header` and compares it against `CONVO_MODEL_API_KEY` from the environment. Returns `403 Unauthorized` on mismatch.
- Generates a 6-character hex `req_id` via `uuid.uuid4().hex[:6]` for log correlation.
- Awaits `engine.respond(...)`.
- On exception, logs the traceback and returns a safe fallback reply (`"Veyra blacked out mid-thought 💀"`).
- Logs request + reply with timing (in milliseconds).

---

### `logger.py`

**Location:** `/logger.py`  
**Responsibility:** Project-wide logging configuration. Provides a single `logger` instance imported by every module.

**Behaviour:**
- Console handler at `DEBUG` level — shows all log messages during development.
- File handler at `INFO` level — writes persistent logs to `conversation.log` (UTF-8 encoded).
- Log format: `[HH:MM:SS] [LEVEL] ConversationModel: message`.
- Guards against duplicate handler registration (`if not logger.handlers`).

---

### `engine/msg_gen_engine.py`

**Location:** `/engine/msg_gen_engine.py`  
**Responsibility:** Central orchestrator. Composes all subsystems and implements the top-level routing decision tree.

**`Engine` class:**

Initialises three generators in `__init__`:
```python
self.chat     = ChatGenerator()
self.cmd_dlcn = CommandDeclineGenerator()
self.msg_dlcn = MsgDeclineGenerator()
```

`respond(message, user_id, user_name, frndship_title, chat_history, req_id)` implements the branching logic:

```
route_type, label = main_router(message, req_id)

if route_type == "intent":
    if label == "chitchat"  → ChatGenerator.generate()
    else (label == "study") → MsgDeclineGenerator.generate()

if route_type == "command":
    if label != "LABEL_8"   → return label string directly
    else (LABEL_8)          → CommandDeclineGenerator.generate()
```

---

### `core/router.py`

**Location:** `/core/router.py`  
**Responsibility:** Instantiates classifiers (once) and exposes `main_router()`.

**Functions:**

| Function | Signature | Returns |
|---|---|---|
| `main_router` | `(message: str, req_id: str)` | `tuple[str, str]` — `(route_type, label)` |
| `classify_intent` | `(message: str)` | `str` — one of `["command", "study", "chitchat"]` |
| `classify_command` | `(message: str)` | `str` — one of 9 command labels or `LABEL_8` |

---

### `classifiers/intent_classifier.py`

**Location:** `/classifiers/intent_classifier.py`  
**Responsibility:** Inference wrapper for the 3-class intent DistilBERT model.

**`IntentClassifier` class:**

| Attribute / Method | Description |
|---|---|
| `LABELS` | `["command", "study", "chitchat"]` — index i maps to model output i |
| `__init__` | Loads tokenizer + model from `./intent_model`; calls `model.eval()` |
| `predict(text)` | Tokenises, runs forward pass, softmax, threshold check, returns label |

**Confidence threshold:** `< 0.35` → fall back to `"chitchat"`. Prevents misclassification of ambiguous requests as `"study"` or `"command"`.

---

### `classifiers/command_classifier.py`

**Location:** `/classifiers/command_classifier.py`  
**Responsibility:** Inference wrapper for the 9-class command DistilBERT model.

**`CommandClassifier` class:**

| Attribute / Method | Description |
|---|---|
| `id2label` | Loaded directly from `model.config.id2label` — no hardcoded mapping in code |
| `__init__` | Loads tokenizer + model from `./command_model`; calls `model.eval()` |
| `predict(text)` | Tokenises, runs forward pass, `argmax` (no threshold), returns label string |

---

### `classifiers/train_intent.py`

**Location:** `/classifiers/train_intent.py`  
**Responsibility:** One-shot training script for the intent classifier.

**Sequence:**
1. Load `data/intent.jsonl` via HuggingFace Datasets.
2. Map string labels → integer IDs via a hard-coded `labels` dict.
3. Tokenise with `distilbert-base-uncased` tokenizer (max-length padding).
4. Load `distilbert-base-uncased` with a 3-class classification head.
5. Configure and run `Trainer` for 5 epochs, batch size 8, lr=4e-5.
6. Save model + tokenizer to `./intent_model`.

---

### `classifiers/train_command.py`

**Location:** `/classifiers/train_command.py`  
**Responsibility:** One-shot training script for the command classifier.

Same sequence as `train_intent.py` but loads `data/commands.jsonl`, uses 9 output labels, and saves to `./command_model`.

---

### `generator/msg_generator.py`

**Location:** `/generator/msg_generator.py`  
**Responsibility:** Main chitchat path generation — mood + memory → prompt → LLM → history.

The module-level `veyra = EmotionModel()` singleton persists emotional state across all requests. `ChatGenerator` instantiates a reference to the shared `client`.

**`generate(user_msg, user_id, user_name, frndship_title, chat_history, req_id)`:**

Async method, returns a `str`. On any exception from the OpenAI call, returns `"ugh—my brain lagged, say that again?"`.

---

### `generator/commanddecline_generator.py`

**Location:** `/generator/commanddecline_generator.py`  
**Responsibility:** Short-form decline messages for improperly invoked commands.

**`generate(command, req_id)`:** Async, calls `gpt-5-mini`. Falls back to static string on exception.

---

### `generator/msgdecline_generator.py`

**Location:** `/generator/msgdecline_generator.py`  
**Responsibility:** In-lore refusal messages for real-world / out-of-character questions.

**`generate(msg, req_id)`:** Async, calls `gpt-5-mini`. Falls back to static string on exception.

---

### `regulators/emotion_model.py`

**Location:** `/regulators/emotion_model.py`  
**Responsibility:** 5-axis emotional state model with LLM-driven delta extraction.

See [Emotion / Mood System](#4-emotion--mood-system) for full detail.

---

### `regulators/context_model.py`

**Location:** `/regulators/context_model.py`  
**Responsibility:** In-memory semantic vector store with per-user and global retrieval.

See [Semantic Context / Memory System](#5-semantic-context--memory-system) for full detail.

---

### `prompts/character_profile.py`

**Location:** `/prompts/character_profile.py`  
**Responsibility:** Builds the main system prompt for Veyra, injecting all dynamic state.

**Key constant:** `FRNDSHIP_MAP` — a `dict[str, str]` mapping 7 friendship tier names to their behavioural descriptor strings.

---

### `prompts/command_decline.py`

**Location:** `/prompts/command_decline.py`  
**Responsibility:** Builds decline prompts for command correction.

**Key constant:** `COMMAND_MAP` — a `dict[str, str]` mapping 26 command keys to their correct bot-command syntax strings (e.g. `"buy"` → `"!buy — Purchase items from the shop"`). When a command key is missing from the map, the prompt instructs Veyra to roast the user for inventing fake syntax.

---

### `prompts/msg_decline.py`

**Location:** `/prompts/msg_decline.py`  
**Responsibility:** Builds lore-refusal prompts for real-world questions.

**`lore_decline_prompt(question, req_id)`:** Wraps the user's question in a persona prompt instructing Veyra to act confused and dismissive, pretending the topic doesn't exist in Natlade.

---

### `state/client.py`

**Location:** `/state/client.py`  
**Responsibility:** Provides the shared `AsyncOpenAI` client instance.

```python
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

This is a module-level singleton imported by all generators and the emotion/context models. Using a single shared async client is correct for asyncio — the `httpx.AsyncClient` pool it wraps handles concurrent requests efficiently.

---

## Data Models

### HTTP Request — `Message`

Defined in `main.py` as a Pydantic `BaseModel`:

| Field | Type | Description |
|---|---|---|
| `text` | `str` | The user's raw message text |
| `frndship_title` | `str` | The current friendship tier (must match a key in `FRNDSHIP_MAP`) |
| `user_id` | `int` | Unique numeric identifier for the user |
| `user_name` | `str` | Display name of the user (injected into the persona prompt) |
| `message_history` | `list` | Recent conversation turns (passed directly to the persona prompt) |

### Mood State

Internal to `EmotionModel`, not exposed via API:

| Field | Type | Range | Meaning |
|---|---|---|---|
| `happy` | `float` | [-10, 10] | Positivity, joy, warmth |
| `angry` | `float` | [-10, 10] | Anger, outrage |
| `irritated` | `float` | [-10, 10] | Low-level frustration |
| `sad` | `float` | [-10, 10] | Melancholy, despondency |
| `flirty` | `float` | [-10, 10] | Playful romantic energy |

### Context History Entry

Module-level list in `context_model.py`:

| Field | Type | Description |
|---|---|---|
| `content` | `str` | The message text (normalised to lowercase) |
| `embedding` | `np.ndarray` | 1536-d float vector (text-embedding-3-small) |
| `role` | `str` | `"user"` or `"assistant"` |
| `user_id` | `int \| None` | Originating user ID; `None` for assistant messages |

### Intent Labels

| Integer | String |
|---|---|
| 0 | `command` |
| 1 | `study` |
| 2 | `chitchat` |

### Command Labels

| Integer | String |
|---|---|
| 0 | `check_wallet` |
| 1 | `check_exp` |
| 2 | `check_energy` |
| 3 | `check_inventory` |
| 4 | `quest` |
| 5 | `shop` |
| 6 | `start_race` |
| 7 | `flip_coin` |
| 8 | `other_command` |

### Training Data Format (JSONL)

Both training datasets use the same format:

```jsonl
{"text": "show my wallet balance", "label": "check_wallet"}
{"text": "yo hello?", "label": "chitchat"}
```

Each line is a valid JSON object. The `text` field is the raw user utterance; `label` is the target class string.

---

## APIs / Commands / Interfaces

### REST API

#### `POST /chat`

The single HTTP endpoint exposed by the server.

**URL:** `http://127.0.0.1:8000/chat`  
**Method:** `POST`  
**Content-Type:** `application/json`

**Headers:**

| Header | Required | Description |
|---|---|---|
| `api-key` | Yes | Must match `CONVO_MODEL_API_KEY` environment variable |

**Request Body:**

```json
{
  "text": "hey what's up",
  "frndship_title": "Friend",
  "user_id": 42,
  "user_name": "Sylver",
  "message_history": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous reply"}
  ]
}
```

**Successful Response:**

HTTP `200 OK` — body is the raw reply string (not JSON-wrapped):

```
"oh hey, Sylver — thought you'd forgotten me or something 😒"
```

**Error Responses:**

| Status | Condition |
|---|---|
| `403 Forbidden` | `api-key` header missing or does not match `CONVO_MODEL_API_KEY` |
| `422 Unprocessable Entity` | Request body fails Pydantic validation |
| `200 OK` (fallback) | Any unhandled engine exception — returns `"Veyra blacked out mid-thought 💀"` |

---

### Command Map (26 defined commands)

The following command keys are mapped in `prompts/command_decline.py`. The engine returns the label string directly to the caller for labels 0–7; LABEL_8 triggers the decline flow.

| Command Key | Correct Syntax | Description |
|---|---|---|
| `buy` | `!buy` | Purchase items from the shop |
| `sell` | `!sell` | Sell items the shop accepts |
| `open` | `!open` | Open a lootbox |
| `bet` | `!bet` | Bet on an ongoing race |
| `play` | `!play` | Number-guessing game |
| `smelt` | `/smelt` | Smelt ores into bars |
| `upgrade` | `!upgrade` | Upgrade a building |
| `unlock` | `!unlock` | Unlock a building |
| `leaderboard` | `/leaderboard` | View top players |
| `info` | `!info` | Item information lookup |
| `ping` | `!ping` | Check bot latency |
| `solve_wordle` | `!solve_wordle` | Start Wordle solver session |
| `wordle_hint` | `/wordle_hint` | Get next Wordle hint |
| `help` | `/help` | Opens main help menu |
| `commandhelp` | `!commandhelp` | Detailed help for any command |
| `transfer_item` | `/transfer_item` | Transfer an item to a user |
| `transfer_gold` | `/transfer_gold` | Transfer gold to a user |
| `battle` | `/battle` | Challenge someone to a duel |
| `work` | `!work` | Do a job to earn gold |
| `load_marketplace` | `/load_marketplace` | View marketplace listings |
| `create_listing` | `/create_listing` | Create a marketplace listing |
| `buy_from_marketplace` | `/buy_from_marketplace` | Buy a marketplace listing |
| `delete_listing` | `/delete_listing` | Delete a listing |
| `use` | `!use` | Use a consumable item |
| `loadout` | `/loadout` | Edit equipment loadout |
| `introduction` | `/introduction` | Open intro form |

### CLI Commands

```bash
# Train intent classifier
python classifiers/train_intent.py

# Train command classifier
python classifiers/train_command.py

# Start server
python main.py
```

---

## System Interactions

### Module Dependency Graph

```
main.py
  │
  └─► Engine (msg_gen_engine.py)
        │
        ├─► main_router (router.py)
        │     ├─► IntentClassifier.predict()     [loads intent_model/]
        │     └─► CommandClassifier.predict()    [loads command_model/]
        │
        ├─► ChatGenerator.generate()
        │     ├─► EmotionModel.extract_deltas()  ──► AsyncOpenAI (gpt-5-mini)
        │     ├─► EmotionModel.update_mood()
        │     ├─► fetch_context()                ──► AsyncOpenAI (text-embedding-3-small)
        │     ├─► create_character_prompt()
        │     ├─► AsyncOpenAI (gpt-5-chat-latest)
        │     └─► add_to_history()               ──► AsyncOpenAI (text-embedding-3-small)
        │
        ├─► MsgDeclineGenerator.generate()
        │     ├─► lore_decline_prompt()
        │     └─► AsyncOpenAI (gpt-5-mini)
        │
        └─► CommandDeclineGenerator.generate()
              ├─► create_command_decline_prompt()
              └─► AsyncOpenAI (gpt-5-mini)
```

### Shared State

| Shared Object | Location | Who reads it | Who writes it |
|---|---|---|---|
| `history` list | `context_model.py` module global | `fetch_context()` | `fetch_context()`, `add_to_history()` |
| `mood_state` dict | `EmotionModel` instance in `msg_generator.py` module | `get_active_mood()` | `update_mood()` |
| `client` | `state/client.py` | All generators, emotion model, context model | Created once at import |
| `intent_clf` | `router.py` module | `classify_intent()` | Loaded once at import |
| `cmd_clf` | `router.py` module | `classify_command()` | Loaded once at import |

### OpenAI API Calls Per Request

For a chitchat-routed message, one request incurs **up to 3 OpenAI API calls**:

1. `gpt-5-mini` — mood delta extraction (`EmotionModel.extract_deltas`)
2. `text-embedding-3-small` — query embedding (`fetch_context`)
3. `gpt-5-chat-latest` — response generation (`ChatGenerator.generate`)
4. `text-embedding-3-small` — reply embedding (`add_to_history`)

For a study (lore decline) or known command label, only **1 API call** is made (decline generation or none). For `LABEL_8`, **1 API call** (command decline).

---

## Internal Workflows

### Workflow 1: Chitchat Message (Full Path)

```
1.  Client sends POST /chat { text: "lol ur such a vibe", user_id: 42, frndship_title: "Friend", ... }

2.  main.py validates API key, generates req_id="a1b2c3"

3.  Engine.respond() called

4.  main_router("lol ur such a vibe", "a1b2c3") →
      IntentClassifier.predict() → softmax → max_prob=0.71 > 0.35 → LABELS[2] = "chitchat"
      returns ("intent", "chitchat")

5.  Engine routes to ChatGenerator.generate()

6.  EmotionModel.extract_deltas("lol ur such a vibe") →
      gpt-5-mini called with emotion analysis prompt →
      returns {"happy": 1, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0.5}

7.  EmotionModel.update_mood(deltas) →
      mood_state["happy"] += 1 → 1.0
      mood_state["flirty"] += 0.5 → 0.5
      (clamped — no values hit ±10)

8.  EmotionModel.get_active_mood() → "happy"

9.  fetch_context("lol ur such a vibe", 42, "a1b2c3") →
      embed "lol ur such a vibe" via text-embedding-3-small → 1536-d vector
      score personal pool (user_id==42) + global pool
      filter threshold 0.35, return top 7 content strings
      append this message to history

10. create_character_prompt(
        user_name="Sylver", frndship_title="Friend",
        mood="happy", chat_context=[...], chat_history=[...], req_id="a1b2c3"
    ) → system_prompt string (~1200 tokens)

11. client.chat.completions.create(
        model="gpt-5-chat-latest",
        messages=[{role:system, content:system_prompt}, {role:user, content:"lol ur such a vibe"}],
        max_tokens=60, temperature=0.9 ...
    ) → "okay ur actually kind of funny sometimes, don't let it go to ur head though 🙄"

12. add_to_history("okay ur actually kind of funny...") →
      embed reply → append to history list

13. reply returned up call stack → main.py logs + returns to client
```

### Workflow 2: Game Command — Known Label

```
1.  POST /chat { text: "show me my wallet", ... }

2.  main_router("show me my wallet") →
      IntentClassifier → "command"
      CommandClassifier → LABEL_0 = "check_wallet"
      returns ("command", "check_wallet")

3.  Engine: route_type=="command", label!="LABEL_8" → return "check_wallet"

4.  main.py returns "check_wallet" string to client

    (The Discord bot then executes the wallet-check command using this label as a trigger.)
```

### Workflow 3: Game Command — Unknown / Multi-Argument (LABEL_8)

```
1.  POST /chat { text: "buy me 5 swords please", ... }

2.  main_router("buy me 5 swords please") →
      IntentClassifier → "command"
      CommandClassifier → LABEL_8 = "other_command"
      returns ("command", "LABEL_8")

3.  Engine routes to CommandDeclineGenerator.generate("LABEL_8")

4.  create_command_decline_prompt("LABEL_8") →
      key not in COMMAND_MAP →
      prompt: "roast user for invented syntax, tell them to use /help"

5.  gpt-5-mini called → "i'm sorry, '!buy me 5 swords please' isn't a thing?? just use !buy and figure it out"

6.  Reply returned to client
```

### Workflow 4: Real-World Question (Lore Decline)

```
1.  POST /chat { text: "what's the speed of light?", ... }

2.  main_router("what's the speed of light?") →
      IntentClassifier → "study"
      returns ("intent", "study")

3.  Engine: route_type=="intent", label=="study" → MsgDeclineGenerator.generate()

4.  lore_decline_prompt("what's the speed of light?") →
      prompt: "you're Veyra from Natlade, reject this real-world question in character"

5.  gpt-5-mini called →
      "...speed of... light? what even is a 'light speed'?
       are you making up words again? go outside."

6.  Reply returned to client (Veyra stays in character, never references physics)
```

---

## Developer Reference

### Adding a New Intent Class

1. Add labelled examples to `data/intent.jsonl` with your new label string.
2. Update the `labels` dict in `classifiers/train_intent.py`.
3. Update `IntentClassifier.LABELS` in `classifiers/intent_classifier.py`.
4. Update `Engine.respond()` in `engine/msg_gen_engine.py` to handle the new `label` value.
5. Retrain: `python classifiers/train_intent.py`.

### Adding a New Command

**If the command requires no user arguments (simple trigger):**
1. Add labelled examples to `data/commands.jsonl` with a new label string.
2. Add the label → integer mapping to the `labels` dict in `classifiers/train_command.py`.
3. Add the command to `COMMAND_MAP` in `prompts/command_decline.py`.
4. Retrain: `python classifiers/train_command.py`.

**No code changes needed in the engine** — the label string is already returned directly to the caller for any non-LABEL_8 command.

**If the command requires multi-word arguments** (already handled), ensure it maps to `other_command` / `LABEL_8` and the user is directed to the correct syntax via `COMMAND_MAP`.

### Swapping the Character

All character logic lives in `prompts/`:
- Edit `prompts/character_profile.py` to change Veyra's identity, lore rules, style, and friendship tier descriptors.
- Edit `prompts/msg_decline.py` to change how out-of-lore questions are rejected.
- Edit `prompts/command_decline.py` to change the command-correction persona.

No changes to the engine, router, classifiers, or generators are needed.

### Adding Persistence to Memory

Currently, `history` in `context_model.py` is an in-process list. To persist across restarts:
1. Replace the `history` list with reads/writes to a database or file.
2. Serialise/deserialise NumPy embedding vectors (e.g. via `np.save` / `np.load` or store as base64 strings).
3. The `fetch_context()` and `add_to_history()` function signatures need not change.

### Configuring LLM Parameters

Chat generation parameters are hardcoded in `generator/msg_generator.py`:
```python
max_tokens=60, temperature=0.9, top_p=0.95,
frequency_penalty=0.2, presence_penalty=0.1
```

Move these to environment variables or a config file if per-deployment tuning is needed.

### Extending `EmotionModel`

- Add new mood axes to `mood_state` in `EmotionModel.__init__`.
- Update the `extract_deltas` prompt to include the new axis names.
- Update `get_active_mood()` if more refined dominant-mood logic is needed (e.g. composite moods).
- Wire `decay_mood()` into a background task or a per-session cleanup hook to naturally return the character to a neutral state between conversations.

### Running Tests

The `tests/` directory currently exists but is empty. To add tests:
1. Use `pytest` with `pytest-asyncio` for testing async methods.
2. Mock the `AsyncOpenAI` client in `state/client.py` to avoid live API calls during test runs.
3. The pure-Python logic in `IntentClassifier`, `CommandClassifier`, and `EmotionModel.update_mood` / `get_active_mood` can be tested synchronously without mocking.

---

## Design Decisions

### Two-Stage Classification vs. Single Model

**Decision:** Use a two-stage cascade (intent → command) rather than a single model with all classes.

**Rationale:** The intent classifier solves a three-way high-level split. The command classifier handles 9 fine-grained game-specific categories. Training one unified model over all possible classes would require many more labelled examples, produce noisier class boundaries between conceptually distant categories (e.g. `chitchat` vs `check_wallet`), and make the system harder to extend. The cascade cleanly separates concerns: new commands can be added to the command model without retraining the intent model.

### Confidence Threshold in Intent Classifier

**Decision:** Return `"chitchat"` when the top softmax probability is below 0.35.

**Rationale:** In a Discord chat context, many messages are ambiguous, brief, or grammatically informal. Without a threshold, the model might confidently classify `"idk maybe"` as `"command"` simply because the logits nudge slightly that way. Defaulting to chitchat is the safest fallback — it invokes the full LLM pipeline and produces a relevant in-character response, whereas a wrong command classification would return a raw label string or a decline message that makes no sense.

### No Confidence Threshold in Command Classifier

**Decision:** Always return `argmax` from the command model.

**Rationale:** The command classifier is only invoked after the intent classifier already determined the message is a command. At this second stage, there is enough prior signal to commit to a specific command label. The `LABEL_8` ("other_command") class acts as a safety net — ambiguous or unrecognised commands fall into it and trigger the decline path.

### In-Memory Vector Store

**Decision:** Keep message history as a Python list with NumPy vectors rather than using a vector database (Pinecone, Chroma, Weaviate, etc.).

**Rationale:** For the current scale (single-process server, < 150 messages in memory), a vector database adds operational overhead without measurable benefit. NumPy cosine similarity over 150 vectors is essentially instant. The architecture is not hostile to replacing this — the `fetch_context` / `add_to_history` interface is clean and swappable.

### Singleton Classifier Instances

**Decision:** `IntentClassifier` and `CommandClassifier` are instantiated at module import time in `core/router.py`.

**Rationale:** Loading a DistilBERT model from disk takes ~1–2 seconds. If models were re-instantiated per request, the server would incur a multi-second delay on every single call. Module-level singletons load once and serve forever. The models are stateless during inference (`model.eval()`), making this completely safe for concurrent async usage.

### Singleton `EmotionModel`

**Decision:** `veyra = EmotionModel()` is a module-level singleton in `msg_generator.py`.

**Rationale:** The mood state must persist across requests to give the character emotional memory. A per-request instance would reset mood to zero every time. A module-level instance retains state for the lifetime of the server process.

**Trade-off:** This means all users share the same emotional state. If User A is extremely rude, Veyra becomes irritated for User B's subsequent message too. This is somewhat intentional — the character is meant to have a continuous inner life — but could be changed to per-user mood instances if needed.

### Prompt-as-Configuration

**Decision:** All persona behaviour is expressed as strings in `prompts/` Python files rather than config files or database records.

**Rationale:** Prompts benefit from Python string formatting (f-strings) and conditional logic. Keeping them in `.py` files gives full expressiveness; a plain `.txt` or `.yaml` approach would require a custom templating layer. The trade-off is that changing the character requires a code deployment rather than a database update.

### Three Separate Generators

**Decision:** Separate `ChatGenerator`, `CommandDeclineGenerator`, and `MsgDeclineGenerator` classes rather than a single generator with branching logic.

**Rationale:** Each generator has a distinct LLM model target, prompt structure, and parameter set. Separating them makes each independently testable, configurable, and replaceable. The engine's `if/else` branches remain clean because all generation specifics are encapsulated inside each class.

---

## Future Improvements

### 1. Persistent Cross-Session Memory

Currently all memory is lost on server restart. A Redis- or SQLite-backed store (or a proper vector database) would allow Veyra to remember conversations indefinitely. The `add_to_history` / `fetch_context` interface is already designed to be swapped out.

### 2. Per-User Mood State

The current mood model is global — one `EmotionModel` instance for all users. A `dict[int, EmotionModel]` keyed by `user_id` would give each user a private emotional relationship with the character.

### 3. Argument Extraction for Commands

Currently, multi-argument commands (e.g. `buy 3 swords`) fall to `LABEL_8` and are declined. An argument extraction layer (using a small LLM or a regex/NLP parser) could parse quantity, item name, and other arguments from the message and return a structured payload (`{"command": "buy", "item": "sword", "quantity": 3}`) rather than just a label string.

### 4. Mood Decay Scheduling

`EmotionModel.decay_mood()` exists but is never called. Wiring it into a background scheduler (e.g. FastAPI lifespan + `asyncio.create_task`) would slowly return Veyra to a neutral state between conversations, preventing permanent anger accumulation.

### 5. Response Caching

For high-traffic deployments, identical or near-identical messages by the same user could be cached (e.g. Redis with cosine-similarity-based cache keys) to avoid redundant OpenAI API calls.

### 6. Token Budget Management

The system prompt (`create_character_prompt`) can grow large as `chat_history` expands. Implementing token counting (via `tiktoken`) and truncating old history beyond a budget would prevent approaching the model's context window limit.

### 7. Streaming Responses

The current OpenAI call uses a blocking `await` for the entire completion. Streaming the response token-by-token via `stream=True` would allow the server to forward tokens to the client as they arrive, dramatically reducing perceived latency for end users.

### 8. Multi-Persona Support

The architecture already supports multiple characters (the `planner/` directory exists as a stub). A persona registry mapping character names to their prompt modules and emotion model instances would allow spawning multiple distinct AI characters from the same engine.

### 9. Evaluation Harness

The `tests/` directory is empty. A proper evaluation suite should test: classifier accuracy on held-out JSONL data; emotion delta correctness; context retrieval precision; and end-to-end pipeline responses against a golden dataset.

### 10. Kubernetes / Horizontal Scaling

The current architecture is single-process. Since `history` and `mood_state` are in-process globals, horizontal scaling requires moving these to a shared external store (Redis for mood state, a vector DB for history) and making the server stateless.

---

*Generated from full source analysis — last updated March 2026.*

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