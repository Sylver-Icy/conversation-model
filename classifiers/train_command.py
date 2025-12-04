"""
Training script for the command classification model.
Loads a JSONL dataset of command examples, tokenizes it, fine‑tunes a DistilBERT classifier,
and saves the resulting model + tokenizer to ./command_model.
Designed to be modular and reusable in any project.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# Base model to fine‑tune. Can be swapped with any HF model supporting sequence classification.
model_name = "distilbert-base-uncased"

# Load the dataset containing text + label fields.
# Expecting a .jsonl file where each row has: {"text": "...", "label": "..."}.
dataset = load_dataset("json", data_files="data/commands.jsonl")

# Mapping string labels → numerical IDs for the model.
labels = {
    "check_wallet": 0,
    "check_exp": 1,
    "check_energy": 2,
    "check_friendship": 3,
    "quest": 4,
    "shop": 5,
    "start_race": 6,
    "other_command": 7
}

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

# Load the base model and attach a classification head with 8 output labels.
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=8)

# Configure training hyperparameters.
args = TrainingArguments(
    output_dir="./command_model",
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
trainer.save_model("./command_model")
tokenizer.save_pretrained("./command_model")