from lime.lime_text import LimeTextExplainer
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# =========================
# DEVICE
# =========================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# MODEL PATH (FOLDER, not .pt)
# =========================

MODEL_PATH = "models/checkpoints/new_model"

# =========================
# LOAD TOKENIZER + MODEL
# =========================

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(DEVICE)
model.eval()

# =========================
# LIME EXPLAINER
# =========================

explainer = LimeTextExplainer(class_names=["legit","likely scam","scam"])

# =========================
# PROBABILITY FUNCTION (for LIME)
# =========================

def predict_proba(texts):
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=64,
        return_tensors="pt"
    )

    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)

    return probabilities.cpu().numpy()

# =========================
# MAIN PREDICT FUNCTION
# =========================

def predict(text: str):

    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=64,
        return_tensors="pt"
    )

    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)
        confidence, predicted_class = torch.max(probabilities, dim=1)

    ###label_map = model.config.id2label
    ###prediction = label_map[predicted_class.item()]
    label_map = {
    0: "legit",
    1: "likely scam",
    2: "scam"
    }

    prediction = label_map[predicted_class.item()]

    # =========================
    # LIME EXPLANATION
    # =========================

    explanation = explainer.explain_instance(
        text,
        predict_proba,
        num_features=6,
        num_samples=100
    )

    STOPWORDS = {
        "this", "that", "for", "with", "and", "the", "you",
        "your", "from", "into", "have", "has", "using"
    }

    lime_words = [w for w, _ in explanation.as_list()]

    input_words = text.lower().split()

    important_words = [
    w for w in input_words
    if w in lime_words
    and w.isalpha()
    and len(w) > 3
    and w not in STOPWORDS
    ]

    if not important_words:
        important_words = input_words[:5]
    return {
        "prediction": prediction,
        "confidence": round(confidence.item(), 4),
        "explanation": important_words
    }

# =========================
# TEST
# =========================

if __name__ == "__main__":
    sample_text = "Urgent! Your bank account has been suspended. Click here to verify immediately."
    result = predict(sample_text)
    print(result)