from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image
import io
import os

from datetime import datetime

from transformers import pipeline

app = FastAPI()

# -------------------------------------------------
# CORS
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# IMAGE MODEL
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.onnx")

image_session = ort.InferenceSession(MODEL_PATH)

# -------------------------------------------------
# DISTILBERT MODEL
# -------------------------------------------------

text_classifier = None

def get_text_classifier():
    global text_classifier

    if text_classifier is None:
        print("Loading DistilBERT...")

        text_classifier = pipeline(
            "text-classification",
            model="Rajesh282002/smellsense-distilbert",
            tokenizer="Rajesh282002/smellsense-distilbert",
            token=os.getenv("HF_TOKEN")
        )

        print("✅ DistilBERT Loaded!")

    return text_classifier

# -------------------------------------------------
# IMAGE PREPROCESS
# -------------------------------------------------

def preprocess(image):

    image = cv2.resize(image, (224, 224))
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)

    return image


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Food Freshness API is running 🚀"
    }


# -------------------------------------------------
# IMAGE + TEXT PREDICTION
# -------------------------------------------------

@app.post("/predict")
async def predict(

    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form("")

):

    if not file and not text:

        return {
            "error": "Provide either an image or text."
        }

    # =============================================
    # IMAGE
    # =============================================

    if file:

        contents = await file.read()

        image = Image.open(io.BytesIO(contents)).convert("RGB")
        image = np.array(image)

        input_data = preprocess(image)

        prediction = image_session.run(
            None,
            {"args_0:0": input_data}
        )[0][0][0]

        print("Image Prediction :", prediction)

        if prediction < 0.5:

            result = "Fresh"
            confidence = (1 - float(prediction)) * 100

        else:

            result = "Spoiled"
            confidence = float(prediction) * 100

        return {

            "result": result,
            "confidence": round(confidence, 2),
            "score": round(confidence, 2)

        }

    # =============================================
    # TEXT
    # =============================================

    classifier = get_text_classifier()
    prediction = classifier(text)[0]

    print(prediction)

    if prediction["label"] == "LABEL_0":

        result = "Fresh"

    else:

        result = "Spoiled"

    confidence = prediction["score"] * 100

    return {

        "result": result,
        "confidence": round(confidence, 2),
        "score": round(confidence, 2)

    }


# -------------------------------------------------
# EXPIRY DATE PREDICTION
# -------------------------------------------------

@app.post("/predict-expiry")
async def predict_expiry(

    product_name: str = Form(...),
    manufacturing_date: str = Form(...),
    expiry_date: str = Form(...)

):

    try:

        today = datetime.now().date()

        mfg = datetime.strptime(
            manufacturing_date,
            "%Y-%m-%d"
        ).date()

        exp = datetime.strptime(
            expiry_date,
            "%Y-%m-%d"
        ).date()

        if exp <= mfg:

            return {
                "error": "Expiry date must be after manufacturing date."
            }

        total_shelf_life = (exp - mfg).days

        remaining_days = (exp - today).days

        freshness_score = max(
            0,
            min(
                100,
                (remaining_days / total_shelf_life) * 100
            )
        )

        if remaining_days < 0:

            result = "Spoiled"

        elif freshness_score <= 20:

            result = "Near Expiry"

        else:

            result = "Fresh"

        return {

            "product": product_name,

            "result": result,

            "freshness_score": round(freshness_score, 2),

            "remaining_days": remaining_days,

            "total_shelf_life": total_shelf_life

        }

    except Exception as e:

        return {
            "error": str(e)
        }