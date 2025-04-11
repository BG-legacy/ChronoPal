import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/RetroStyles.css';
import catLogo from '../assets/cat.png';
import csuLogo from '../assets/464-CSU-cougars.webp';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [petMood, setPetMood] = useState('happy');
  const [showWelcome, setShowWelcome] = useState(false);

  // Cycle through pet moods to show virtual pet behavior
  useEffect(() => {
    const moods = ['happy', 'eating', 'playing', 'sleeping'];
    let moodIndex = 0;
    
    const moodInterval = setInterval(() => {
      moodIndex = (moodIndex + 1) % moods.length;
      setPetMood(moods[moodIndex]);
    }, 3000);
    
    return () => clearInterval(moodInterval);
  }, []);

  useEffect(() => {
    // Show welcome popup after a delay for that authentic 2000s experience
    const timer = setTimeout(() => {
      setShowWelcome(true);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  // 2000s cursor trail effect
  useEffect(() => {
    const MAX_TRAIL = 12; // Number of trail elements
    const trails: HTMLDivElement[] = [];
    let mouseX = 0;
    let mouseY = 0;

    // Create trail elements
    for (let i = 0; i < MAX_TRAIL; i++) {
      const trail = document.createElement('div');
      trail.className = 'trail-dot';
      trail.style.position = 'fixed';
      trail.style.width = '8px';
      trail.style.height = '8px';
      trail.style.borderRadius = '50%';
      trail.style.background = i % 2 === 0 ? '#ff00ff' : '#00ffff';
      trail.style.zIndex = '9999';
      trail.style.pointerEvents = 'none';
      trail.style.transition = 'left 0.1s ease, top 0.1s ease';
      trail.style.opacity = (1 - i / MAX_TRAIL).toString();
      document.body.appendChild(trail);
      trails.push(trail);
    }

    // Update mouse position
    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    // Update trail positions
    const updateTrail = () => {
      for (let i = trails.length - 1; i > 0; i--) {
        const prevX = parseInt(trails[i-1].style.left || '0', 10);
        const prevY = parseInt(trails[i-1].style.top || '0', 10);
        
        if (!isNaN(prevX) && !isNaN(prevY)) {
          trails[i].style.left = prevX + 'px';
          trails[i].style.top = prevY + 'px';
        }
      }
      
      trails[0].style.left = mouseX + 'px';
      trails[0].style.top = mouseY + 'px';
      
      requestAnimationFrame(updateTrail);
    };

    // Start the animation
    document.addEventListener('mousemove', handleMouseMove);
    requestAnimationFrame(updateTrail);

    // Cleanup
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      trails.forEach(trail => {
        if (trail.parentNode) {
          trail.parentNode.removeChild(trail);
        }
      });
    };
  }, []);

  // Helper function to render pet with different animations based on mood
  const renderPetAnimation = () => {
    return (
      <div className={`tamagotchi-pet ${petMood}`}>
        <div className="tamagotchi-screen-minimal">
          <div className="tamagotchi-body">
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
          
          {petMood === 'eating' && (
            <div className="food-particles"></div>
          )}
          
          {petMood === 'playing' && (
            <>
              <div className="play-toy"></div>
              <div className="play-stars"></div>
            </>
          )}
        </div>
      </div>
    );
  };
  
  const getMoodMessage = () => {
    switch(petMood) {
      case 'happy': return "I'm happy!";
      case 'eating': return "Yum yum!";
      case 'playing': return "This is fun!";
      case 'sleeping': return "Zzz...";
      default: return "";
    }
  };

  return (
    <div className="retro-container">
      {/* Browser Notice */}
      <div className="retro-browser-notice">
        Best viewed in Netscape Navigator 4.0 or higher at 800x600 resolution
      </div>

      {/* Old-school popup */}
      {showWelcome && (
        <div className="retro-popup">
          <div className="retro-popup-content">
            <h3>Welcome to ChronoPal!</h3>
            <p>The #1 Virtual Pet Community on the Web!</p>
            <button onClick={() => setShowWelcome(false)}>Enter Site</button>
          </div>
        </div>
      )}

      {/* Custom Marquee using CSS animation instead of the deprecated marquee tag */}
      <div className="retro-marquee">
        <div className="marquee-content">
          <span>★★★ Welcome to ChronoPal - Your Virtual Pet from the Future! ★★★ Feed! Play! Teach! ★★★ Watch your pet evolve! ★★★</span>
        </div>
      </div>

      {/* Header with title only */}
      <div className="retro-header">
        <div className="flex justify-center items-center">
          <h1 className="retro-title retro-glow text-3xl">ChronoPal</h1>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="retro-table">
        <div className="retro-table-row">
          {/* Left Sidebar - simplified with pixelated peach */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            {/* CSU Cougars Logo */}
            <div className="csu-logo-container">
              <img src={csuLogo} alt="CSU Cougars" className="csu-logo" />
            </div>
            
            {/* Pixelated Peach */}
            <div className="pixel-art-container">
              <div className="pixel-art pixel-peach">
                <div className="leaf"></div>
                <div className="stem"></div>
              </div>
              <div className="pixel-art-caption">Peachy!</div>
            </div>
          </div>

          {/* Main Content - enhanced center content with visual demo */}
          <div className="retro-table-cell" style={{ width: '60%' }}>
            <div className="retro-panel black-bg">
              <div className="text-center mb-6 mobile-priority-content">
                {/* Proper order for mobile: title, subtitle, description, pet, button */}
                <div className="sparkle-text">⋆✧⋆ Your Pet Awaits! ⋆✧⋆</div>
                <h2 className="retro-title text-2xl mb-4">ChronoPal - Tamagotchi AI</h2>
                <p className="mb-4 text-xl" style={{ color: '#0ff' }}>FEED. PLAY. EVOLVE!</p>
                
                {/* Interactive Pet Demo */}
                <div className="pet-only">
                  {renderPetAnimation()}
                </div>
                
                <button 
                  onClick={() => navigate('/login')}
                  className="retro-button retro-glow"
                >
                  Start Your Journey
                </button>
              </div>
              
              {/* Feature Grid - Visual showcase */}
              <div className="feature-grid mt-6">
                <div className="feature-box">
                  <div className="feature-box-title">Raise Your Pet</div>
                  <div className="feature-box-content">
                    <div className="feature-animation raising"></div>
                    <p>Feed, clean & nurture your digital companion!</p>
                  </div>
                </div>
                
                <div className="feature-box">
                  <div className="feature-box-title">Play Games</div>
                  <div className="feature-box-content">
                    <div className="feature-animation gaming"></div>
                    <p>Unlock mini-games & earn coins!</p>
                  </div>
                </div>
                
                <div className="feature-box">
                  <div className="feature-box-title">Evolve</div>
                  <div className="feature-box-content">
                    <div className="feature-animation evolving"></div>
                    <p>Watch your pet transform as it grows!</p>
                  </div>
                </div>
                
                <div className="feature-box">
                  <div className="feature-box-title">Connect</div>
                  <div className="feature-box-content">
                    <div className="feature-animation connecting"></div>
                    <p>Meet other pet owners in our community!</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar - replaced with pixelated images */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            {/* Pixelated Images Related to Project */}
            <div className="pixelated-images-container">
              {/* Pixelated Tamagotchi Device */}
              <div className="pixel-art-container">
                <div className="pixel-art tamagotchi-device">
                  <div className="button-a"></div>
                  <div className="button-b"></div>
                  <div className="button-c"></div>
                </div>

              </div>
              
              {/* Pixelated Y2K Computer */}
              <div className="pixel-art-container">
                <div className="pixel-art y2k-computer">
                  <div className="base"></div>
                  <div className="keyboard"></div>
                </div>
               
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="retro-footer mt-8">
        <div className="flex justify-center space-x-4 mb-2">
          <Link to="/about" className="retro-link">About</Link> |
          <Link to="/contact" className="retro-link">Contact</Link> |
          <Link to="/rules" className="retro-link">Rules</Link> |
          <Link to="/privacy" className="retro-link">Privacy</Link> |
          <a href="#" className="retro-link">Sign Guestbook</a>
        </div>
        <div>© 2000 ChronoPal - All Your Pets Are Belong To Us</div>
        <div className="page-stats">
          <span>Page loads: {Math.floor(Math.random() * 9999) + 1000}</span> |
          <span>Last updated: 04/20/2000</span> |
          <span>Optimized for 800x600</span>
        </div>
      </div>

      {/* Under Construction Corner */}
      <div className="under-construction"></div>

      {/* Best Viewed Notice */}
      <div className="best-viewed">
        Best viewed with<br/>Netscape Navigator
      </div>
    </div>
  );
};

export default LandingPage; 