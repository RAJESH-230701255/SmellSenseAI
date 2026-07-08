import { useState } from "react";
import api from "../api/api";
import "../styles/form.css";

function ExpiryDateForm() {

    const [productName, setProductName] = useState("");
    const [manufacturingDate, setManufacturingDate] = useState("");
    const [expiryDate, setExpiryDate] = useState("");

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleAnalyze = async () => {

        if (
            productName.trim() === "" ||
            manufacturingDate === "" ||
            expiryDate === ""
        ) {
            alert("Please fill all the fields.");
            return;
        }

        try {

            setLoading(true);

            const formData = new FormData();

            formData.append("product_name", productName);
            formData.append("manufacturing_date", manufacturingDate);
            formData.append("expiry_date", expiryDate);

            const response = await api.post("/predict-expiry", formData);

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

            <h2>Expiry Date Analysis</h2>

            <p>
                Enter the product details to analyze its freshness.
            </p>

            <input
                type="text"
                className="description-box"
                placeholder="Product Name (e.g. Milk)"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
            />

            <br /><br />

            <label>
                <strong>Manufacturing Date </strong>
            </label>

            <input
                type="date"
                className="description-box"
                value={manufacturingDate}
                onChange={(e) => setManufacturingDate(e.target.value)}
            />

            <br /><br />

            <label>
                <strong>Expiry Date </strong>
            </label>

            <input
                type="date"
                className="description-box"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
            />

            <br /><br />

            <button
                className="analyze-btn"
                onClick={handleAnalyze}
            >
                {loading ? "Analyzing..." : "Analyze"}
            </button>

            {result && (

                <div className="result-box">

                    <h3>Prediction Result</h3>

                    <p><strong>🧾 Product:</strong> {result.product}</p>

                    <p>
                        <strong>Status:</strong>{" "}
                        <span
                        style={{
                            color:
                                result.result === "Fresh"
                                    ? "green"
                                    : result.result === "Near Expiry"
                                    ? "orange"
                                    : "red",
                            fontWeight: "bold",
                            fontSize: "18px"
                        }}>
                        {result.result}
                        </span>
                    </p>

                    <p><strong>Freshness Score:</strong> {result.freshness_score}%</p>

                    <p><strong>Remaining Days:</strong> {result.remaining_days} day(s)</p>

                    <p><strong>Total Shelf Life:</strong> {result.total_shelf_life} day(s)</p>

                </div>

            )}

        </div>

    );

}

export default ExpiryDateForm;