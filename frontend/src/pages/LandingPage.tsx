import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <main className="landing-page">
      <section className="hero">
        <p className="eyebrow">A probability-powered board game</p>

        <h1>
          Camel Up
          <span> Strategy Lab</span>
        </h1>

        <p className="hero-description">
          Race across the desert while an exact probability engine
          evaluates every available betting decision.
        </p>

        <div className="hero-actions">
          <Link className="primary-button" to="/setup">
            Start a new game
          </Link>

          <a className="secondary-button" href="#features">
            Explore the engine
          </a>
        </div>
      </section>

      <section className="feature-grid" id="features">
        <article className="feature-card">
          <span className="feature-number">01</span>
          <h2>Exact probabilities</h2>
          <p>
            Analyze possible remaining dice sequences instead of
            relying only on random simulation.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-number">02</span>
          <h2>Expected-value advice</h2>
          <p>
            Compare available betting tickets using their current
            probability-weighted value.
          </p>
        </article>

        <article className="feature-card">
          <span className="feature-number">03</span>
          <h2>Interactive game state</h2>
          <p>
            Roll dice, place bets, track camel stacks, and watch each
            leg evolve in real time.
          </p>
        </article>
      </section>
    </main>
  );
}