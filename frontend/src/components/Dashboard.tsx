import React, { useState } from 'react';
import PetDisplay from './PetDisplay';
import ActionButtons from './ActionButtons';
import Notification from './Notification';
import { Pet, PetAction } from '../types/pet';
import '../styles/RetroStyles.css';

interface DashboardProps {
  pet: Pet;
}

interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

const Dashboard: React.FC<DashboardProps> = ({ pet }) => {
  // Simulated action cooldown (3 seconds)
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
  
  // Handle pet actions (Feed, Play, Teach)
  const handleAction = (action: PetAction) => {
    // Set cooldown
    setActionCooldown(true);
    
    // Update pet based on action type
    switch (action.type) {
      case 'FEED':
        setIsFeeding(true);
        setTimeout(() => setIsFeeding(false), 500); // Match animation duration
        showNotification('ChronoPal is eating... Yum!', 'success');
        break;
        
      case 'PLAY':
        setIsPlaying(true);
        setTimeout(() => setIsPlaying(false), 3000); // Match animation duration
        showNotification('ChronoPal is playing and having fun!', 'success');
        break;
        
      case 'TEACH':
        setIsTeaching(true);
        setTimeout(() => setIsTeaching(false), 2000); // Total duration for 2 iterations
        showNotification('ChronoPal is learning new things!', 'info');
        break;
    }
    
    // Reset cooldown after 3 seconds
    setTimeout(() => setActionCooldown(false), 3000);
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
    if (!userInput.trim()) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      type: 'user',
      content: userInput,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsTyping(true);

    try {
      // Simulate AI response with a more direct, friendly style
      setTimeout(() => {
        const aiResponse: ChatMessage = {
          type: 'ai',
          content: generatePetResponse(userInput),
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiResponse]);
        setIsTyping(false);
      }, 1000);
    } catch (error) {
      showNotification('Error communicating with ChronoPal', 'warning');
      setIsTyping(false);
    }
  };

  // Add a function to generate contextual pet responses
  const generatePetResponse = (input: string) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('how are you') || lowerInput.includes('how do you feel')) {
      return `I'm feeling ${pet.happiness > 80 ? 'super happy' : pet.happiness > 50 ? 'pretty good' : 'a bit down'}! ${pet.hunger < 50 ? 'Could use a snack though!' : ''}`;
    }
    
    if (lowerInput.includes('play') || lowerInput.includes('game')) {
      return `Yes! I love playing games! ${pet.happiness < 70 ? 'It would really cheer me up!' : 'It will be so much fun!'}`;
    }
    
    if (lowerInput.includes('food') || lowerInput.includes('hungry') || lowerInput.includes('eat')) {
      return `${pet.hunger < 50 ? 'Yes, I am getting hungry! Feed me please!' : 'I\'m pretty full right now, but thanks for asking!'}`;
    }
    
    if (lowerInput.includes('learn') || lowerInput.includes('teach') || lowerInput.includes('smart')) {
      return `${pet.intelligence < 70 ? 'I love learning new things! Teach me more!' : 'I\'ve learned so much already, but there\'s always more to discover!'}`;
    }
    
    if (lowerInput.includes('name')) {
      return `I'm ${pet.name}, your digital friend! Nice to chat with you!`;
    }
    
    // Default responses based on pet's mood
    const defaultResponses = [
      `*wiggles happily* What shall we do next?`,
      `I'm so glad you're here! Want to play or learn something new?`,
      `*bounces excitedly* I love chatting with you!`,
      `Let's do something fun together!`
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
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
                  <span>Hunger:</span>
                  <span>{pet.hunger}/100</span>
                </div>
                <div className="player-row">
                  <span>Happiness:</span>
                  <span>{pet.happiness}/100</span>
                </div>
                <div className="player-row">
                  <span>Intelligence:</span>
                  <span>{pet.intelligence}/100</span>
                </div>
              </div>
            </div>
          </div>

          {/* AI Chat Section */}
          <div className="retro-table-row">
            <div className="retro-table-cell" style={{ gridColumn: '1 / -1' }}>
              <div className="section-header">Ask ChronoPal</div>
              <div className="retro-card">
                {/* Chat Messages */}
                <div className="chat-messages" style={{ 
                  height: '200px', 
                  overflowY: 'auto',
                  border: '1px solid #0ff',
                  padding: '10px',
                  marginBottom: '10px',
                  backgroundColor: '#000',
                  color: '#0ff',
                  fontFamily: 'Courier New, monospace'
                }}>
                  {chatMessages.map((message, index) => (
                    <div key={index} style={{ 
                      marginBottom: '10px',
                      padding: '5px',
                      borderLeft: `3px solid ${message.type === 'user' ? '#0f0' : '#f0f'}`,
                      backgroundColor: '#000'
                    }}>
                      <div style={{ 
                        color: message.type === 'user' ? '#0f0' : '#f0f',
                        fontWeight: 'bold',
                        marginBottom: '5px'
                      }}>
                        {message.type === 'user' ? 'You:' : 'ChronoPal:'}
                      </div>
                      <div style={{ whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </div>
                      <div style={{ 
                        fontSize: '10px',
                        color: '#666',
                        textAlign: 'right'
                      }}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div style={{ 
                      color: '#f0f',
                      fontStyle: 'italic'
                    }}>
                      ChronoPal is thinking...
                    </div>
                  )}
                </div>

                {/* Chat Input */}
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="text"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask ChronoPal anything..."
                    style={{
                      flex: 1,
                      padding: '8px',
                      backgroundColor: '#000',
                      color: '#0ff',
                      border: '1px solid #0ff',
                      fontFamily: 'Courier New, monospace'
                    }}
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

      {/* Footer */}
      <div className="retro-footer">
        <div className="hit-counter">Visitors: 000001</div>
        <div className="web-ring">
          <div className="web-ring-title">Web Ring</div>
          <a href="#" className="retro-link">Previous Site</a>
          <a href="#" className="retro-link">Next Site</a>
        </div>
        <div className="under-construction"></div>
      </div>

      <Notification
        show={notification.show}
        message={notification.message}
        type={notification.type}
        onClose={closeNotification}
      />
    </div>
  );
};

export default Dashboard; 