import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/apiService';
import { UserLogin } from '../types';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await apiService.login(email, password);
      navigate('/dashboard');
    } catch (err) {
      if (err instanceof Error) {
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
        <h2 className="retro-title">Welcome to ChronoPal</h2>
        <div className="retro-browser-notice">
          Best viewed in Netscape Navigator 4.0 or higher
        </div>
        
        <form onSubmit={handleSubmit} className="retro-form">
          <div className="retro-table">
            <div className="retro-table-row">
              <div className="retro-table-cell">
                <label htmlFor="email" className="section-header">Email:</label>
              </div>
              <div className="retro-table-cell">
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="retro-input"
                  required
                  disabled={isLoading}
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="retro-error">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="retro-button"
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Login'}
          </button>
        </form>

        <div className="retro-footer">
          <p>New to ChronoPal? <a href="/register" className="retro-link">Create an account</a></p>
        </div>
      </div>
    </div>
  );
};

export default Login; 