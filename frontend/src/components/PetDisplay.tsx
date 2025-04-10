import React from 'react';
import { Pet, Mood, EvolutionStage } from '../types/pet';
import { PET_SPRITES } from '../assets/pet-sprites';

interface PetDisplayProps {
  pet: Pet;
}

const PetDisplay: React.FC<PetDisplayProps> = ({ pet }) => {
  // Get the appropriate sprite based on pet's evolution stage and mood
  const getSprite = (evolution: EvolutionStage, mood: Mood) => {
    return PET_SPRITES[evolution][mood];
  };

  // Calculate level progress percentage
  const levelProgress = (pet.level % 10) * 10; // Assuming 10 levels per evolution stage

  return (
    <div className="flex flex-col items-center">
      {/* Pet sprite */}
      <div className="w-32 h-32 mb-4 animate-pet-float">
        <img 
          src={getSprite(pet.evolution, pet.mood)} 
          alt={`${pet.name} - ${pet.evolution} ${pet.mood}`}
          className="w-full h-full object-contain"
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