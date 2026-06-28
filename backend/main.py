from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image
import io
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ONNX model
session = ort.InferenceSession("model/model.onnx")


def preprocess(image):
    image = cv2.resize(image, (224, 224))
    image = image / 255.0
    image = np.expand_dims(image.astype(np.float32), axis=0)
    return image


@app.get("/")
def home():
    return {"message": "Food Freshness API is running 🚀"}


@app.post("/predict")
async def predict(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(""),
    expiry_date: Optional[str] = Form("")
):

    pred = None
    result = "Unknown"

    # Image Prediction
    if file:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image)

        input_data = preprocess(image)

        pred = session.run(None, {"args_0:0": input_data})[0][0][0]

        print("Prediction:", pred)

        # Fresh / Spoiled
        if pred < 0.5:
            result = "Fresh"
        else:
            result = "Spoiled"

        print("Final Result:", result)

    # No input
    if not file and not text and not expiry_date:
        return {"error": "Provide at least one input"}

    # Text Adjustment
    bad_words = ["rotten", "smell", "mushy", "black", "fungus"]

    if text and any(word in text.lower() for word in bad_words):
        result = "Spoiled"

    # Expiry Date Adjustment
    if expiry_date:
        try:
            exp = datetime.strptime(expiry_date, "%Y-%m-%d")
            if datetime.now() > exp:
                result = "Spoiled"
        except:
            pass

    # Score Calculation
    score = None

    if pred is not None:
        if result == "Fresh":
            score = round((1 - float(pred)) * 100, 2)
        else:
            score = round(float(pred) * 100, 2)

    return {
        "result": result,
        "score": score,
        "confidence": float(pred) if pred is not None else None
    }