import { useState } from "react";
import AnalysisCard from "./AnalysisCard";
import ImageForm from "./ImageForm";
import TextAnalysisForm from "./TextAnalysisForm";
import ExpiryDateForm from "./ExpiryDateForm";

import "../styles/cards.css";

import { FaCamera, FaCalendarAlt } from "react-icons/fa";
import { BsFileTextFill } from "react-icons/bs";

function FeatureSection() {

    const [selected, setSelected] = useState(null);

    return (

        <section className="feature-section">

            <h1>Choose Your Analysis Method</h1>

            <p className="feature-subtitle">
                Select one of the AI-powered freshness analysis methods.
            </p>

            <div className="workspace">

                {/* LEFT PANEL */}

                <div className="left-panel">

                    <AnalysisCard
                        icon={<FaCamera />}
                        title="Image Analysis"
                        description="Analyze food images."
                        onClick={() => setSelected("image")}
                    />

                    <AnalysisCard
                        icon={<BsFileTextFill />}
                        title="Text Analysis"
                        description="Predict freshness from a text description."
                        onClick={() => setSelected("text")}
                    />

                    <AnalysisCard
                        icon={<FaCalendarAlt />}
                        title="Expiry Date"
                        description="Check product expiry."
                        onClick={() => setSelected("expiry")}
                    />

                </div>

                {/* RIGHT PANEL */}

                <div className="right-panel">

                    {!selected && (

                        <div className="placeholder">

                            <h2>Select an Analysis Method</h2>

                            <p>
                                Click any card on the left to begin.
                            </p>

                        </div>

                    )}

                    {selected === "image" && (
                        <ImageForm />
                    )}

                    {selected === "text" && (
                        <TextAnalysisForm />
                    )}

                    {selected === "expiry" && (
                        <ExpiryDateForm />
                    )}

                </div>

            </div>

        </section>

    );

}

export default FeatureSection;