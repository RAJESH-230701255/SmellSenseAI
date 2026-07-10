import { useState } from "react";
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

            const response = await fetch("/api/predict-text", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: text
                })
            });

            const data = await response.json();

            if (!response.ok) {
                console.error("Prediction error:", data);
                throw new Error(data.error || "Prediction failed");
            }

            setResult(data);

        } catch (err) {

            console.error("Text analysis error:", err);
            alert("Prediction Failed: " + err.message);

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