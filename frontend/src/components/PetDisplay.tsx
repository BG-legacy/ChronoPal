import React from 'react';
import { Pet } from '../types/pet';
import '../styles/RetroStyles.css';

interface PetDisplayProps {
  pet: Pet;
  isFeeding: boolean;
  isPlaying: boolean;
  isTeaching: boolean;
}

const PetDisplay: React.FC<PetDisplayProps> = ({ pet, isFeeding, isPlaying, isTeaching }) => {
  const getMoodEmoji = (mood: string) => {
    switch (mood.toLowerCase()) {
      case 'happy':
        return '😊';
      case 'content':
        return '😌';
      case 'neutral':
        return '😐';
      case 'grumpy':
        return '😠';
      case 'angry':
        return '😡';
      default:
        return '😊';
    }
  };

  const getSassEmoji = (sassLevel: number) => {
    switch (sassLevel) {
      case 1:
        return '😇';
      case 2:
        return '😋';
      case 3:
        return '😏';
      case 4:
        return '😒';
      case 5:
        return '😈';
      default:
        return '😇';
    }
  };

  return (
    <div className="pet-display">
      <div className="pet-info">
        <h2 className="retro-title">{pet.name}</h2>
        <div className="pet-stats">
          <div className="stat-row">
            <span className="stat-label">Species:</span>
            <span className="stat-value">{pet.species}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Level:</span>
            <span className="stat-value">{pet.level}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Mood:</span>
            <span className="stat-value">
              {getMoodEmoji(pet.mood)} {pet.mood}
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Sass Level:</span>
            <span className="stat-value">
              {getSassEmoji(pet.sass_level)} {pet.sass_level}
            </span>
          </div>
        </div>
      </div>

      <div className={`pet-animation ${isFeeding ? 'feeding' : ''} ${isPlaying ? 'playing' : ''} ${isTeaching ? 'teaching' : ''}`}>
        <div className="pet-sprite">
          {/* Pet sprite will be rendered here */}
          <div className="pet-eyes">
            <div className="eye left"></div>
            <div className="eye right"></div>
          </div>
          <div className="pet-mouth"></div>
        </div>
      </div>

      <div className="pet-memory">
        <h3 className="retro-subtitle">Recent Memories</h3>
        <div className="memory-log">
          {pet.memoryLog.slice(-3).map((memory, index) => (
            <div key={index} className="memory-item">
              {memory}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PetDisplay; 