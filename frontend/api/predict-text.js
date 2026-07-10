export default async function handler(req, res) {
  // Allow only POST requests
  if (req.method !== "POST") {
    return res.status(405).json({
      error: "Method not allowed. Use POST.",
    });
  }

  try {
    const { text } = req.body;

    // Check if text is provided
    if (!text || !text.trim()) {
      return res.status(400).json({
        error: "Please provide text for analysis.",
      });
    }

    // Get Hugging Face token from Vercel environment variables
    const HF_TOKEN = process.env.HF_TOKEN;

    if (!HF_TOKEN) {
      console.error("HF_TOKEN is missing");

      return res.status(500).json({
        error: "Hugging Face token is not configured.",
      });
    }

    // Your Hugging Face DistilBERT model
    const API_URL =
      "https://api-inference.huggingface.co/models/Rajesh282002/smellsense-distilbert";

    // Call Hugging Face Inference API
    const response = await fetch(API_URL, {
      method: "POST",

      headers: {
        Authorization: `Bearer ${HF_TOKEN}`,
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        inputs: text,
      }),
    });

    // Read response
    const data = await response.json();

    // Handle Hugging Face errors
    if (!response.ok) {
      console.error("Hugging Face API Error:", data);

      return res.status(response.status).json({
        error: "Hugging Face inference failed.",
        details: data,
      });
    }

    console.log("Hugging Face response:", data);

    // Hugging Face may return:
    // [[{ label: "LABEL_0", score: 0.95 }, ...]]
    // or [{ label: "LABEL_0", score: 0.95 }]
    let prediction;

    if (Array.isArray(data[0])) {
      prediction = data[0][0];
    } else {
      prediction = data[0];
    }

    if (!prediction || !prediction.label) {
      return res.status(500).json({
        error: "Invalid prediction response from Hugging Face.",
        details: data,
      });
    }

    // Convert model label to readable result
    let result;

    if (prediction.label === "LABEL_0") {
      result = "Fresh";
    } else {
      result = "Spoiled";
    }

    const confidence = prediction.score * 100;

    // Send final result to React frontend
    return res.status(200).json({
      result: result,
      confidence: Number(confidence.toFixed(2)),
      score: Number(confidence.toFixed(2)),
    });
  } catch (error) {
    console.error("Text prediction error:", error);

    return res.status(500).json({
      error: "Text prediction failed.",
      details: error.message,
    });
  }
}