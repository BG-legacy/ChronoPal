import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import RetroDemo from './components/RetroDemo';
import SoundButton from './components/SoundButton';
import { PetProvider } from './contexts/PetContext';
import { usePet } from './contexts/PetContext';
import LandingPage from './components/LandingPage';

function AppContent() {
  const [showDemo, setShowDemo] = useState(false);
  const { pet, loading, error } = usePet();

  const handleToggleDemo = () => {
    setShowDemo(!showDemo);
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="text-center text-white">
          <h1 className="text-4xl font-bold mb-4">Loading...</h1>
          <p className="text-xl">Please wait while we fetch your pet data</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center text-white">
          <h1 className="text-4xl font-bold mb-4">Error</h1>
          <p className="text-xl text-red-500">{error.message}</p>
        </div>
      );
    }

    if (!pet) {
      return <LandingPage />;
    }

    return showDemo ? <RetroDemo pet={pet} /> : <Dashboard pet={pet} />;
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Retro Background Effects */}
      <div className="retro-bg" />
      <div className="noise" />
      <div className="crt-glow" />
      
      {/* Content */}
      <div className="z-10 w-full max-w-5xl">
        {renderContent()}
      </div>

      {/* Toggle Demo Button */}
      {pet && (
        <SoundButton 
          soundType={showDemo ? 'beep' : 'notification'}
          onClick={handleToggleDemo}
          className="absolute top-4 right-4 bg-purple-700 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors z-50"
        >
          {showDemo ? 'Show Dashboard' : 'Show Retro Demo'}
        </SoundButton>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <PetProvider>
        <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/dashboard" element={<AppContent />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </PetProvider>
    </Router>
  );
}

export default App;
