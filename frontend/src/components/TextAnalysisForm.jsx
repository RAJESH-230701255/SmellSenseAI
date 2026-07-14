import { useState } from "react";
import api from "../api/api";
import "../styles/form.css";

function TextAnalysisForm() {

    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {

        if (text.trim() === "") {
            alert("Please enter a food description.");
            return;
        }

        try {

            setLoading(true);
            setResult(null);

            // Create FormData because FastAPI expects Form(...)
            const formData = new FormData();

            formData.append("text", text.trim());

            // Send text directly to Render FastAPI backend
            const response = await api.post(
                "/predict",
                formData
            );

            console.log("Text prediction response:", response.data);

            setResult(response.data);

        } catch (err) {

            console.error("Text analysis error:", err);

            const errorMessage =
                err.response?.data?.error ||
                err.message ||
                "Prediction failed";

            alert("Prediction Failed: " + errorMessage);

        } finally {

            setLoading(false);

        }
    };

    return (

        <div className="form-container">

            <h2>Text Analysis</h2>

            <p>
                Describe the food and AI will predict whether it is Fresh or Spoiled.
            </p>

            <textarea
                rows="8"
                className="description-box"
                placeholder="Example: The banana has black spots and smells rotten."
                value={text}
                onChange={(e) => setText(e.target.value)}
                disabled={loading}
            />

            <button
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={loading}
            >
                {loading ? "Analyzing..." : "Analyze"}
            </button>

            {result && (

                <div className="result-box">

                    <h3>Prediction Result</h3>

                    <p>
                        <strong>Result:</strong> {result.result}
                    </p>

                    <p>
                        <strong>Confidence:</strong> {result.confidence}%
                    </p>

                    <p>
                        <strong>Score:</strong> {result.score}%
                    </p>

                    {result.model_type && (
                        <p>
                            <strong>Model:</strong>{" "}
                            {result.model_type}
                        </p>
                    )}

                    {result.recommendation && (
                        <p>
                            <strong>Recommendation:</strong>{" "}
                            {result.recommendation}
                        </p>
                    )}

                </div>

            )}

        </div>

    );
}

export default TextAnalysisForm;