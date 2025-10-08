import pandas as pd
import yaml
from datasets import Dataset
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    TrainingArguments,
    Trainer,
    set_seed,
)
import torch
from torch.nn import CrossEntropyLoss
from sklearn.model_selection import train_test_split
import os

set_seed(42)

# === Load CSV Dataset ===
csv_path = "C:/Users/gowth/Desktop/ChatBot/models/wellness_dataset.csv"
df_csv = pd.read_csv(csv_path)
df_csv = df_csv.dropna(subset=["text", "label"])[["text", "label"]]

# === Load YAML NLU Data ===
yaml_path = "C:/Users/gowth/Desktop/ChatBot/models/nlu_data.yml"
with open(yaml_path, "r", encoding="utf-8") as f:
    nlu_yaml = yaml.safe_load(f)

nlu_rows = []
for item in nlu_yaml["nlu"]:
    intent = item["intent"]
    examples = item["examples"].split("\n")
    for ex in examples:
        ex = ex.strip("- ").strip()
        if ex:
            nlu_rows.append({"text": ex, "label": intent})

df_yaml = pd.DataFrame(nlu_rows)

# === Merge CSV + YAML ===
df = pd.concat([df_csv, df_yaml], ignore_index=True)

# === Generate Synthetic Queries ===
synthetic_data = []
for _, row in df_csv.iterrows():
    disease = row.get("ChronicDisease", "")
    mood = row.get("Mood", "")
    factors = row.get("LifestyleFactors", "")

    if pd.notna(disease) and disease.lower() != "none":
        synthetic_data.append({
            "text": f"I have {disease.lower()}, what should I do?",
            "label": "disease_advice"
        })

    if pd.notna(mood):
        synthetic_data.append({
            "text": f"I'm feeling {mood.lower()}, any wellness tips?",
            "label": "wellness_tip"
        })

    if pd.notna(factors):
        for factor in str(factors).split(","):
            synthetic_data.append({
                "text": f"I've been doing {factor.strip().lower()}, is that healthy?",
                "label": "general_query"
            })

df_synthetic = pd.DataFrame(synthetic_data)
df = pd.concat([df, df_synthetic], ignore_index=True)

print("Intents in training data:", sorted(df["label"].unique()))

print(df["label"].value_counts())

# === Encode Labels ===
labels_sorted = sorted(df["label"].unique())
label2id = {l: i for i, l in enumerate(labels_sorted)}
id2label = {i: l for l, i in label2id.items()}
df["label_id"] = df["label"].map(label2id)

# === Train-Test Split ===
train_df, test_df = train_test_split(
    df[["text", "label", "label_id"]],
    test_size=0.2,
    stratify=df["label"],
    random_state=42,
)

train_ds = Dataset.from_pandas(train_df.reset_index(drop=True))
eval_ds = Dataset.from_pandas(test_df.reset_index(drop=True))

# === Tokenization ===
tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

def preprocess(batch):
    toks = tokenizer(batch["text"], padding="max_length", truncation=True, max_length=128)
    toks["labels"] = batch["label_id"]
    return toks

train_ds = train_ds.map(preprocess, batched=True, remove_columns=train_ds.column_names)
eval_ds = eval_ds.map(preprocess, batched=True, remove_columns=eval_ds.column_names)
train_ds.set_format("torch")
eval_ds.set_format("torch")

# === Model Setup ===
model = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=len(labels_sorted),
    id2label=id2label,
    label2id=label2id,
)

# === Class Weights ===
class_counts = df["label"].value_counts().to_dict()
total = len(df)
weights_list = [total / class_counts[id2label[i]] for i in range(len(labels_sorted))]
class_weights = torch.tensor(weights_list, dtype=torch.float)

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels").to(model.device)
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = CrossEntropyLoss(weight=class_weights.to(logits.device))
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# === Training Arguments ===
training_args = TrainingArguments(
    output_dir="./results",
    save_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=8,
    weight_decay=0.01,
    warmup_ratio=0.1,
    logging_dir="./logs",
    logging_steps=10,
)

# === Evaluation Metrics ===
def compute_metrics(eval_pred):
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted", zero_division=0)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": p, "recall": r}

# === Train Model ===
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=eval_ds,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()
final_metrics = trainer.evaluate()
print("Final eval metrics:", final_metrics)

# === Save Model ===
save_path = "./models/wellness-intent"
os.makedirs(save_path, exist_ok=True)
trainer.model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

# Manual Save
torch.save(trainer.model.state_dict(), os.path.join(save_path, "pytorch_model.bin"))
trainer.model.config.to_json_file(os.path.join(save_path, "config.json"))

print("✅ Model weights saved to ./models/wellness-intent")
