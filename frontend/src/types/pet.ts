export type Mood = 'happy' | 'normal' | 'sad';
export type EvolutionStage = 'BABY' | 'CHILD' | 'TEEN' | 'ADULT';

export interface Pet {
  id: string;
  userId: string;
  name: string;
  species: string;
  level: number;
  experience: number;
  lastFed: string;
  lastPlayed: string;
  lastCleaned: string;
  evolution: EvolutionStage;
  mood: Mood;
  hunger: number;
  cleanliness: number;
  happiness: number;
  intelligence: number;
}

export interface PetAction {
  type: 'FEED' | 'PLAY' | 'TEACH';
  timestamp: Date;
} 