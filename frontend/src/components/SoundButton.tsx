import React, { ButtonHTMLAttributes } from 'react';
import { playSound, SoundType } from '../assets/sounds/soundService';

interface SoundButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  soundType?: SoundType;
  children: React.ReactNode;
}

const SoundButton: React.FC<SoundButtonProps> = ({
  soundType = 'click',
  onClick,
  children,
  ...props
}) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    // Play the sound
    playSound(soundType);
    
    // Call the original onClick if provided
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <button
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default SoundButton; 