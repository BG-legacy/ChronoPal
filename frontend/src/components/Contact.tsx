import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/RetroStyles.css';
import linkedinIcon from '../assets/linkedin-icon.png';
import catDivider from '../assets/cat-icon.gif'; //pulled from Camerons World

const teamMembers = [
  {
    name: "Carnell Greenfield",
    description: "Frontend wizard passionate about playful UX, nostalgia and interface magic. Makes retro cool again.",
    linkedin: "https://www.linkedin.com/in/carnell-greenfield/",
  },
  {
    name: "Bernard Ginn Jr.",
    description: "Creative backend engineer and game logic master. Breathes life into digital pets with clean code.",
    linkedin: "https://www.linkedin.com/in/bernard-ginn-jr/",
  },
  {
    name: "Destiny Butler",
    description: "AI systems thinker and storyteller. Weaves narrative into tech for deeper connections.",
    linkedin: "https://www.linkedin.com/in/destiny-butler-6491a2325/",
  }
];

const About: React.FC = () => {
  return (
    <div className="retro-container">
      <div className="retro-panel text-center">
        <h1 className="retro-title text-2xl mb-6">Meet the ChronoPal Team</h1>
        <div className="space-y-10">
          {teamMembers.map((member, index) => (
            <div key={member.name}>
              <div className="flex items-center justify-center space-x-4">
                <a href={member.linkedin} target="_blank" rel="noopener noreferrer">
                  <img src={linkedinIcon} alt={`${member.name}'s LinkedIn`} width={40} height={40} />
                </a>
                <div className="text-left">
                  <p className="text-lg font-bold">{member.name}</p>
                  <p>{member.description}</p>
                </div>
              </div>
              {index < teamMembers.length - 1 && (
                <div className="my-4">
                  <img src={catDivider} alt="Divider Cat GIF" className="mx-auto" />
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-6">
          <Link to="/" className="retro-link">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
};

export default About;
