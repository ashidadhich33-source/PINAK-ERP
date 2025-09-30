import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff } from 'lucide-react';
import { isOnline, addOnlineListener, addOfflineListener, removeOnlineListener, removeOfflineListener } from '../../utils/pwa';

const OfflineIndicator = () => {
  const [isOnlineStatus, setIsOnlineStatus] = useState(isOnline());

  useEffect(() => {
    const handleOnline = () => setIsOnlineStatus(true);
    const handleOffline = () => setIsOnlineStatus(false);

    addOnlineListener(handleOnline);
    addOfflineListener(handleOffline);

    return () => {
      removeOnlineListener(handleOnline);
      removeOfflineListener(handleOffline);
    };
  }, []);

  if (isOnlineStatus) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-warning-500 text-white px-4 py-2 text-center">
      <div className="flex items-center justify-center space-x-2">
        <WifiOff className="w-4 h-4" />
        <span className="text-sm font-medium">
          You're offline. Some features may not be available.
        </span>
      </div>
    </div>
  );
};

export default OfflineIndicator;