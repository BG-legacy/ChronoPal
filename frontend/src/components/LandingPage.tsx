import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/RetroStyles.css';
import catLogo from '../assets/cat.png';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [totalVisitors] = React.useState(Math.floor(Math.random() * 100000) + 10000);
  const [showWelcome, setShowWelcome] = useState(false);

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
          <span>★★★ Welcome to ChronoPal - Your Virtual Pet from the Future! ★★★ Join our Web Ring! ★★★ New Pet Evolution System Released! ★★★</span>
        </div>
      </div>

      {/* Header with title only */}
      <div className="retro-header">
        <div className="flex justify-center items-center">
          <h1 className="retro-title retro-glow text-3xl">ChronoPal</h1>
        </div>
      </div>

      {/* Navigation Panel with more Y2K style buttons */}
      <div className="retro-panel">
        <div className="retro-table">
          <div className="retro-table-row">
            <button className="retro-nav-button retro-glow">HOME</button>
            <button className="retro-nav-button">FORUMS</button>
            <button className="retro-nav-button">GALLERY</button>
            <button className="retro-nav-button">RANKINGS</button>
            <button className="retro-nav-button">GUESTBOOK</button>
            <button className="retro-nav-button retro-blink">NEW!!</button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="retro-table">
        <div className="retro-table-row">
          {/* Left Sidebar - now with banners instead of quick links */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            {/* Hit Counter */}
            <div className="hit-counter">
              Visitors: {totalVisitors.toString().padStart(8, '0')}
            </div>
            
            {/* Y2K Era Banners */}
            <div className="retro-banner-collection">
              <div className="retro-banner">
                <span className="retro-blink">NEW!</span>
                <img src="hamster-dance.gif" alt="Dancing Hamster" width="88" height="31" />
              </div>
              <div className="retro-banner">
                <img src="midi-enabled.gif" alt="MIDI Enabled" width="88" height="31" />
              </div>
              <div className="retro-banner">
                <img src="get-flash.gif" alt="Get Flash Player" width="88" height="31" />
              </div>
            </div>
            
            {/* Award Banner */}
            <div className="award-banner">
              <img src="award-best-site.gif" alt="Best Site Award 2000" width="100" height="100" />
            </div>
          </div>

          {/* Main Content - enhanced center content */}
          <div className="retro-table-cell" style={{ width: '60%' }}>
            <div className="retro-panel">
              <div className="text-center mb-6">
                <img 
                  src={catLogo} 
                  alt="ChronoPal" 
                  className="mx-auto mb-4 animate-pet-float" 
                  style={{ 
                    imageRendering: 'pixelated',
                    width: '150px',
                    height: '150px'
                  }} 
                />
                <div className="sparkle-text">⋆✧⋆ ⋆✧⋆ ⋆✧⋆ ⋆✧⋆ ⋆✧⋆</div>
                <h2 className="retro-title text-2xl mb-4">ChronoPal - Tamagotchi AI</h2>
                <p className="mb-4 text-xl" style={{ color: '#0ff' }}>PLAY. EVOLVE. CONNECT!</p>
                <div className="text-sm mb-3" style={{ color: '#ff0' }}>
                  Your Y2K-Ready Virtual Pet Experience
                </div>
                <button 
                  onClick={() => navigate('/login')}
                  className="retro-button retro-glow"
                >
                  Start Your Journey
                </button>
              </div>
              
              {/* News Updates - more vintage styling */}
              <div className="mt-6">
                <h3 className="retro-title text-xl mb-2">Latest Updates</h3>
                <div className="space-y-2 updates-container">
                  <div className="retro-card">
                    <div className="new-label">NEW!</div>
                    <p>🌟 Pet Evolution System Released!</p>
                    <span className="text-sm" style={{ color: '#00ffff' }}>Posted: 4/20/2000</span>
                  </div>
                  <div className="retro-card">
                    <p>🎮 Mini-games Tournament This Weekend!</p>
                    <span className="text-sm" style={{ color: '#00ffff' }}>Posted: 4/19/2000</span>
                  </div>
                  <div className="retro-card">
                    <p>💿 Download our screensaver! (3.2MB)</p>
                    <span className="text-sm" style={{ color: '#00ffff' }}>Posted: 4/15/2000</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar - replaced Top Players with more 2000s elements */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            {/* Web Badges - expanded with more Y2K web badges */}
            <div className="retro-badges">
              <div className="retro-badge">
                <img src="netscape-now.gif" alt="Netscape Now!" width="88" height="31" />
              </div>
              <div className="retro-badge">
                <img src="ie_anim.gif" alt="Internet Explorer" width="88" height="31" />
              </div>
              <div className="retro-badge">
                <img src="geocities.gif" alt="Made with GeoCities" width="88" height="31" />
              </div>
              <div className="retro-badge">
                <img src="under-construction.gif" alt="Under Construction" width="88" height="31" />
              </div>
              <div className="retro-badge">
                <img src="y2k-ready.gif" alt="Y2K Ready" width="88" height="31" />
              </div>
            </div>

            {/* Web Ring - enhanced */}
            <div className="web-ring">
              <div className="web-ring-title">Virtual Pet Web Ring</div>
              <div>
                <a href="#" className="retro-link">[Previous]</a>
                <a href="#" className="retro-link">[Next]</a>
                <a href="#" className="retro-link">[Random]</a>
                <a href="#" className="retro-link">[List]</a>
              </div>
            </div>
            
            {/* Sign Guestbook Call to Action */}
            <div className="guestbook-cta">
              <div className="guestbook-title">Sign Our Guestbook!</div>
              <img src="guestbook.gif" alt="Sign Guestbook" width="100" height="50" />
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