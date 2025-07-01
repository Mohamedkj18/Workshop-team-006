import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import './styles/Home.css';

export default function Home() {
  useScrollFadeIn();

  return (
    <>
      <Header />
      <main className="home-main">
        <section className="hero visible">
          <div className="container center-text">
            <h1>Welcome to <span className="highlight">LazyMail</span></h1>
            <p className="subtitle">
              Your intelligent email assistant that learns your style and replies for you.
            </p>
            <Link to="/signup" className="btn get-started-btn">Get Started</Link>
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">About Us</h2>
          <div className="container section-row">
            <div className="text">
              <p>
                LazyMail is your personal writing assistant designed to help you communicate faster
                without sacrificing authenticity. Whether you’re managing a team, a classroom, or just
                trying to stay sane in your inbox, LazyMail learns your style and takes care of replies.
              </p>
            </div>
            <img src="/placeholder-about.png" alt="About Screenshot" className="image" />
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">📝 AI Replies</h2>
          <div className="container section-row reverse">
            <div className="text">
              <p>
                Say goodbye to repetitive writing. LazyMail drafts replies that sound like you
                tailored to your tone, structure, and intent.
              </p>
            </div>
            <img src="/placeholder-ai-replies.png" alt="AI Replies Screenshot" className="image" />
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">📚 Learns Your Style</h2>
          <div className="container section-row">
            <div className="text">
              <p>
                Upload past email threads and let LazyMail learn how you communicate from phrasing to punctuation.
                The more you use it, the better it gets at sounding like you.
              </p>
            </div>
            <img src="/placeholder-style-learning.png" alt="Style Learning Screenshot" className="image" />
          </div>
        </section>

        <section className="section">
          <h2 className="section-title">📁 Smart Drafts & Workflow</h2>
          <div className="container section-row reverse">
            <div className="text">
              <p>
                Review, edit, approve, or send all from one clean interface. LazyMail blends AI assistance
                with your own voice and final control.
              </p>
            </div>
            <img src="/placeholder-drafts.png" alt="Drafts Screenshot" className="image" />
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} LazyMail All rights reserved.</p>
      </footer>
    </>
  );
}

function useScrollFadeIn() {
  useEffect(() => {
    const reveal = () => {
      document.querySelectorAll(".section").forEach((sec) => {
        const top = sec.getBoundingClientRect().top;
        if (top < window.innerHeight - 100) {
          sec.classList.add("visible");
        }
      });
    };

    window.addEventListener("scroll", reveal);
    reveal();
    return () => window.removeEventListener("scroll", reveal);
  }, []);
}
