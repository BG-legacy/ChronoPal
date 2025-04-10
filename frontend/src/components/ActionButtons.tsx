import React, { useState } from 'react';
import { PetAction } from '../types/pet';
import '../styles/RetroStyles.css';

interface ActionButtonsProps {
  onAction: (action: PetAction) => void;
  disabled: boolean;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({ onAction, disabled }) => {
  const [teachMessage, setTeachMessage] = useState('');

  const handleAction = (type: 'FEED' | 'PLAY' | 'TEACH') => {
    if (disabled) return;

    if (type === 'TEACH' && !teachMessage.trim()) {
      return;
    }

    onAction({
      type,
      message: type === 'TEACH' ? teachMessage : undefined
    });

    if (type === 'TEACH') {
      setTeachMessage('');
    }
  };

  return (
    <div className="action-buttons">
      <button
        className="retro-button action-button feed"
        onClick={() => handleAction('FEED')}
        disabled={disabled}
      >
        Feed
      </button>

      <button
        className="retro-button action-button play"
        onClick={() => handleAction('PLAY')}
        disabled={disabled}
      >
        Play
      </button>

      <div className="teach-action">
        <input
          type="text"
          value={teachMessage}
          onChange={(e) => setTeachMessage(e.target.value)}
          placeholder="What to teach?"
          className="retro-input"
          disabled={disabled}
        />
        <button
          className="retro-button action-button teach"
          onClick={() => handleAction('TEACH')}
          disabled={disabled || !teachMessage.trim()}
        >
          Teach
        </button>
      </div>
    </div>
  );
};

export default ActionButtons; 