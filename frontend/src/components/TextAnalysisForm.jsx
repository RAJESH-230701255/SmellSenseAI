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

            const formData = new FormData();
            formData.append("text", text);

            const response = await api.post("/predict", formData);

            setResult(response.data);

        } catch (err) {

            console.error(err);
            alert("Prediction Failed");

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
                        <strong>Confidence:</strong> {result.confidence}
                    </p>

                    <p>
                        <strong>Score:</strong> {result.score}
                    </p>

                    <p>
                        <strong>Recommendation:</strong> {result.recommendation}
                    </p>

                </div>

            )}

        </div>

    );
}

export default TextAnalysisForm;