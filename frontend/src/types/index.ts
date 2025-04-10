export interface User {
  id: string;
  email: string;
  username: string;
  createdAt: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Pet {
  id: string;
  userId: string;
  name: string;
  species: string;
  level: number;
  mood: string;
  lastFed: string;
  lastPlayed: string;
  interactionCount: number;
  memories: string[];
  sass_level: number;
  createdAt: string;
  updatedAt: string;
} 