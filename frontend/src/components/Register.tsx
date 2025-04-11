import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { UserCreate } from '../types/user';
import { Pet } from '../types/pet';
import '../styles/RetroStyles.css';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserCreate>({
    email: '',
    password: '',
    username: ''
  });
  const [petName, setPetName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    // Validate passwords match
    if (formData.password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    // Validate username format
    if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      setError('Username can only contain letters, numbers, and underscores');
      return;
    }

    // Validate username length
    if (formData.username.length < 3 || formData.username.length > 50) {
      setError('Username must be between 3 and 50 characters long');
      return;
    }

    // Validate email format
    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    // Validate pet name
    if (!petName.trim()) {
      setError('Please give your pet a name');
      return;
    }

    setIsLoading(true);

    try {
      // Register the user
      const user = await apiService.register(formData.email, formData.password, formData.username);
      setSuccessMessage('Account created successfully! Creating your pet...');
      
      // Log the user in
      await apiService.login(formData.email, formData.password);

      const now = new Date().toISOString();

      // Create the pet
      const newPet = {
        name: petName,
        species: 'Digital',
        mood: 'happy',
        level: 1,
        sassLevel: 1,
        userId: user.id,
        lastFed: now,
        lastInteraction: now,
        interactionCount: 0,
        memoryLog: []
      };

      // Wait for pet creation to complete
      const createdPet = await apiService.savePet(newPet);
      if (!createdPet) {
        throw new Error('Failed to create pet');
      }

      // Verify pet was created
      const verifiedPet = await apiService.getUserPet();
      if (!verifiedPet) {
        throw new Error('Failed to verify pet creation');
      }

      setSuccessMessage('Pet created successfully! Redirecting to dashboard...');

      // Redirect to dashboard after a short delay to show success message
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err: any) {
      if (err.response?.data?.detail) {
        // Handle Pydantic validation errors
        if (Array.isArray(err.response.data.detail)) {
          // If it's an array of validation errors, join them
          setError(err.response.data.detail.map((e: any) => e.msg).join(', '));
        } else {
          // If it's a single error message
          setError(err.response.data.detail);
        }
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="retro-container">
      <div className="retro-panel" style={{ maxWidth: '400px', margin: '0 auto' }}>
        <h2 className="retro-title">Create Your Account</h2>
        
        <form onSubmit={handleSubmit} className="retro-form">
          <div className="retro-table">
            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="username" className="section-header">Username:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="retro-input"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>
            
            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="email" className="section-header">Email:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="retro-input"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="password" className="section-header">Password:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="retro-input"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="confirmPassword" className="section-header">Confirm Password:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="retro-input"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="petName" className="section-header">Pet Name:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="text"
                  id="petName"
                  value={petName}
                  onChange={(e) => setPetName(e.target.value)}
                  className="retro-input"
                  required
                  disabled={isLoading}
                  placeholder="Name your ChronoPal"
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="retro-error">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="retro-success" style={{ color: '#0f0', textAlign: 'center', margin: '10px 0' }}>
              {successMessage}
            </div>
          )}

          <button 
            type="submit" 
            className="retro-button"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="retro-footer">
          <p>Already have an account? <a href="/login" className="retro-link">Login here</a></p>
        </div>
      </div>
    </div>
  );
};

export default Register; 