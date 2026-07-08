import "../styles/hero.css";
import heroCartoon from "../assets/cartoon.png";

function Hero(){

    return(

        <section className="hero">

            <div className="hero-left">

                <h1>

                    AI Powered

                    <br/>

                    Food Freshness

                    <br/>

                    Detection

                </h1>

                <p>

                    Detect food freshness using Computer Vision,

                    Deep Learning and Intelligent AI.

                </p>

            </div>

            <div className="hero-right">
                <img
                    src={heroCartoon}
                    alt="AI Food Freshness"
                    className="hero-cartoon"
                />
            </div>

        </section>

    );

}

export default Hero;