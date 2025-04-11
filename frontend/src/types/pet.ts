export interface Pet {
  id?: string;  // Optional to handle cases where MongoDB returns _id instead
  _id?: string; // MongoDB's default ID field
  name: string;
  species: string;
  mood: string;
  level: number;
  sassLevel: number;
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