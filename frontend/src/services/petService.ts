import { Pet } from '../types/pet';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001';

export const petService = {
  async getPetByUserId(userId: string): Promise<Pet | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/pets/user/${userId}`);
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error('Failed to fetch pet data');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching pet:', error);
      throw error;
    }
  },

  async createPet(userId: string, petData: Partial<Pet>): Promise<Pet> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/pets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...petData,
          userId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create pet');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating pet:', error);
      throw error;
    }
  },
}; 