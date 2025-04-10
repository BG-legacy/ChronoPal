import { useState, useCallback, useEffect } from 'react';
import { playSound, setVolume, setMuted, isMuted, SoundType } from './soundService';

interface UseSoundsReturn {
  playSound: (type: SoundType) => void;
  volume: number;
  setVolume: (volume: number) => void;
  muted: boolean;
  toggleMute: () => void;
}

export const useSounds = (): UseSoundsReturn => {
  const [volume, setVolumeState] = useState(0.5);
  const [muted, setMutedState] = useState(false);

  // Initialize mute state
  useEffect(() => {
    setMutedState(isMuted());
  }, []);

  const handlePlaySound = useCallback((type: SoundType) => {
    playSound(type);
  }, []);

  const handleSetVolume = useCallback((newVolume: number) => {
    setVolumeState(newVolume);
    setVolume(newVolume);
  }, []);

  const handleToggleMute = useCallback(() => {
    const newMutedState = !muted;
    setMutedState(newMutedState);
    setMuted(newMutedState);
  }, [muted]);

  return {
    playSound: handlePlaySound,
    volume,
    setVolume: handleSetVolume,
    muted,
    toggleMute: handleToggleMute
  };
};

export default useSounds; 