import torch
import numpy as np
from lime.lime_text import LimeTextExplainer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# =========================
# DEVICE
# =========================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# MODEL PATH (FOLDER)
# =========================

MODEL_PATH = "models/checkpoints/best_model"

# =========================
# LOAD MODEL + TOKENIZER
# =========================

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(DEVICE)
model.eval()

class_names = ["legit", "scam"]

# Initialize LIME once
explainer = LimeTextExplainer(class_names=class_names)


# =========================
# PREDICT PROBA (for LIME)
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
        probs = torch.softmax(outputs.logits, dim=1)

    return probs.cpu().numpy()


# =========================
# MAIN PREDICT FUNCTION
# =========================

def predict(text, explain=False):

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
        probs = torch.softmax(outputs.logits, dim=1)

    # =========================
    # THRESHOLD-BASED LOGIC
    # =========================

    scam_prob = probs[0][1].item()

    if scam_prob >= 0.85:
        prediction = "scam"
        confidence = scam_prob

    elif scam_prob >= 0.6:
        prediction = "likely spam"
        confidence = scam_prob

    else:
        prediction = "legit"
        confidence = 1 - scam_prob

    # =========================
    # OPTIONAL LIME
    # =========================

    explanation_words = []

    if explain:
        explanation = explainer.explain_instance(
            text,
            predict_proba,
            num_features=6,
            num_samples=30
        )

        explanation_words = [
            str(word) for word, weight in explanation.as_list()
        ]

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "explanation": explanation_words
    }


# =========================
# TEST
# =========================

if __name__ == "__main__":

    sample_text = "Hi team, please find attached the meeting minutes from yesterday."

    print("\n--- WITHOUT EXPLANATION ---")
    print(predict(sample_text, explain=False))

    print("\n--- WITH EXPLANATION ---")
    print(predict(sample_text, explain=True))