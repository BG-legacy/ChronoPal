import axios from 'axios';
import { Pet } from '../types/pet';
import { User } from '../types/user';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface InteractionRequest {
  pet_id: string;
  interaction_type: string;
  message?: string;
}

interface ChatRequest {
  message: string;
  pet_id: string;
}

interface LoginResponse {
  session_id: string;
  user: User;
}

interface ChatResponse {
  response: string;
}

class ApiService {
  private static instance: ApiService;
  private sessionId: string | null = null;

  private constructor() {
    this.sessionId = localStorage.getItem('sessionId');
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private get headers() {
    if (!this.sessionId) {
      throw new Error('No session ID found. Please log in.');
    }
    return {
      'Content-Type': 'application/json',
      'session-id': this.sessionId
    };
  }

  public setSessionId(sessionId: string) {
    this.sessionId = sessionId;
    localStorage.setItem('sessionId', sessionId);
  }

  public clearSession() {
    this.sessionId = null;
    localStorage.removeItem('sessionId');
  }

  public forceSessionRefresh() {
    const sessionId = localStorage.getItem('sessionId');
    if (sessionId) {
      this.sessionId = sessionId;
      console.log('Session refreshed from localStorage:', sessionId.substring(0, 8) + '...');
    } else {
      this.clearSession();
      window.location.href = '/login';
    }
  }

  private async getCorrectPetId(): Promise<string> {
    try {
      const pet = await this.getUserPet();
      if (pet && pet.id) {
        localStorage.setItem('currentPetId', pet.id);
        return pet.id;
      }
      
      const storedId = localStorage.getItem('currentPetId');
      if (storedId) {
        return storedId;
      }
      
      throw new Error('No valid pet ID available');
    } catch (error) {
      const storedId = localStorage.getItem('currentPetId');
      if (storedId) {
        return storedId;
      }
      throw new Error('Could not get valid pet ID');
    }
  }

  public async register(email: string, password: string, username: string): Promise<User> {
    const response = await axios.post<User>(`${API_BASE_URL}/api/register`, {
      email,
      password,
      username
    });
    return response.data;
  }

  public async login(email: string, password: string): Promise<LoginResponse> {
    try {
      console.log(`[apiService] Attempting login for email: ${email}`);
      
      const response = await axios.post<LoginResponse>(`${API_BASE_URL}/api/login`, {
        email,
        password
      });
      
      console.log(`[apiService] Login successful, received session ID: ${response.data.session_id.substring(0, 8)}...`);
      this.setSessionId(response.data.session_id);
      
      return response.data;
    } catch (error: any) {
      console.error('[apiService] Login failed:', error);
      throw error;
    }
  }

  public async logout(): Promise<void> {
    try {
      await axios.post(`${API_BASE_URL}/api/logout`, null, {
        headers: this.headers
      });
    } finally {
      this.clearSession();
    }
  }

  public async getUserPet(): Promise<Pet> {
    try {
      console.log('Requesting pet data from API...');
      const response = await axios.get<any>(`${API_BASE_URL}/api/fixed-pet`, {
        headers: this.headers
      });
      console.log('API response for user-pet:', JSON.stringify(response.data, null, 2));
      
      // Check if the response has valid pet data
      const petData = response.data;
      if (!petData) {
        console.error('API returned empty pet data');
        throw new Error('No pet data received from server');
      }
      
      // Normalize MongoDB _id to id if needed
      let normalizedPetData: Pet = { ...petData };
      
      if (!normalizedPetData.id && petData._id) {
        console.log('Normalizing MongoDB _id to id field:', petData._id);
        normalizedPetData.id = petData._id;
      }
      
      if (!normalizedPetData.id) {
        console.error('API returned pet without ID:', petData);
        throw new Error('Pet ID is missing in server response');
      }
      
      return normalizedPetData;
    } catch (error: any) {
      console.error('getUserPet error details:', error);
      if (error.response) {
        console.error('API error response:', error.response.status, error.response.data);
      }
      
      if (error.response?.status === 401) {
        this.clearSession();
        throw new Error('Session expired. Please log in again.');
      }
      throw error;
    }
  }

  public async updateInteraction(request: InteractionRequest): Promise<Pet> {
    try {
      console.log('[apiService] updateInteraction request:', JSON.stringify(request, null, 2));
      
      if (!request.interaction_type) {
        console.error('[apiService] Missing interaction_type in request:', request);
        throw new Error('Interaction type is required');
      }
      
      let response;
      
      // Use the specific by-user endpoints based on interaction type
      switch (request.interaction_type.toLowerCase()) {
        case 'feed':
          console.log('[apiService] Sending feed request');
          response = await axios.post<any>(`${API_BASE_URL}/api/feed-pet-by-user`, null, {
            headers: this.headers
          });
          break;
          
        case 'play':
          console.log('[apiService] Sending play request');
          response = await axios.post<any>(`${API_BASE_URL}/api/play-with-pet-by-user`, null, {
            headers: this.headers
          });
          break;
          
        case 'teach':
          if (!request.message) {
            throw new Error('Message is required for teach interactions');
          }
          
          console.log('[apiService] Sending teach request');
          response = await axios.post<any>(`${API_BASE_URL}/api/teach-pet-by-user`, {
            message: request.message
          }, {
            headers: this.headers
          });
          break;
          
        default:
          throw new Error(`Unsupported interaction type: ${request.interaction_type}`);
      }
      
      console.log('[apiService] Interaction response:', response.data);
      
      // Normalize MongoDB _id to id if needed
      let petData = response.data;
      
      if (!petData.id && petData._id) {
        console.log('[apiService] Normalizing MongoDB _id to id field in response:', petData._id);
        petData = {
          ...petData,
          id: petData._id
        };
      }
      
      return petData;
    } catch (error: any) {
      console.error('[apiService] Error in updateInteraction:', error);
      
      if (error.response) {
        console.error('[apiService] Response error data:', error.response.data);
        console.error('[apiService] Response error status:', error.response.status);
      }
      
      if (error.response?.status === 401) {
        this.clearSession();
        throw new Error('Session expired. Please log in again.');
      } else if (error.response?.status === 422) {
        const errorDetail = error.response.data.detail;
        const errorMessage = typeof errorDetail === 'object' 
          ? JSON.stringify(errorDetail) 
          : errorDetail || 'Please check your input';
        throw new Error(`Validation error: ${errorMessage}`);
      } else if (error.response?.status === 404) {
        throw new Error('Pet not found. The pet ID may be invalid or deleted.');
      }
      throw error;
    }
  }

  public async chatWithPet(request: ChatRequest): Promise<ChatResponse> {
    try {
      const petId = await this.getCorrectPetId();
      
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/api/chat`, {
        ...request,
        pet_id: petId
      }, {
        headers: this.headers
      });
      return response.data;
    } catch (error) {
      console.error('Error in chatWithPet:', error);
      throw error;
    }
  }

  public async savePet(pet: Partial<Pet>): Promise<Pet> {
    const response = await axios.post<Pet>(`${API_BASE_URL}/api/save-pet`, pet, {
      headers: this.headers
    });
    return response.data;
  }
}

export const apiService = ApiService.getInstance(); 