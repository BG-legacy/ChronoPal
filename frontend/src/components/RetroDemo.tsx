import React, { useState } from 'react';
import CRTEffect from './CRTEffect';
import useSounds from '../assets/sounds/useSounds';
import { SoundType } from '../assets/sounds/soundService';
import SoundButton from './SoundButton';
import QuestionButton from './QuestionButton';
import { Pet } from '../types/pet';

interface RetroDemoProps {
  pet: Pet;
}

const RetroDemo: React.FC<RetroDemoProps> = ({ pet }) => {
  const { playSound, volume, setVolume, muted, toggleMute } = useSounds();
  const [crtEnabled, setCrtEnabled] = useState(true);
  
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
  };
  
  const handleToggleCRT = () => {
    setCrtEnabled(!crtEnabled);
  };
  
  return (
    <CRTEffect enabled={crtEnabled}>
      <div className="p-6 bg-gray-900 text-green-400 min-h-screen font-mono">
        <h1 className="text-2xl mb-6">RetroChronoPal Demo</h1>
        
        {/* Pet Info */}
        <div className="mb-8 p-4 bg-gray-800 rounded">
          <h2 className="text-xl mb-4">Pet Status</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p>Name: {pet.name}</p>
              <p>Species: {pet.species}</p>
              <p>Level: {pet.level}</p>
              <p>Mood: {pet.mood}</p>
              <p>Sass Level: {pet.sass_level}</p>
              <p>Interactions: {pet.interactionCount}</p>
            </div>
            <div>
              <p>Last Fed: {new Date(pet.lastFed).toLocaleString()}</p>
              <p>Last Interaction: {new Date(pet.lastInteraction).toLocaleString()}</p>
              <p>Memories: {pet.memoryLog.length}</p>
            </div>
          </div>
        </div>
        
        <div className="mb-8">
          <h2 className="text-xl mb-4">Sound Controls</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            <SoundButton
              soundType="click"
              className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors"
            >
              Click Sound
            </SoundButton>
            <SoundButton
              soundType="beep"
              className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors"
            >
              Beep Sound
            </SoundButton>
            <SoundButton
              soundType="success"
              className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors"
            >
              Success Sound
            </SoundButton>
            <SoundButton
              soundType="error"
              className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors"
            >
              Error Sound
            </SoundButton>
            <SoundButton
              soundType="notification"
              className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors"
            >
              Notification Sound
            </SoundButton>
          </div>
          
          <div className="flex items-center gap-4 mb-4">
            <label htmlFor="volume" className="inline-block w-20">Volume:</label>
            <input
              id="volume"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              className="w-48"
            />
            <span>{Math.round(volume * 100)}%</span>
          </div>
          
          <SoundButton
            soundType="click"
            onClick={toggleMute}
            className={`px-4 py-2 rounded transition-colors ${
              muted ? 'bg-red-800 hover:bg-red-700' : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            {muted ? 'Unmute' : 'Mute'}
          </SoundButton>
        </div>
        
        <div className="mb-8">
          <h2 className="text-xl mb-4">CRT Effect</h2>
          <SoundButton
            soundType="click"
            onClick={handleToggleCRT}
            className={`px-4 py-2 rounded transition-colors ${
              crtEnabled ? 'bg-green-800 hover:bg-green-700' : 'bg-gray-800 hover:bg-gray-700'
            }`}
          >
            {crtEnabled ? 'Disable CRT Effect' : 'Enable CRT Effect'}
          </SoundButton>
        </div>
        
        <div className="mb-8">
          <h2 className="text-xl mb-4">Pet Interaction</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            <QuestionButton className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition-colors text-green-400 font-mono" />
          </div>
        </div>
        
        <div className="mt-8 p-4 bg-gray-800 rounded">
          <p>This demo shows how to use Howler.js for retro sound effects and the CRT effect component for a retro visual style.</p>
          <p className="mt-2">Click on any of the sound buttons to play the corresponding sound.</p>
          <p className="mt-2">Each button interaction automatically plays a sound using the SoundButton component.</p>
        </div>
      </div>
    </CRTEffect>
  );
};

export default RetroDemo; 