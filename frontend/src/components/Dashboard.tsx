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
  isTyping?: boolean;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [pet, setPet] = useState<Pet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [petDead, setPetDead] = useState(false);
  
  // Action states
  const [actionCooldown, setActionCooldown] = useState(false);
  const [isFeeding, setIsFeeding] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isTeaching, setIsTeaching] = useState(false);
  
  // Clock state
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Notification state
  const [notification, setNotification] = useState({
    show: false,
    message: '',
    type: 'info' as 'success' | 'warning' | 'info'
  });
  
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Battery depletion logic
  useEffect(() => {
    // Deplete battery every 30 seconds
    const batteryDrainInterval = setInterval(() => {
      if (pet && !petDead) {
        // Calculate new battery level
        const newBatteryLevel = Math.max(0, (pet.batteryLevel || 100) - 1);
        
        // Update pet with new battery level
        setPet(prevPet => {
          if (prevPet) {
            return { ...prevPet, batteryLevel: newBatteryLevel };
          }
          return prevPet;
        });
        
        // Check if pet is dead
        if (newBatteryLevel <= 0) {
          handlePetDeath();
        }
      }
    }, 30000); // 30 seconds
    
    return () => clearInterval(batteryDrainInterval);
  }, [pet, petDead]);

  // Handle pet death
  const handlePetDeath = () => {
    setPetDead(true);
    
    // Show death notification
    showNotification("Your ChronoPal's battery has depleted completely! It has shut down.", 'warning');
    
    // Add death message to chat
    const deathMessage: ChatMessage = {
      type: 'ai',
      content: "System Error: Battery depleted. ChronoPal shutting down... *beep* *boop* *silence*",
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, deathMessage]);
  };

  // Reset pet (create a new one)
  const handleResetPet = async () => {
    try {
      // Show loading message
      showNotification('Resetting your ChronoPal...', 'info');
      setLoading(true);
      
      // Call the API to reset the pet
      const newPet = await apiService.resetPet();
      
      // Update the pet state
      setPet(newPet);
      setPetDead(false);
      
      // Show success message
      showNotification('ChronoPal has been reset with a fresh battery!', 'success');
      
      // Reset chat messages
      setChatMessages([]);
      
      // Add welcome message
      setTimeout(() => {
        const welcomeMessage: ChatMessage = {
          type: 'ai',
          content: "OMG hi there! I'm your new ChronoPal! Like, I'm totally ready to chat! What's up? :D",
          timestamp: new Date()
        };
        setChatMessages([welcomeMessage]);
      }, 1000);
      
    } catch (err) {
      console.error('Failed to reset pet:', err);
      showNotification('Failed to reset your ChronoPal. Please try again.', 'warning');
    } finally {
      setLoading(false);
    }
  };

  // Update clock every second instead of every minute
  useEffect(() => {
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(clockInterval);
  }, []);

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
              batteryLevel: 100, // Initialize with full battery
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
        
        // Set default battery level if not present
        if (petData.batteryLevel === undefined) {
          petData.batteryLevel = 100;
        }
        
        if (!petData.id) {
          console.error('WARNING: Pet has no ID!', petData);
        } else {
          // Store the pet ID in localStorage for consistency
          localStorage.setItem('currentPetId', petData.id);
          console.log('Stored pet ID in localStorage:', petData.id);
        }
        
        setPet(petData);
        
        // Check if pet is already dead
        if (petData.batteryLevel <= 0) {
          setPetDead(true);
        }
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

    // Initial fetch
    fetchPet();
    
    // Set up automatic refresh every 30 seconds
    const petRefreshInterval = setInterval(() => {
      if (!petDead) {
        fetchPet();
      }
    }, 30000);
    
    return () => clearInterval(petRefreshInterval);
  }, [navigate, petDead]);

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
    if (actionCooldown || petDead) return;
    
    if (petDead) {
      showNotification("Your ChronoPal's battery is depleted! You need to reset your pet.", 'warning');
      return;
    }
    
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
      
      // Ensure the pet's battery level persists if not returned by API
      if (updatedPet.batteryLevel === undefined && pet.batteryLevel !== undefined) {
        updatedPet.batteryLevel = pet.batteryLevel;
      }
      
      // Increase battery based on action type
      let batteryIncrease = 0;
      switch (action.type) {
        case 'FEED':
          batteryIncrease = 10;
          break;
        case 'PLAY':
          batteryIncrease = 5;
          break;
        case 'TEACH':
          batteryIncrease = 7;
          break;
      }
      
      // Update the battery level (cap at 100)
      updatedPet.batteryLevel = Math.min(100, (updatedPet.batteryLevel || 0) + batteryIncrease);
      
      setPet(updatedPet);
      
      // Set animation states
      switch (action.type) {
        case 'FEED':
          setIsFeeding(true);
          setTimeout(() => setIsFeeding(false), 1500); // Reduced from 3000 to 1500ms
          showNotification('ChronoPal is eating... Yum! Battery increased by 10%', 'success');
          break;
        case 'PLAY':
          setIsPlaying(true);
          setTimeout(() => setIsPlaying(false), 2000); // Reduced from 4000 to 2000ms
          showNotification('ChronoPal is playing and having fun! Battery increased by 5%', 'success');
          break;
        case 'TEACH':
          setIsTeaching(true);
          // Keep teaching animation active until response is received
          setTimeout(() => setIsTeaching(false), 2000); // Reduced from 4000 to 2000ms
          showNotification('ChronoPal is learning new things! Battery increased by 7%', 'info');
          
          // Add a personalized response from the pet to what was taught
          if (action.message) {
            // Show typing indicator while waiting for response
            setIsTyping(true);
            
            setTimeout(async () => {
              try {
                // Call the chat API to get a personalized response using OpenAI
                const response = await apiService.chatWithPet({
                  message: `I just learned about ${action.message}. What do you think about that?`,
                  pet_id: pet.id || ''
                });
                
                // Add the teaching response as a chat message
                const aiMessage: ChatMessage = {
                  type: 'ai',
                  content: response.response || `OMG, I just learned about "${action.message}"! That's like, totally cool! Thanks for teaching me that!`,
                  timestamp: new Date()
                };
                setChatMessages(prev => [...prev, aiMessage]);
              } catch (err) {
                console.error('Error getting teaching response:', err);
                // Fallback response if API call fails
                const aiMessage: ChatMessage = {
                  type: 'ai',
                  content: `I just learned about "${action.message}"! That's so cool! Thanks for teaching me that!`,
                  timestamp: new Date()
                };
                setChatMessages(prev => [...prev, aiMessage]);
              } finally {
                setIsTyping(false);
              }
            }, 2000); // Show response after teaching animation finishes
          }
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
    
    // Auto-hide notification after 2 seconds
    setTimeout(() => {
      setNotification(prev => ({ ...prev, show: false }));
    }, 2000);
  };
  
  const closeNotification = () => {
    setNotification(prev => ({ ...prev, show: false }));
  };

  const handleSendMessage = async () => {
    if (!userInput.trim() || !pet || petDead) return;
    
    if (petDead) {
      showNotification("Your ChronoPal's battery is depleted! It can't respond.", 'warning');
      return;
    }

    try {
      setIsTyping(true);
      const userMessage: ChatMessage = {
        type: 'user',
        content: userInput,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, userMessage]);
      setUserInput('');

      // Add a small delay to simulate thinking
      await new Promise(resolve => setTimeout(resolve, 1000));

      try {
        const response = await apiService.chatWithPet({
          message: userMessage.content,
          pet_id: pet.id || ''
        });
        
        // Add a typing indicator message
        const typingMessage: ChatMessage = {
          type: 'ai',
          content: '...',
          timestamp: new Date(),
          isTyping: true
        };
        setChatMessages(prev => [...prev, typingMessage]);
        
        // Simulate typing delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Remove typing indicator and add actual response
        setChatMessages(prev => {
          const newMessages = prev.filter(msg => !msg.isTyping);
          const aiMessage: ChatMessage = {
            type: 'ai',
            content: response.response,
            timestamp: new Date()
          };
          return [...newMessages, aiMessage];
        });
        
        // Chatting depletes battery slightly
        setPet(prevPet => {
          if (prevPet) {
            const newBatteryLevel = Math.max(0, (prevPet.batteryLevel || 100) - 3);
            
            if (newBatteryLevel <= 0 && (prevPet.batteryLevel || 0) > 0) {
              setTimeout(() => handlePetDeath(), 1000);
            }
            
            return {
              ...prevPet,
              batteryLevel: newBatteryLevel
            };
          }
          return prevPet;
        });
        
        // After successful chat, refresh pet data
        try {
          const refreshedPet = await apiService.getUserPet();
          if (refreshedPet) {
            const currentBatteryLevel = pet.batteryLevel;
            setPet({
              ...refreshedPet,
              batteryLevel: currentBatteryLevel
            });
          }
        } catch (refreshErr) {
          console.log('Could not refresh pet after chat:', refreshErr);
        }
      } catch (apiErr) {
        console.error('API error during chat:', apiErr);
        
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

  // Get appropriate battery class based on level
  const getBatteryClassName = () => {
    if (petDead) return 'battery-empty';
    if (pet.batteryLevel <= 10) return 'battery-critical';
    if (pet.batteryLevel <= 30) return 'battery-low';
    if (pet.batteryLevel <= 50) return 'battery-medium';
    return 'battery-full';
  };

  return (
    <div className="retro-container">
      {/* Main Header */}
      <div className="retro-header">
        <h1 className="site-title">ChronoPal</h1>
        <p className="retro-title">Your l33t Digital BFF from Y2K!</p>
        <button 
          onClick={async () => {
            try {
              await apiService.logout();
              navigate('/');
            } catch (error) {
              console.error('Logout failed:', error);
              showNotification('Failed to logout. Please try again.', 'warning');
            }
          }}
          className="retro-button logout-button"
          style={{ marginTop: '10px' }}
        >
          Logout
        </button>
        {/* Debug Controls */}
        <div style={{ marginTop: '10px' }}>
  
        </div>
      </div>

      {/* Main Content */}
      <div className="retro-panel">
        {/* Four Square Grid Layout */}
        <div className="four-square-grid">
          {/* Top Left: Pet Display with Image */}
          <div className="grid-square grid-square-top-left">
            <div className="section-header">Your ChronoPal</div>
            <div className="pet-image-container">
              <div className="pet-image retro-image-placeholder pet-placeholder">
                <div className="pet-screen-container">
                  <div className="pet-screen">
                    {/* Clock - Improved time display */}
                    <div className="pet-clock">
                      {currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                    {/* Battery indicator */}
                    <div className="battery-indicator">
                      <div 
                        className={`battery-level ${getBatteryClassName()}`}
                        style={{ width: `${petDead ? 0 : Math.max(5, pet.batteryLevel)}%` }}
                      ></div>
                    </div>
                    <div 
                      className={`tamagotchi-pet ${isFeeding ? 'feeding' : ''} ${isPlaying ? 'playing' : ''} ${isTeaching ? 'teaching' : ''} ${petDead ? 'dead' : ''} ${pet.batteryLevel <= 30 ? 'low-battery' : ''} ${pet.batteryLevel <= 10 ? 'critical-battery' : ''}`}
                      data-mood={pet.mood.toLowerCase()}
                      data-sass={pet.sassLevel.toString()}
                      data-level={pet.level.toString()}
                      data-species={pet.species}
                      data-battery={pet.batteryLevel || 0}
                    >
                      {isFeeding && (
                        <div className="food-particles">
                          {/* Food particles will be created via CSS */}
                        </div>
                      )}
                      {isPlaying && (
                        <>
                          <div className="play-toy"></div>
                          <div className="play-stars"></div>
                        </>
                      )}
                      {isTeaching && (
                        <div className="learning-symbols">
                          {/* Learning symbols will be created via CSS */}
                        </div>
                      )}
                      {/* Pixelated cat pet sprite */}
                      <div className="tamagotchi-body">
                        {/* Main cat body structure */}
                        <div className="tamagotchi-head">
                          <div className="tamagotchi-eye left"></div>
                          <div className="tamagotchi-eye right"></div>
                          <div className="tamagotchi-mouth"></div>
                        </div>
                        <div className="tamagotchi-limb tamagotchi-arm left"></div>
                        <div className="tamagotchi-limb tamagotchi-arm right"></div>
                        <div className="tamagotchi-limb tamagotchi-leg left"></div>
                        <div className="tamagotchi-limb tamagotchi-leg right"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="pet-name">{pet.name}</div>
              <div>{pet.species}</div>
              <div>Level: {pet.level}</div>
              <div>Mood: {petDead ? '💀' : pet.batteryLevel <= 10 ? '😨' : pet.batteryLevel <= 30 ? '😟' : '😊'}</div>
              <div>Battery: {petDead ? 'DEPLETED' : `${pet.batteryLevel || 0}%`}</div>
              
              {petDead && (
                <button
                  onClick={handleResetPet}
                  className="retro-button revival-button"
                  style={{ marginTop: '15px', background: 'linear-gradient(to bottom, #00ff00, #009900)' }}
                >
                  Reset ChronoPal
                </button>
              )}
            </div>
          </div>

          {/* Top Right: Actions */}
          <div className="grid-square grid-square-top-right">
            <div className="section-header">Actions</div>
            <div className="action-buttons">
              <ActionButtons 
                onAction={handleAction} 
                disabled={actionCooldown || petDead} 
              />
              
              {petDead && (
                <div className="death-message" style={{ marginTop: '15px', color: '#ff0000', textAlign: 'center' }}>
                  <p>Your ChronoPal's battery has depleted!</p>
                  <p>Reset it to continue.</p>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Left: Stats */}
          <div className="grid-square grid-square-bottom-left">
            <div className="section-header">Status</div>
            <div className="pet-stats">
              <div className="retro-card">
                <div className="player-row">
                  <span>Level:</span>
                  <span>{pet.level}</span>
                </div>
                <div className="player-row">
                  <span>Mood:</span>
                  <span>{petDead ? 'OFFLINE' : pet.mood}</span>
                </div>
                <div className="player-row">
                  <span>Sass Level:</span>
                  <span>{pet.sassLevel}</span>
                </div>
                <div className="player-row">
                  <span>Battery:</span>
                  <span className={getBatteryClassName()}>{petDead ? 'DEPLETED' : `${pet.batteryLevel || 0}%`}</span>
                </div>
                <div className="player-row">
                  <span>Interactions:</span>
                  <span>{pet.interactionCount}</span>
                </div>
                <div className="player-row">
                  <span>System Time:</span>
                  <span>{currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
                <div className="player-row">
                  <span>Current Time:</span>
                  <span>{currentTime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Right: Chat */}
          <div className="grid-square grid-square-bottom-right">
            <div className="section-header">Chat with ChronoPal</div>
            <div className="chat-section">
              <div className="chat-messages">
                {chatMessages.map((msg, index) => (
                  <div key={index} className={`chat-message ${msg.type} ${msg.isTyping ? 'typing' : ''}`}>
                    <span className="message-content">
                      {msg.isTyping ? (
                        <span className="typing-indicator">
                          <span className="dot">.</span>
                          <span className="dot">.</span>
                          <span className="dot">.</span>
                        </span>
                      ) : (
                        msg.content
                      )}
                    </span>
                    {!msg.isTyping && (
                      <span className="message-time">
                        {msg.timestamp.toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                ))}
                {isTyping && !chatMessages.some(msg => msg.isTyping) && (
                  <div className="chat-message ai typing">
                    <span className="typing-indicator">
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                    </span>
                  </div>
                )}
                {chatMessages.length === 0 && !petDead && (
                  <div className="chat-message ai">
                    <span className="message-content">Hey there! What can I assist you with today? 😊</span>
                    <span className="message-time">{new Date().toLocaleTimeString()}</span>
                  </div>
                )}
                {petDead && chatMessages.length === 0 && (
                  <div className="chat-message ai">
                    <span className="message-content">*ERROR: BATTERY DEPLETED* Please reset your ChronoPal to continue...</span>
                    <span className="message-time">{new Date().toLocaleTimeString()}</span>
                  </div>
                )}
              </div>
              <div className="chat-input">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={petDead ? "ChronoPal is offline" : "Type your message..."}
                  className="retro-input"
                  disabled={isTyping || petDead}
                />
                <button
                  onClick={handleSendMessage}
                  className="retro-button"
                  disabled={isTyping || !userInput.trim() || petDead}
                >
                  Send
                </button>
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