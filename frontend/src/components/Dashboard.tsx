import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import PetDisplay from './PetDisplay';
import ActionButtons from './ActionButtons';
import Notification from './Notification';
import { Pet, PetAction } from '../types/pet';
import { apiService } from '../services/apiService';
import '../styles/RetroStyles.css';

interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Action states
  const [actionCooldown, setActionCooldown] = useState(false);
  const [isFeeding, setIsFeeding] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isTeaching, setIsTeaching] = useState(false);
  
  // Notification state
  const [notification, setNotification] = useState({
    show: false,
    message: '',
    type: 'info' as 'success' | 'warning' | 'info'
  });
  
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    const fetchPet = async () => {
      try {
        setLoading(true);
        setError(null);
        const petData = await apiService.getUserPet();
        setPet(petData);
      } catch (err: any) {
        console.error('Error fetching pet:', err);
        if (err.message === 'No session ID found. Please log in.' || 
            err.message === 'Session expired. Please log in again.') {
          setError('Please log in to view your pet');
          navigate('/login');
        } else {
          setError(err.message || 'Failed to fetch pet data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPet();
  }, [navigate]);

  if (loading) {
    return (
      <div className="retro-container">
        <div className="retro-panel">
          <h2 className="retro-title">Loading your ChronoPal...</h2>
        </div>
      </div>
    );
  }

  if (error || !pet) {
    return (
      <div className="retro-container">
        <div className="retro-panel">
          <h2 className="retro-title">Error</h2>
          <p className="retro-error">{error || 'No pet found'}</p>
          <button 
            onClick={() => navigate('/login')}
            className="retro-button"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }
  
  const handleAction = async (action: PetAction) => {
    if (actionCooldown) return;
    
    setActionCooldown(true);
    
    try {
      const updatedPet = await apiService.updateInteraction({
        pet_id: pet.id,
        interaction_type: action.type.toLowerCase(),
        message: action.message
      });
      
      setPet(updatedPet);
      
      // Set animation states
      switch (action.type) {
        case 'FEED':
          setIsFeeding(true);
          setTimeout(() => setIsFeeding(false), 500);
          showNotification('ChronoPal is eating... Yum!', 'success');
          break;
        case 'PLAY':
          setIsPlaying(true);
          setTimeout(() => setIsPlaying(false), 3000);
          showNotification('ChronoPal is playing and having fun!', 'success');
          break;
        case 'TEACH':
          setIsTeaching(true);
          setTimeout(() => setIsTeaching(false), 2000);
          showNotification('ChronoPal is learning new things!', 'info');
          break;
      }
    } catch (err) {
      showNotification('Failed to perform action', 'warning');
    } finally {
      setTimeout(() => setActionCooldown(false), 3000);
    }
  };
  
  const showNotification = (message: string, type: 'success' | 'warning' | 'info') => {
    setNotification({
      show: true,
      message,
      type
    });
  };
  
  const closeNotification = () => {
    setNotification(prev => ({ ...prev, show: false }));
  };

  const handleSendMessage = async () => {
    if (!userInput.trim() || !pet) return;

    const userMessage: ChatMessage = {
      type: 'user',
      content: userInput,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsTyping(true);

    try {
      const response = await apiService.chatWithPet({
        message: userInput,
        pet_id: pet.id
      });
      
      const aiMessage: ChatMessage = {
        type: 'ai',
        content: response.response,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      showNotification('Error communicating with ChronoPal', 'warning');
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="retro-container">
      {/* Browser Notice */}
      <div className="retro-browser-notice">
        Best viewed in Netscape Navigator 4.0 or Internet Explorer 5.0 at 800x600 resolution
      </div>

      {/* Main Header */}
      <div className="retro-header">
        <h1 className="site-title">ChronoPal</h1>
        <p className="retro-title">Your l33t Digital BFF from Y2K!</p>
      </div>

      {/* Main Content */}
      <div className="retro-panel">
        <div className="retro-table">
          <div className="retro-table-row">
            {/* Pet Display */}
            <div className="retro-table-cell">
              <div className="section-header">Your ChronoPal</div>
              <PetDisplay 
                pet={pet} 
                isFeeding={isFeeding}
                isPlaying={isPlaying}
                isTeaching={isTeaching}
              />
            </div>

            {/* Actions */}
            <div className="retro-table-cell">
              <div className="section-header">Actions</div>
              <ActionButtons 
                onAction={handleAction} 
                disabled={actionCooldown} 
              />
            </div>
          </div>

          {/* Status Section */}
          <div className="retro-table-row">
            <div className="retro-table-cell" style={{ gridColumn: '1 / -1' }}>
              <div className="section-header">Status</div>
              <div className="retro-card">
                <div className="player-row">
                  <span>Level:</span>
                  <span>{pet.level}</span>
                </div>
                <div className="player-row">
                  <span>Mood:</span>
                  <span>{pet.mood}</span>
                </div>
                <div className="player-row">
                  <span>Sass Level:</span>
                  <span>{pet.sass_level}</span>
                </div>
                <div className="player-row">
                  <span>Interactions:</span>
                  <span>{pet.interactionCount}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Section */}
          <div className="retro-table-row">
            <div className="retro-table-cell" style={{ gridColumn: '1 / -1' }}>
              <div className="section-header">Chat with ChronoPal</div>
              <div className="chat-container">
                <div className="chat-messages">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.type}`}>
                      <span className="message-content">{msg.content}</span>
                      <span className="message-time">
                        {msg.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="chat-message ai typing">
                      ChronoPal is typing...
                    </div>
                  )}
                </div>
                <div className="chat-input">
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                    className="retro-input"
                  />
                  <button
                    onClick={handleSendMessage}
                    className="retro-button"
                    disabled={isTyping}
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Notification */}
      {notification.show && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={closeNotification}
          show={notification.show}
        />
      )}
    </div>
  );
};

export default Dashboard; 