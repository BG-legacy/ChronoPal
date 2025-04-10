export interface User {
  id: string;
  email: string;
  username: string;
}

export interface UserCreate {
  email: string;
  password: string;
  username: string;
}

export interface UserLogin {
  email: string;
  password: string;
} 