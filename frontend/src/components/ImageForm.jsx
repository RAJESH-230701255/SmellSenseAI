import { FaCloudUploadAlt } from "react-icons/fa";
import { useRef, useState } from "react";
import "../styles/form.css";
import api from "../api/api";

function ImageForm() {

    const fileInputRef = useRef(null);

    const [fileName, setFileName] = useState("");
    const [preview, setPreview] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleClick = () => {
        fileInputRef.current.click();
    };

    const handleFile = (e) => {

    const file = e.target.files[0];

    if(file){

        setSelectedFile(file);
        setFileName(file.name);
        setPreview(URL.createObjectURL(file));

    }

    };

    const handleAnalyze = async () => {

    if (!selectedFile) {
        alert("Please select an image first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {

        setLoading(true);

        const response = await api.post("/predict", formData);

        setResult(response.data);

    } catch (error) {

        console.error(error);
        alert("Prediction failed.");

    } finally {

        setLoading(false);

    }
    };

    return (

        <div className="form-container">

            <h2>Image Analysis</h2>

            <p>
                Upload a food image and let AI determine its freshness.
            </p>

            <div
                className="upload-box"
                onClick={handleClick}
            >

                <FaCloudUploadAlt className="upload-icon"/>

                <h3>Drag & Drop Image</h3>

                <span>or Click to Browse</span>

                <small>PNG • JPG • JPEG</small>

                <input
                    type="file"
                    accept="image/*"
                    ref={fileInputRef}
                    onChange={handleFile}
                    hidden
                />

            </div>

            {

preview &&

<div className="preview-box">

    <img

        src={preview}

        alt="preview"

    />

</div>

}

<div className="selected-file">

    {

        fileName

        ?

        <>✅ {fileName}</>

        :

        <>No image selected</>

    }

        </div>

            <button className="analyze-btn" onClick={handleAnalyze}>
                {loading ? "Analyzing..." : "Analyze Image"}

            </button>

            {
    result && (

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

    )
}

        </div>

    );

}

export default ImageForm;