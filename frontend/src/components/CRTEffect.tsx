import React, { useState, useEffect } from 'react';

interface CRTEffectProps {
  children: React.ReactNode;
  enabled?: boolean;
}

const CRTEffect: React.FC<CRTEffectProps> = ({ children, enabled = true }) => {
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [isOn, setIsOn] = useState(true);

  // Initialize based on prop value
  useEffect(() => {
    setIsEnabled(enabled);
  }, [enabled]);

  const toggleEffect = () => {
    // Turn off with animation if going from enabled to disabled
    if (isEnabled) {
      setIsOn(false);
      // After animation completes, disable the effect
      setTimeout(() => {
        setIsEnabled(false);
      }, 1000);
    } else {
      // Turn on directly
      setIsEnabled(true);
      setIsOn(true);
    }
  };

  if (!isEnabled && !isOn) {
    return <>{children}</>;
  }

  return (
    <div className="relative w-full h-full">
      {/* CRT Container */}
      <div 
        className={`relative w-full h-full overflow-hidden rounded-lg ${isOn ? 'crt-turn-on' : ''} ${isEnabled ? 'crt-flicker crt-scanline' : ''}`}
        style={{
          boxShadow: '0 0 15px rgba(10, 255, 90, 0.4)',
          animation: isEnabled ? 'textShadow 1.6s infinite' : 'none'
        }}
      >
        {/* Original content */}
        <div 
          className="w-full h-full"
          style={{ 
            filter: isEnabled ? 'brightness(1.2) contrast(1.1) saturate(1.2)' : 'none'
          }}
        >
          {children}
        </div>
        
        {/* Scanlines overlay */}
        {isEnabled && (
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              background: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%)',
              backgroundSize: '100% 4px',
              mixBlendMode: 'overlay',
              opacity: 0.35
            }}
          />
        )}
        
        {/* Vignette effect */}
        {isEnabled && (
          <div 
            className="absolute inset-0 pointer-events-none"
            style={{
              background: 'radial-gradient(circle at center, transparent 60%, rgba(0, 0, 0, 0.7) 100%)',
              mixBlendMode: 'multiply'
            }}
          />
        )}
      </div>
      
      {/* Toggle button */}
      <button 
        onClick={toggleEffect}
        className="absolute bottom-2 right-2 bg-gray-800 text-xs text-green-400 px-2 py-1 rounded z-10 opacity-50 hover:opacity-100 transition-opacity rgb-shift"
      >
        CRT: {isEnabled ? 'ON' : 'OFF'}
      </button>
      
      {/* Note: The textShadow animation keyframes are now defined in App.css */}
    </div>
  );
};

export default CRTEffect; 