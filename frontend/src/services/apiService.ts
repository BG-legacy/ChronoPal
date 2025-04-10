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

  public async register(email: string, password: string, username: string): Promise<User> {
    const response = await axios.post<User>(`${API_BASE_URL}/api/register`, {
      email,
      password,
      username
    });
    return response.data;
  }

  public async login(email: string, password: string): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(`${API_BASE_URL}/api/login`, {
      email,
      password
    });
    this.setSessionId(response.data.session_id);
    return response.data;
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
      const response = await axios.get<Pet>(`${API_BASE_URL}/api/user-pet`, {
        headers: this.headers
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        this.clearSession();
        throw new Error('Session expired. Please log in again.');
      }
      throw error;
    }
  }

  public async updateInteraction(request: InteractionRequest): Promise<Pet> {
    const response = await axios.post<Pet>(`${API_BASE_URL}/api/update-interaction`, request, {
      headers: this.headers
    });
    return response.data;
  }

  public async chatWithPet(request: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(`${API_BASE_URL}/api/chat`, request, {
      headers: this.headers
    });
    return response.data;
  }

  public async savePet(pet: Pet): Promise<Pet> {
    const response = await axios.post<Pet>(`${API_BASE_URL}/api/save-pet`, pet, {
      headers: this.headers
    });
    return response.data;
  }
}

export const apiService = ApiService.getInstance(); 