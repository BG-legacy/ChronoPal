import React, { useEffect, useState } from 'react';

interface NotificationProps {
  message: string;
  type: 'success' | 'warning' | 'info';
  show: boolean;
  onClose: () => void;
}

const Notification: React.FC<NotificationProps> = ({ message, type, show, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    if (show) {
      setIsVisible(true);
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);
  
  if (!isVisible) return null;
  
  const bgColor = {
    success: 'bg-green-800',
    warning: 'bg-yellow-800',
    info: 'bg-blue-800'
  }[type];
  
  const borderColor = {
    success: 'border-green-500',
    warning: 'border-yellow-500',
    info: 'border-blue-500'
  }[type];
  
  const icon = {
    success: '✓',
    warning: '⚠️',
    info: 'ℹ️'
  }[type];
  
  return (
    <div className={`fixed bottom-5 left-1/2 transform -translate-x-1/2 ${bgColor} ${borderColor} border-2 px-4 py-2 rounded-lg font-pixel text-white text-sm shadow-lg animate-pixel-pulse z-50`}>
      <div className="flex items-center">
        <span className="mr-2">{icon}</span>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default Notification; 