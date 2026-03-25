import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from src.explainability.lime_explain import predict

# ✅ IMPORTANT: use your new LIME-based predictor
from src.explainability.lime_explain import predict

# ------------------------
# App Initialization
# ------------------------

app = FastAPI(title="ScamShield API")

origins = [
    "chrome-extension://lajgddkjgchejfnldleoicmpojdejndi",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Request / Response Schemas
# ------------------------

class PredictRequest(BaseModel):
    text: str
    explain: bool = False  # ✅ NEW


class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: Optional[List[str]] = None


# ------------------------
# Prediction Endpoint
# ------------------------

@app.post("/predict", response_model=PredictResponse)
async def predict_text(request: PredictRequest):

    print(f"Received request: text='{request.text}', explain={request.explain}")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        result = predict(request.text, explain=request.explain)

        return PredictResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            explanation=result["explanation"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))