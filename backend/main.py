from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from transformers import AutoTokenizer
from huggingface_hub import hf_hub_download

import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image
import io
import os

from datetime import datetime


# =================================================
# FASTAPI
# =================================================

app = FastAPI(
    title="SmellSense AI API",
    description=(
        "AI-powered food freshness detection using "
        "image, text, and expiry-date analysis"
    ),
    version="1.0.0"
)


# =================================================
# CORS
# =================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =================================================
# BASE DIRECTORY
# =================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# =================================================
# IMAGE MODEL
# =================================================

MODEL_PATH = os.path.join(
    BASE_DIR,
    "model",
    "model.onnx"
)

print("Loading image ONNX model...")
print("Image model path:", MODEL_PATH)

if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Image ONNX model not found: {MODEL_PATH}"
    )

image_session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

print("Image ONNX model loaded successfully!")


# =================================================
# TEXT MODEL DIRECTORY
# =================================================

TEXT_MODEL_DIR = os.path.join(
    BASE_DIR,
    "model",
    "text_model",
    "distilbert_onnx"
)

print("Text model directory:", TEXT_MODEL_DIR)

if not os.path.isdir(TEXT_MODEL_DIR):
    raise FileNotFoundError(
        f"Text model directory not found: {TEXT_MODEL_DIR}"
    )


# =================================================
# LOAD TEXT TOKENIZER
# =================================================

print("Loading text tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    TEXT_MODEL_DIR,
    local_files_only=True
)

print("Text tokenizer loaded successfully!")


# =================================================
# DOWNLOAD QUANTIZED TEXT ONNX MODEL
# FROM HUGGING FACE
# =================================================

print(
    "Downloading/loading quantized text ONNX model "
    "from Hugging Face..."
)

TEXT_ONNX_PATH = hf_hub_download(
    repo_id="Rajesh282002/smellsense-distilbert",
    filename="model_quantized.onnx"
)

print(
    "Quantized text ONNX model path:",
    TEXT_ONNX_PATH
)


# =================================================
# LOAD QUANTIZED TEXT ONNX MODEL
# =================================================

print(
    "Loading quantized text ONNX model "
    "into ONNX Runtime..."
)

text_session = ort.InferenceSession(
    TEXT_ONNX_PATH,
    providers=["CPUExecutionProvider"]
)

print(
    "Quantized text ONNX model loaded successfully!"
)


# =================================================
# DEBUG: PRINT TEXT MODEL INPUTS
# =================================================

print("\nText model inputs:")

for model_input in text_session.get_inputs():

    print(
        f"Name: {model_input.name}, "
        f"Shape: {model_input.shape}, "
        f"Type: {model_input.type}"
    )


# =================================================
# DEBUG: PRINT TEXT MODEL OUTPUTS
# =================================================

print("\nText model outputs:")

for model_output in text_session.get_outputs():

    print(
        f"Name: {model_output.name}, "
        f"Shape: {model_output.shape}, "
        f"Type: {model_output.type}"
    )


# =================================================
# IMAGE PREPROCESSING
# =================================================

def preprocess(image):

    image = cv2.resize(
        image,
        (224, 224)
    )

    image = image.astype(
        np.float32
    ) / 255.0

    image = np.expand_dims(
        image,
        axis=0
    )

    return image


# =================================================
# SOFTMAX FUNCTION
# =================================================

def softmax(logits):

    logits = np.asarray(
        logits,
        dtype=np.float32
    )

    # Numerically stable softmax
    exp_values = np.exp(
        logits
        - np.max(
            logits,
            axis=-1,
            keepdims=True
        )
    )

    probabilities = (
        exp_values
        / np.sum(
            exp_values,
            axis=-1,
            keepdims=True
        )
    )

    return probabilities


# =================================================
# HOME
# =================================================

@app.get("/")
def home():

    return {
        "message": "Food Freshness API is running 🚀",
        "image_model": "loaded",
        "text_model": "INT8 quantized ONNX loaded"
    }


# =================================================
# HEALTH CHECK
# =================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "image_model_loaded": (
            image_session is not None
        ),
        "text_model_loaded": (
            text_session is not None
        ),
        "tokenizer_loaded": (
            tokenizer is not None
        ),
        "text_model_type": (
            "INT8 quantized ONNX"
        )
    }


# =================================================
# IMAGE + TEXT PREDICTION
# =================================================

@app.post("/predict")
async def predict(

    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form("")

):

    try:

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        has_file = (
            file is not None
            and file.filename is not None
            and file.filename.strip() != ""
        )

        has_text = (
            text is not None
            and text.strip() != ""
        )

        if not has_file and not has_text:

            return {
                "error": (
                    "Provide either an image or text."
                )
            }


        # =========================================
        # IMAGE PREDICTION
        # =========================================

        if has_file:

            contents = await file.read()

            image = Image.open(
                io.BytesIO(contents)
            ).convert("RGB")

            image = np.array(image)

            input_data = preprocess(image)

            # Automatically get the actual
            # image-model input name
            image_input_name = (
                image_session
                .get_inputs()[0]
                .name
            )

            prediction_output = (
                image_session.run(
                    None,
                    {
                        image_input_name:
                        input_data
                    }
                )
            )

            prediction = float(
                np.asarray(
                    prediction_output[0]
                ).flatten()[0]
            )

            print(
                "Image Prediction:",
                prediction
            )

            if prediction < 0.5:

                result = "Fresh"

                confidence = (
                    1 - prediction
                ) * 100

            else:

                result = "Spoiled"

                confidence = (
                    prediction * 100
                )

            return {
                "analysis_type": "image",
                "result": result,
                "confidence": round(
                    confidence,
                    2
                ),
                "score": round(
                    confidence,
                    2
                )
            }


        # =========================================
        # TEXT PREDICTION
        # =========================================

        if has_text:

            cleaned_text = text.strip()

            print("\nReceived text:")
            print(cleaned_text)


            # -------------------------------------
            # TOKENIZE TEXT
            # -------------------------------------

            encoded = tokenizer(
                cleaned_text,
                return_tensors="np",
                padding=True,
                truncation=True,
                max_length=128
            )

            print(
                "Tokenizer output keys:",
                list(encoded.keys())
            )


            # -------------------------------------
            # PREPARE ONNX INPUTS
            # -------------------------------------

            onnx_inputs = {}

            for model_input in (
                text_session.get_inputs()
            ):

                input_name = (
                    model_input.name
                )

                if input_name not in encoded:

                    print(
                        "Skipping unavailable "
                        f"input: {input_name}"
                    )

                    continue

                input_array = np.asarray(
                    encoded[input_name]
                )

                if (
                    "int64"
                    in model_input.type
                ):

                    input_array = (
                        input_array.astype(
                            np.int64
                        )
                    )

                elif (
                    "int32"
                    in model_input.type
                ):

                    input_array = (
                        input_array.astype(
                            np.int32
                        )
                    )

                onnx_inputs[
                    input_name
                ] = input_array


            print(
                "ONNX input keys:",
                list(onnx_inputs.keys())
            )


            # -------------------------------------
            # VERIFY REQUIRED INPUTS
            # -------------------------------------

            required_inputs = {
                model_input.name
                for model_input
                in text_session.get_inputs()
            }

            provided_inputs = set(
                onnx_inputs.keys()
            )

            missing_inputs = (
                required_inputs
                - provided_inputs
            )

            if missing_inputs:

                return {
                    "error": (
                        "Missing required "
                        "ONNX inputs."
                    ),
                    "missing_inputs": list(
                        missing_inputs
                    ),
                    "available_tokenizer_inputs":
                        list(encoded.keys())
                }


            # -------------------------------------
            # RUN QUANTIZED TEXT MODEL
            # -------------------------------------

            outputs = text_session.run(
                None,
                onnx_inputs
            )

            logits = np.asarray(
                outputs[0]
            )

            print(
                "Raw logits:",
                logits
            )


            # -------------------------------------
            # CALCULATE PROBABILITIES
            # -------------------------------------

            probabilities = softmax(
                logits
            )

            print(
                "Probabilities:",
                probabilities
            )

            predicted_class = int(
                np.argmax(
                    probabilities,
                    axis=-1
                )[0]
            )

            confidence = float(
                np.max(
                    probabilities,
                    axis=-1
                )[0]
            ) * 100


            # -------------------------------------
            # LABEL MAPPING
            # -------------------------------------
            #
            # Class 0 = Fresh
            # Class 1 = Spoiled
            # -------------------------------------

            label_map = {
                0: "Fresh",
                1: "Spoiled"
            }

            result = label_map.get(
                predicted_class,
                f"Class {predicted_class}"
            )


            # -------------------------------------
            # RECOMMENDATION
            # -------------------------------------

            if result == "Fresh":

                recommendation = (
                    "The food appears fresh "
                    "based on the provided "
                    "description."
                )

            elif result == "Spoiled":

                recommendation = (
                    "The food may be spoiled. "
                    "Avoid consuming it if there "
                    "are signs of mold, rotten "
                    "smell, slimy texture, or "
                    "unusual appearance."
                )

            else:

                recommendation = (
                    "Unable to provide a "
                    "specific freshness "
                    "recommendation."
                )


            # -------------------------------------
            # RETURN TEXT RESULT
            # -------------------------------------

            return {
                "analysis_type": "text",
                "result": result,
                "confidence": round(
                    confidence,
                    2
                ),
                "score": round(
                    confidence,
                    2
                ),
                "predicted_class":
                    predicted_class,
                "model_type":
                    "INT8 quantized ONNX",
                "recommendation":
                    recommendation
            }


    except Exception as e:

        print("\nPrediction error:")

        print(
            type(e).__name__,
            ":",
            str(e)
        )

        return {
            "error": "Prediction failed.",
            "details": str(e)
        }


# =================================================
# EXPIRY DATE PREDICTION
# =================================================

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


        # -----------------------------------------
        # VALIDATE DATES
        # -----------------------------------------

        if exp <= mfg:

            return {
                "error": (
                    "Expiry date must be after "
                    "manufacturing date."
                )
            }


        # -----------------------------------------
        # CALCULATE SHELF LIFE
        # -----------------------------------------

        total_shelf_life = (
            exp - mfg
        ).days

        remaining_days = (
            exp - today
        ).days


        # -----------------------------------------
        # CALCULATE FRESHNESS SCORE
        # -----------------------------------------

        freshness_score = max(
            0,
            min(
                100,
                (
                    remaining_days
                    / total_shelf_life
                ) * 100
            )
        )


        # -----------------------------------------
        # DETERMINE RESULT
        # -----------------------------------------

        if remaining_days < 0:

            result = "Spoiled"

        elif freshness_score <= 20:

            result = "Near Expiry"

        else:

            result = "Fresh"


        # -----------------------------------------
        # RETURN RESULT
        # -----------------------------------------

        return {
            "product": product_name,
            "result": result,
            "freshness_score": round(
                freshness_score,
                2
            ),
            "remaining_days":
                remaining_days,
            "total_shelf_life":
                total_shelf_life
        }


    except ValueError:

        return {
            "error": (
                "Invalid date format. "
                "Use YYYY-MM-DD."
            )
        }


    except Exception as e:

        print(
            "Expiry prediction error:",
            str(e)
        )

        return {
            "error": str(e)
        }