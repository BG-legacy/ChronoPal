import React from 'react';
import { Link } from 'react-router-dom';

const Rules: React.FC = () => {
  return (
    <div className="retro-container text-center">
      <div className="retro-panel p-4">
        <h2 className="retro-title text-3xl mb-4">ChronoPal Rules</h2>
        <p>Welcome to ChronoPal! Please read and follow these rules to ensure a fun and safe experience for everyone.</p>
        <ul className="list-disc list-inside mt-4">
          <li><strong>Be Respectful:</strong> Avoid using offensive language or behaving inappropriately.</li>
          <li><strong>No Cheating:</strong> Do not use exploits, hacks, or third-party software to gain unfair advantages.</li>
          <li><strong>Protect Your Account:</strong> Never share your password. Be cautious of phishing attempts or suspicious links.</li>
          <li><strong>Respect Your Pets:</strong> Everyone should feel welcome in the community.</li>
          <li><strong>Follow the Law:</strong> Do not share or engage in illegal activities. Respect intellectual property and others' privacy.</li>
          <li><strong>Have Fun:</strong> Enjoy raising your virtual pets, interacting with the community, and exploring all that ChronoPal has to offer!</li>
        </ul>
        <img 
          src="https://www.cameronsworld.net/img/content/23/frame-3/1.gif" 
          alt="Rules Decoration"
          className="mx-auto mt-4"
          style={{ imageRendering: 'pixelated' }}
        />
      </div>

      {/* Back Button */}
      <div className="mt-6">
        <Link to="/" className="retro-link">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
};

export default Rules;
