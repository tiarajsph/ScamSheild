import torch
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from tqdm import tqdm
import os

from src.models.model import DistilBERTClassifier

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TRAIN_PATH = "data/processed/train_encodings.pt"
TEST_PATH = "data/processed/test_encodings.pt"

BATCH_SIZE = 16
EPOCHS = 5  # Increased from 1 to 5 for better training
LEARNING_RATE = 2e-5


class ScamDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __len__(self):
        return len(self.encodings["input_ids"])

    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.encodings["labels"][idx],
        }


def evaluate(model, dataloader):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            outputs = model(input_ids, attention_mask)
            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average="binary"
    )

    return acc, precision, recall, f1


def train():
    print("Loading encodings...")
    train_encodings = torch.load(TRAIN_PATH, weights_only=False)
    test_encodings = torch.load(TEST_PATH, weights_only=False)

    train_dataset = ScamDataset(train_encodings)
    test_dataset = ScamDataset(test_encodings)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    model = DistilBERTClassifier().to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    best_f1 = 0.0

    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        print(f"\nEpoch {epoch+1}/{EPOCHS}")

        for batch in tqdm(train_loader):
            input_ids = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)

            optimizer.zero_grad()

            outputs = model(input_ids, attention_mask)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        acc, precision, recall, f1 = evaluate(model, test_loader)

        print(f"Train Loss: {avg_loss:.4f}")
        print(f"Validation Accuracy: {acc:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(), "models/checkpoints/best_model.pt")
            print("Best model saved.")

    print("\nTraining complete.")


if __name__ == "__main__":
    train()