import "../styles/cards.css";
import { FaArrowRight } from "react-icons/fa";

function AnalysisCard({ icon, title, description, onClick }) {
  return (
    <div className="analysis-card" onClick={onClick}>

      <div className="card-icon">
        {icon}
      </div>

      <h2>{title}</h2>

      <p>{description}</p>

      <div className="card-footer">

        <span>Click anywhere</span>

        <FaArrowRight className="arrow"/>

      </div>

    </div>
  );
}

export default AnalysisCard;