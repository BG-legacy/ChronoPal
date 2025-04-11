import React from 'react';
import { Link } from 'react-router-dom';

const Privacy: React.FC = () => {
  return (
    <div className="retro-container text-center">
      <div className="retro-panel p-4">
        <h2 className="retro-title text-3xl mb-4">Privacy Policy</h2>
        <p>
          At ChronoPal, we are committed to protecting your privacy and ensuring a safe online experience. We take your personal
          information seriously and strive to maintain the highest standards of privacy and security.
        </p>
        <p>
          Please note that prompts and user interactions may be saved to ensure more accurate responses from the system and to
          enhance the overall experience. These saved prompts help improve the AI and allow us to provide you with more
          personalized responses.
        </p>
        <p>
          We do not share or sell any personal information to third parties. Your data is securely stored and used only for
          improving your experience with ChronoPal.
        </p>

        <img 
          src="https://www.cameronsworld.net/img/content/23/frame-3/1.gif" 
          alt="Privacy Decoration"
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

export default Privacy;
