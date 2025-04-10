import React, { useState, useEffect } from 'react';
import { Pet, Mood, EvolutionStage } from '../types/pet';
import catPixelArt from '../assets/petlog.png';

interface PetDisplayProps {
  pet: Pet;
  isFeeding?: boolean;
  isPlaying?: boolean;
  isTeaching?: boolean;
}

const PetDisplay: React.FC<PetDisplayProps> = ({ 
  pet, 
  isFeeding = false, 
  isPlaying = false,
  isTeaching = false 
}) => {
  const [isEating, setIsEating] = useState(false);
  const [isPlayingAnim, setIsPlayingAnim] = useState(false);
  const [isLearning, setIsLearning] = useState(false);
  const [playCount, setPlayCount] = useState(0);
  const [teachCount, setTeachCount] = useState(0);

  useEffect(() => {
    if (isFeeding) {
      setIsEating(true);
      const timer = setTimeout(() => {
        setIsEating(false);
      }, 500); // Match animation duration
      return () => clearTimeout(timer);
    }
  }, [isFeeding]);

  useEffect(() => {
    if (isPlaying) {
      setIsPlayingAnim(true);
      setPlayCount(3); // Play animation 3 times
      
      const playTimer = setInterval(() => {
        setPlayCount(prev => {
          if (prev <= 1) {
            clearInterval(playTimer);
            setIsPlayingAnim(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000); // Each animation is 1s

      return () => {
        clearInterval(playTimer);
        setIsPlayingAnim(false);
        setPlayCount(0);
      };
    }
  }, [isPlaying]);

  useEffect(() => {
    if (isTeaching) {
      setIsLearning(true);
      setTeachCount(2); // Teaching animation 2 times
      
      const teachTimer = setInterval(() => {
        setTeachCount(prev => {
          if (prev <= 1) {
            clearInterval(teachTimer);
            setIsLearning(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000); // Each animation is 1s

      return () => {
        clearInterval(teachTimer);
        setIsLearning(false);
        setTeachCount(0);
      };
    }
  }, [isTeaching]);

  // Calculate level progress percentage
  const levelProgress = (pet.level % 10) * 10; // Assuming 10 levels per evolution stage

  const getAnimation = () => {
    if (isEating) return 'animate-pet-eating';
    if (isPlayingAnim) return 'animate-pet-playing';
    if (isLearning) return 'animate-pet-teaching';
    return 'animate-pet-float';
  };

  const getIterationCount = () => {
    if (isPlayingAnim) return playCount;
    if (isLearning) return teachCount;
    if (isEating) return 1;
    return 'infinite';
  };

  return (
    <div className="flex flex-col items-center">
      {/* Pet sprite */}
      <div 
        className={`w-20 h-20 mb-4 ${getAnimation()}`}
        style={{
          animationIterationCount: getIterationCount()
        }}
      >
        <img 
          src={catPixelArt} 
          alt={`${pet.name} - ${pet.evolution} ${pet.mood}`}
          className="w-full h-full object-contain pixelated"
          style={{
            imageRendering: 'pixelated',
            transform: `scale(1.2)`,
          }}
        />
      </div>

      {/* Pet info */}
      <div className="bg-gray-800 p-4 rounded-lg border border-green-500 w-full max-w-xs text-white font-pixel">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-green-400">{pet.name}</h2>
          <span className="text-yellow-400">Lvl {pet.level}</span>
        </div>

        <div className="mb-2">
          <p className="text-xs text-gray-300">Evolution: {pet.evolution}</p>
          <p className="text-xs text-gray-300">Mood: {pet.mood}</p>
        </div>

        {/* Stats */}
        <div className="space-y-2 text-xs">
          <div>
            <div className="flex justify-between">
              <span>Level Progress</span>
              <span>{levelProgress}%</span>
            </div>
            <div className="h-2 bg-gray-700 rounded overflow-hidden">
              <div 
                className="h-full bg-blue-500" 
                style={{ width: `${levelProgress}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between">
              <span>Hunger</span>
              <span>{pet.hunger}/100</span>
            </div>
            <div className="h-2 bg-gray-700 rounded overflow-hidden">
              <div 
                className="h-full bg-green-500" 
                style={{ width: `${pet.hunger}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between">
              <span>Happiness</span>
              <span>{pet.happiness}/100</span>
            </div>
            <div className="h-2 bg-gray-700 rounded overflow-hidden">
              <div 
                className="h-full bg-yellow-500" 
                style={{ width: `${pet.happiness}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between">
              <span>Intelligence</span>
              <span>{pet.intelligence}/100</span>
            </div>
            <div className="h-2 bg-gray-700 rounded overflow-hidden">
              <div 
                className="h-full bg-purple-500" 
                style={{ width: `${pet.intelligence}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PetDisplay; 