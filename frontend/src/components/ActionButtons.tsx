import React from 'react';
import { PetAction } from '../types/pet';

interface ActionButtonsProps {
  onAction: (action: PetAction) => void;
  disabled?: boolean;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({ onAction, disabled = false }) => {
  const handleAction = (type: 'FEED' | 'PLAY' | 'TEACH') => {
    onAction({
      type,
      timestamp: new Date()
    });
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3 mt-6 w-full max-w-xs">
      <button
        onClick={() => handleAction('FEED')}
        disabled={disabled}
        className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-pixel py-3 px-4 rounded-lg border-b-4 border-green-800 active:border-b-0 active:mt-1 transition-all"
      >
        <div className="flex flex-col items-center">
          <span className="text-2xl">🍔</span>
          <span>Feed</span>
        </div>
      </button>
      
      <button
        onClick={() => handleAction('PLAY')}
        disabled={disabled}
        className="flex-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-pixel py-3 px-4 rounded-lg border-b-4 border-yellow-800 active:border-b-0 active:mt-1 transition-all"
      >
        <div className="flex flex-col items-center">
          <span className="text-2xl">🎮</span>
          <span>Play</span>
        </div>
      </button>
      
      <button
        onClick={() => handleAction('TEACH')}
        disabled={disabled}
        className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-pixel py-3 px-4 rounded-lg border-b-4 border-purple-800 active:border-b-0 active:mt-1 transition-all"
      >
        <div className="flex flex-col items-center">
          <span className="text-2xl">📚</span>
          <span>Teach</span>
        </div>
      </button>
    </div>
  );
};

export default ActionButtons; 