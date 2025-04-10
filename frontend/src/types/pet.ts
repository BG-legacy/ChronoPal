export interface Pet {
  id: string;
  name: string;
  species: string;
  mood: string;
  level: number;
  sass_level: number;
  userId: string;
  lastFed: string;
  lastInteraction: string;
  interactionCount: number;
  memoryLog: string[];
}

export type PetAction = {
  type: 'FEED' | 'PLAY' | 'TEACH';
  message?: string;
}; 