# ScamShield 🛡️

ScamShield is a phishing detection system that uses a fine-tuned **DistilBERT** model to classify messages as legitimate or scam/phishing.

The system also uses a probability threshold to identify messages with an intermediate scam probability as **likely spam**.

## Features

* DistilBERT-based text classification
* Legit vs scam detection
* Threshold-based likely-spam detection
* LIME-based explanations
* FastAPI backend
* URL checking using Google Safe Browsing
* QR-code based detection

## How it works

```text
Message
   ↓
Tokenization
   ↓
DistilBERT
   ↓
Scam Probability
   ↓
Threshold Logic
   ↓
Legit / Likely Spam / Scam
   ↓
LIME Explanation
```

The underlying DistilBERT model is trained as a **binary classifier**:

* `0` → Legit
* `1` → Scam

The third output category is created after prediction using thresholds:

```text
Scam probability < 0.40
        → Legit

0.40 ≤ Scam probability < 0.80
        → Likely Spam

Scam probability ≥ 0.80
        → Scam
```

Therefore, `likely spam` is **not a separately trained class**. It is a threshold-based interpretation of the model's confidence.

## Model

* Model: `distilbert-base-uncased`
* Task: Binary text classification
* Classes: Legit / Scam
* Framework: Hugging Face Transformers
* Training: Fine-tuning on combined message/email datasets

## Explainability

LIME is used to provide a local explanation for individual predictions.

It creates modified versions of the input text, obtains predictions from the model, and identifies words that are influential for the prediction.

Example:

```text
Input:
"Your account requires urgent verification"

Explanation:
account
urgent
verification
```

## Backend

The FastAPI backend provides endpoints for:

* `/predict` — classify a message
* `/url-check` — check a URL
* `/predict-qr` — analyze a QR-code image

## Project Structure

```text
ScamShield/
│
├── models/
│   └── checkpoints/
│       └── best_model/
│
├── run.py
├── lime_explain.py
├── requirements.txt
└── README.md
```

## Running

Install the required packages:

```bash
pip install -r requirements.txt
```

Then run the FastAPI application:

```bash
uvicorn run:app --reload
```

## Limitations

* Spam is not a separately trained class.
* The likely-spam category is based on manually selected probability thresholds.
* LIME currently uses a relatively small number of samples.
* The model can struggle with subtle or less-represented scam types.
* Long messages may be truncated during inference.
* The final model was trained for one epoch.

## Future Improvements

* Build a clean, manually validated three-class dataset
* Improve spam/scam separation
* Tune probability thresholds using validation data
* Improve LIME explanations
* Increase training and evaluation on diverse datasets
