# Retro Effects Guide for ChronoPal

This guide explains how to use the retro sound effects and CRT visual effects in your ChronoPal application.

## Sound Effects with Howler.js

We've implemented retro sound effects using [Howler.js](https://howlerjs.com/), a powerful audio library for the web.

### Features

- Retro 8-bit style sound effects
- Volume control
- Mute/unmute functionality
- Consistent API for playing sounds across components

### Available Sounds

The following sound types are available:

- `click`: Short click sound (for button presses)
- `beep`: Simple beep sound
- `success`: Ascending tone for completion/success events
- `error`: Descending tone for errors
- `notification`: Notification sound

### Usage

#### Basic Usage with SoundButton

The easiest way to add sounds to your UI is to use the `SoundButton` component:

```tsx
import SoundButton from './components/SoundButton';

// In your component:
<SoundButton
  soundType="click"
  onClick={handleSomeAction}
  className="your-button-styles"
>
  Button Text
</SoundButton>
```

#### Using the Sound Hook

For more control, use the `useSounds` hook:

```tsx
import useSounds from './assets/sounds/useSounds';

function MyComponent() {
  const { playSound, volume, setVolume, muted, toggleMute } = useSounds();
  
  const handleAction = () => {
    playSound('success');
    // Your action code
  };
  
  return (
    <div>
      {/* Volume controls */}
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.1" 
        value={volume} 
        onChange={(e) => setVolume(parseFloat(e.target.value))} 
      />
      
      {/* Mute toggle */}
      <button onClick={toggleMute}>
        {muted ? 'Unmute' : 'Mute'}
      </button>
    </div>
  );
}
```

#### Direct API Access

For direct access to the sound API:

```tsx
import { playSound, setVolume, setMuted } from './assets/sounds/soundService';

// Play a sound
playSound('notification');

// Set volume (0-1)
setVolume(0.5);

// Mute/unmute
setMuted(true);
```

## CRT Visual Effects

Create a retro CRT monitor look with our CRT effect component.

### Features

- Scanlines
- Screen flicker
- Color distortion
- Vignette effect
- On/off animation

### Usage

Wrap any component with the `CRTEffect` component:

```tsx
import CRTEffect from './components/CRTEffect';

function MyComponent() {
  return (
    <CRTEffect enabled={true}>
      {/* Your content */}
      <div>Your app content here</div>
    </CRTEffect>
  );
}
```

The component includes a small toggle button in the bottom right corner that users can click to turn the effect on/off.

### CSS Utility Classes

You can also use these CSS classes directly in your components:

- `.crt-flicker`: Adds screen flicker effect
- `.crt-turn-on`: Plays CRT turn-on animation
- `.crt-scanline`: Adds moving scan line effect
- `.rgb-shift`: Adds RGB color shift to text

Example:

```tsx
<div className="crt-flicker rgb-shift">
  Retro Text with Effects
</div>
```

## Demo

Check out the RetroDemo component by clicking the "Show Retro Demo" button in the app header to see all these effects in action.

## Customization

### Sounds

To add custom sounds, modify the `SOUND_DATA` object in `soundService.ts`.

### CRT Effects

Customize the CRT effect by modifying the `CRTEffect.tsx` component and the CSS animations in `App.css`. 