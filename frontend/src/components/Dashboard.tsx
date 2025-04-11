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
        
        // Check if session exists
        const sessionId = localStorage.getItem('sessionId');
        if (!sessionId) {
          console.log('No session found, redirecting to login');
          setError('Please log in to view your pet');
          navigate('/login');
          return;
        }
        
        // Try to get a consistent pet by using the stored pet ID if available
        const storedPetId = localStorage.getItem('currentPetId');
        
        console.log('Trying to fetch pet with session:', sessionId.substring(0, 8) + '...');
        console.log('Stored pet ID:', storedPetId || 'none');
        
        let petData;
        try {
          petData = await apiService.getUserPet();
          console.log('Pet data fetched successfully:', petData);
          console.log('Pet ID type and value:', typeof petData.id, petData.id);
        } catch (fetchErr) {
          console.error('Error fetching pet from API:', fetchErr);
          
          // If stored ID exists, create a fallback pet object
          if (storedPetId) {
            console.log('Using stored pet ID to create fallback pet:', storedPetId);
            petData = {
              id: storedPetId,
              name: "Berny",
              species: "Digital",
              mood: "happy",
              level: 1,
              sassLevel: 1,
              userId: "current-user",
              lastFed: new Date().toISOString(),
              lastInteraction: new Date().toISOString(),
              interactionCount: 0,
              memoryLog: []
            };
          } else {
            throw fetchErr;
          }
        }
        
        // Handle case where pet data doesn't have an id but has _id (MongoDB format)
        if (!petData.id && (petData as any)._id) {
          console.log('Pet has _id but no id, fixing...', (petData as any)._id);
          petData = {
            ...petData,
            id: (petData as any)._id
          };
        }
        
        if (!petData.id) {
          console.error('WARNING: Pet has no ID!', petData);
        } else {
          // Store the pet ID in localStorage for consistency
          localStorage.setItem('currentPetId', petData.id);
          console.log('Stored pet ID in localStorage:', petData.id);
        }
        
        setPet(petData);
      } catch (err: any) {
        console.error('Error fetching pet:', err);
        if (err.message === 'No session ID found. Please log in.' || 
            err.message === 'Session expired. Please log in again.') {
          setError('Please log in to view your pet');
          
          // Clear any invalid session
          localStorage.removeItem('sessionId');
          apiService.clearSession();
          
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
    
    // Extract the message if present in the action
    const message = action.type === 'TEACH' ? action.message : undefined;
    
    try {
      // Map the action type to the interaction_type expected by the API
      const interactionType = action.type.toLowerCase();
      
      // Call the API service - our new implementation doesn't need pet_id
      // but we still include it for compatibility with older code
      const updatedPet = await apiService.updateInteraction({
        pet_id: pet?.id || 'user-pet', // pet ID isn't needed anymore but included for API compatibility
        interaction_type: interactionType,
        ...(message ? { message } : {})
      });
      
      console.log('Received updated pet:', updatedPet);
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
    } catch (err: any) {
      console.error('Failed to perform action:', err);
      
      // Extract and clean up the error message
      let errorMessage = 'Failed to perform action';
      
      if (err.message) {
        // Clean up validation error messages
        if (err.message.includes('Validation error:')) {
          errorMessage = err.message.replace('Validation error: ', '');
          
          // Format specific error messages better
          if (errorMessage.includes('Message is required for')) {
            errorMessage = 'You need to enter something to teach your pet!';
          } else if (errorMessage.includes('missing') && errorMessage.includes('pet_id')) {
            errorMessage = 'Pet ID is missing. Please refresh the page.';
          }
        } else {
          errorMessage = err.message;
        }
      }
      
      // Additional error context
      if (err.response && err.response.status === 404) {
        errorMessage = 'Could not find your pet in the database. Try refreshing the page.';
      }
      
      showNotification(`Error: ${errorMessage}`, 'warning');
    } finally {
      // Always set the cooldown to false after a delay
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

    try {
      setIsTyping(true);
      const userMessage: ChatMessage = {
        type: 'user',
        content: userInput,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, userMessage]);
      setUserInput('');

      try {
        // The API service now handles getting the correct pet ID
        const response = await apiService.chatWithPet({
          message: userMessage.content,
          pet_id: pet.id || '' // This will be overridden by the apiService
        });
        
        const aiMessage: ChatMessage = {
          type: 'ai',
          content: response.response,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiMessage]);
        
        // After successful chat, refresh pet data
        try {
          const refreshedPet = await apiService.getUserPet();
          if (refreshedPet) {
            setPet(refreshedPet);
          }
        } catch (refreshErr) {
          console.log('Could not refresh pet after chat:', refreshErr);
        }
      } catch (apiErr) {
        console.error('API error during chat:', apiErr);
        
        // Generate a fallback response
        const fallbackResponses = [
          "OMG, like, the internet connection is totally buggin'! Can we chat later?",
          "Whoa, server drama! Let's pretend I said something super clever.",
          "System's having a Y2K moment. BRB after I fix this glitch!",
          "*dial-up noises* Sorry, my brain is buffering right now."
        ];
        
        const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
        
        const aiMessage: ChatMessage = {
          type: 'ai',
          content: randomResponse,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiMessage]);
      } finally {
        setIsTyping(false);
      }
    } catch (error) {
      showNotification('Error in chat functionality', 'warning');
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
        {/* Debug Controls */}
        <div style={{ marginTop: '10px' }}>
          <button 
            onClick={() => {
              apiService.forceSessionRefresh();
            }}
            className="retro-button retro-button-small"
            style={{ fontSize: '10px', padding: '2px 5px' }}
          >
            Debug: Refresh Session
          </button>
        </div>
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
                  <span>{pet.sassLevel}</span>
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