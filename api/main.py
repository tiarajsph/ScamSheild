from lime.lime_text import LimeTextExplainer
import logging
logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os
import re
import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
import os

# Import the ML inference function
from src.models.inference import predict

# For QR decoding
from PIL import Image
from pyzbar.pyzbar import decode


app = FastAPI(title="ScamShield API")

# CORS (allow extension + frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # You can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------
# Schemas
# ------------------------

class PredictRequest(BaseModel):
    message: str


class PredictResponse(BaseModel):
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    explanation: Optional[list[str]] = None
    url_risks: Optional[list[str]] = None

class URLCheckRequest(BaseModel):
    url: str

class URLCheckResponse(BaseModel):
    risks: list[str]


# ------------------------
# TEXT PREDICTION
# ------------------------
def map_explanation_to_reasons(words):
    cleaned = [
        w.lower()
        for w in words
        if w.isalpha() and len(w) > 2
    ]

    if not cleaned:
        return ["no strong suspicious patterns detected"]

    # remove duplicates but keep order
    seen = set()
    cleaned_unique = []
    for w in cleaned:
        if w not in seen:
            seen.add(w)
            cleaned_unique.append(w)

    top_words = cleaned_unique[:6]

    return top_words
@app.post("/predict", response_model=PredictResponse)
async def predict_text(request: PredictRequest):

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        result = predict(request.message)

        # 🔥 Convert LIME words → human reasons
        mapped_reasons = map_explanation_to_reasons(result["explanation"])

        return PredictResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            explanation=mapped_reasons
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ----------------------------
# Google Safe Browsing Helper
# ----------------------------
def google_safe_browsing_check(url):
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "scamshield", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    logging.info(f"Calling Google Safe Browsing API for URL: {url}")
    try:
        resp = requests.post(endpoint, json=payload, timeout=5)
        logging.info(f"Google Safe Browsing response status: {resp.status_code}")
        logging.info(f"Google Safe Browsing response body: {resp.text}")
        resp.raise_for_status()
        data = resp.json()
        if "matches" in data:
            return "Unsafe: Threat detected by Google Safe Browsing"
        else:
            return "Safe: No threats found by Google Safe Browsing"
    except Exception as e:
        logging.error(f"Safe Browsing check error: {str(e)}")
        return f"Safe Browsing check error: {str(e)}"

# ------------------------
# URL CHECK ENDPOINT
# ------------------------

@app.post("/url-check", response_model=URLCheckResponse)
async def url_check(request: URLCheckRequest):
    verdict = google_safe_browsing_check(request.url)
    return URLCheckResponse(risks=[verdict])
# ------------------------
# QR PREDICTION
# ------------------------

@app.post("/predict-qr", response_model=PredictResponse)
async def predict_qr(file: UploadFile = File(...)):
    try:
        temp_path = "temp_qr.png"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image = Image.open(temp_path)
        decoded_objects = decode(image)
        if not decoded_objects:
            raise HTTPException(status_code=400, detail="No QR code found")
        extracted_text = decoded_objects[0].data.decode("utf-8")
        prediction = None
        confidence = None
        explanation = []
        url_risks = []
        if re.match(r"https?://", extracted_text):
            # Only run Google Safe Browsing check for URLs
            url_risks = [google_safe_browsing_check(extracted_text)]
        else:
            # Only run ML prediction for plain text
            result = predict(extracted_text)
            prediction = result["prediction"]
            confidence = result["confidence"]
            explanation = map_explanation_to_reasons(result["explanation"])
        os.remove(temp_path)
        return PredictResponse(
            prediction=prediction,
            confidence=confidence,
            explanation=explanation,
            url_risks=url_risks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))