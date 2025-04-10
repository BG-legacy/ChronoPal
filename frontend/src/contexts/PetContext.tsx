import React, { createContext, useContext, useState, useEffect } from 'react';
import { Pet } from '../types/pet';
import { apiService } from '../services/apiService';

interface PetContextType {
  pet: Pet | null;
  loading: boolean;
  error: Error | null;
  refreshPet: () => Promise<void>;
  createPet: (petData: Omit<Pet, 'id' | 'userId'>) => Promise<void>;
}

const PetContext = createContext<PetContextType | undefined>(undefined);

export const PetProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [pet, setPet] = useState<Pet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchPet = async () => {
    try {
      setLoading(true);
      setError(null);
      const petData = await apiService.getUserPet();
      setPet(petData);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch pet'));
    } finally {
      setLoading(false);
    }
  };

  const createPet = async (petData: Omit<Pet, 'id' | 'userId'>) => {
    try {
      setLoading(true);
      setError(null);
      const now = new Date().toISOString();
      const newPet: Pet = {
        ...petData,
        id: Date.now().toString(),
        userId: 'default',
        species: 'Digital',
        mood: 'happy',
        level: 1,
        sass_level: 1,
        lastFed: now,
        lastInteraction: now,
        interactionCount: 0,
        memoryLog: []
      };
      const savedPet = await apiService.savePet(newPet);
      setPet(savedPet);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to create pet'));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPet();
  }, []);

  return (
    <PetContext.Provider value={{ pet, loading, error, refreshPet: fetchPet, createPet }}>
      {children}
    </PetContext.Provider>
  );
};

export const usePet = () => {
  const context = useContext(PetContext);
  if (context === undefined) {
    throw new Error('usePet must be used within a PetProvider');
  }
  return context;
}; 