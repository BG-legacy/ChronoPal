import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/RetroStyles.css';
import { usePet } from '../contexts/PetContext';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { createPet } = usePet();
  const [onlineUsers] = React.useState(Math.floor(Math.random() * 100) + 50);
  const [totalVisitors] = React.useState(Math.floor(Math.random() * 100000) + 10000);

  const handleStartJourney = async () => {
    try {
      await createPet({
        name: 'ChronoPal',
        species: 'Digital',
        level: 1,
        experience: 0,
        lastFed: new Date().toISOString(),
        lastPlayed: new Date().toISOString(),
        lastCleaned: new Date().toISOString(),
        evolution: 'BABY',
        mood: 'happy',
        hunger: 100,
        cleanliness: 100,
        happiness: 100,
        intelligence: 50
      });
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to create pet:', error);
    }
  };

  return (
    <div className="retro-container">
      {/* Browser Notice */}
      <div className="retro-browser-notice">
        Best viewed in Netscape Navigator 4.0 at 800x600 resolution
      </div>

      {/* Marquee Announcement */}
      <div className="retro-marquee">
        <span>🌟 Welcome to ChronoPal 2000 - Your Time-Traveling Digital Pet! 🌟 New Features Coming Soon! 🌟 Join Our Community! 🌟 Sign Our Guestbook! 🌟</span>
      </div>

      {/* Header with User Counter */}
      <div className="retro-header">
        <div className="flex justify-between items-center">
          <h1 className="retro-title retro-glow text-3xl">ChronoPal 2000</h1>
          <div className="retro-counter">
            <span className="retro-blink">●</span> {onlineUsers} Users Online
          </div>
        </div>
      </div>

      {/* Navigation Panel */}
      <div className="retro-panel">
        <div className="retro-table">
          <div className="retro-table-row">
            <button className="retro-nav-button">HOME</button>
            <button className="retro-nav-button">FORUMS</button>
            <button className="retro-nav-button">GALLERY</button>
            <button className="retro-nav-button">RANKINGS</button>
            <button className="retro-nav-button">GUESTBOOK</button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="retro-table">
        <div className="retro-table-row">
          {/* Left Sidebar */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            <div className="retro-panel">
              <h3 className="retro-title text-xl mb-4">Quick Links</h3>
              <div className="flex flex-col space-y-2">
                <Link to="/profile" className="retro-link">» My Profile</Link>
                <Link to="/pets" className="retro-link">» My Pets</Link>
                <Link to="/achievements" className="retro-link">» Achievements</Link>
                <Link to="/shop" className="retro-link">» Pet Shop</Link>
              </div>
            </div>

            {/* Hit Counter */}
            <div className="hit-counter">
              Visitors: {totalVisitors.toString().padStart(8, '0')}
            </div>
          </div>

          {/* Main Content */}
          <div className="retro-table-cell" style={{ width: '60%' }}>
            <div className="retro-panel">
              <h2 className="retro-title text-2xl mb-4">Welcome to ChronoPal 2000!</h2>
              <div className="text-center mb-6">
                <img src="/chronopal-logo.png" alt="ChronoPal" className="mx-auto mb-4" style={{ imageRendering: 'pixelated' }} />
                <button onClick={handleStartJourney} className="retro-button retro-glow">
                  START YOUR JOURNEY!
                </button>
              </div>
              
              {/* News Updates */}
              <div className="mt-6">
                <h3 className="retro-title text-xl mb-2">Latest Updates</h3>
                <div className="space-y-2">
                  <div className="retro-card">
                    <p className="retro-blink">NEW!</p>
                    <p>🌟 Pet Evolution System Released!</p>
                    <span className="text-sm" style={{ color: '#00ffff' }}>Posted: 4/20/2000</span>
                  </div>
                  <div className="retro-card">
                    <p>🎮 Mini-games Tournament This Weekend!</p>
                    <span className="text-sm" style={{ color: '#00ffff' }}>Posted: 4/19/2000</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="retro-table-cell" style={{ width: '20%' }}>
            <div className="retro-panel">
              <h3 className="retro-title text-xl mb-4">Top Players</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span style={{ color: '#ff0' }}>CoolDude2000</span>
                  <span className="retro-glow">Lvl 99</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#ff0' }}>PetMaster</span>
                  <span>Lvl 95</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#ff0' }}>ChronoKing</span>
                  <span>Lvl 92</span>
                </div>
              </div>
            </div>

            {/* Web Badges */}
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
            </div>

            {/* Web Ring */}
            <div className="web-ring">
              <div className="web-ring-title">Virtual Pet Web Ring</div>
              <div>
                <a href="#" className="retro-link">[Previous]</a>
                <a href="#" className="retro-link">[Next]</a>
                <a href="#" className="retro-link">[Random]</a>
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
        <div style={{ fontSize: '10px', marginTop: '5px' }}>
          Last updated: 04/20/2000 | Optimized for 800x600
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