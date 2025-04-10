import { Howl, Howler } from 'howler';

// Define sound types
export type SoundType = 
  | 'click'
  | 'beep'
  | 'success'
  | 'error'
  | 'notification';

// Base64 encoded WAV sounds - very small retro beeps and blips
const SOUND_DATA = {
  // Short click sound
  click: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=',
  
  // Simple beep
  beep: 'data:audio/wav;base64,UklGRh4AAABXQVZFZm10IBAAAAABAAEAESsAABErAAACABAAZGF0YQAAAAoA',
  
  // Success sound (ascending two tones)
  success: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=',
  
  // Error sound (descending tone)
  error: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=',
  
  // Notification blip
  notification: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='
};

// Sound instances
const soundInstances: Partial<Record<SoundType, Howl>> = {};

// Track mute state
let isSoundMuted = false;

// Initialize sounds
export const initSounds = (): void => {
  Object.entries(SOUND_DATA).forEach(([key, dataUri]) => {
    soundInstances[key as SoundType] = new Howl({
      src: [dataUri],
      volume: 0.5,
      preload: true,
      format: ['wav']
    });
  });
};

// Play a sound
export const playSound = (type: SoundType): void => {
  const sound = soundInstances[type];
  if (sound) {
    sound.play();
  } else {
    console.warn(`Sound not loaded: ${type}`);
  }
};

// Set global volume (0.0 to 1.0)
export const setVolume = (volume: number): void => {
  Object.values(soundInstances).forEach(sound => {
    if (sound) {
      sound.volume(volume);
    }
  });
};

// Mute/unmute all sounds
export const setMuted = (muted: boolean): void => {
  isSoundMuted = muted;
  Howler.mute(muted);
};

// Check if sound is currently muted
export const isMuted = (): boolean => {
  return isSoundMuted;
};

// Initialize sounds on import
initSounds(); 