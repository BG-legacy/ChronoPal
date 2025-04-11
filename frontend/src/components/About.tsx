import React from 'react';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <div className="retro-container text-center">
      <div className="retro-panel p-4">
        <h2 className="retro-title text-3xl mb-4">About ChronoPal</h2>
        <p>
          ChronoPal is a retro-futuristic virtual pet simulator powered by AI. Inspired by Tamagotchi, Digimon, Pokémon,
          and the Spore Creature Creator, it lets you raise, evolve, and bond with your own custom creatures online!
        </p>
        <img 
          src="https://www.cameronsworld.net/img/content/23/frame-3/1.gif" 
          alt="Retro Decoration"
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

export default About;
