"""
Training script for the intent classification model.
Loads a JSONL dataset, tokenizes it, fine-tunes a DistilBERT classifier,
and saves the resulting model + tokenizer to ./intent_model.
Designed to be lightweight and easy to reuse in any project.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# Base model to fine‑tune. Can be swapped with any HF model supporting sequence classification.
model_name = "distilbert-base-uncased"

# Load the dataset containing text + label fields.
# Expecting a .jsonl file where each row has: {"text": "...", "label": "..."}.
dataset = load_dataset("json", data_files="data/intent.jsonl")

# Mapping string labels → numerical IDs for the model.
labels = {"command": 0, "study": 1, "chitchat": 2}

def encode(batch):
    """
    Converts raw text + labels into tokenized batches the model can train on.
    Also attaches numeric label IDs to each item.
    """
    batch["labels"] = [labels[l] for l in batch["label"]]
    # Tokenize the input text. Using max_length padding for consistency.
    return tokenizer(batch["text"], truncation=True, padding="max_length")

# Initialize tokenizer from the selected base model.
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Apply encoding to the entire dataset.
dataset = dataset.map(encode, batched=True)
dataset = dataset.remove_columns(["label"])

# Load the base model and attach a classification head with 3 output labels.
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# Configure training hyperparameters.
args = TrainingArguments(
    output_dir="./intent_model",
    per_device_train_batch_size=8,
    num_train_epochs=5 ,
    learning_rate=4e-5,
    logging_steps=20
)

# HuggingFace Trainer handles batching, optimization, logging, etc.
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
)

trainer.train()

# Save the fine‑tuned model + tokenizer so the classifier can load them later.
trainer.save_model("./intent_model")
tokenizer.save_pretrained("./intent_model")