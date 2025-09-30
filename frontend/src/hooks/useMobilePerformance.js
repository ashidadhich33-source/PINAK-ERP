import { useState, useEffect, useCallback, useRef } from 'react';

// Hook for mobile performance optimization
export const useMobilePerformance = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [isLowMemory, setIsLowMemory] = useState(false);
  const [batteryLevel, setBatteryLevel] = useState(null);
  const [isCharging, setIsCharging] = useState(false);

  useEffect(() => {
    // Detect mobile device
    const checkMobile = () => {
      const userAgent = navigator.userAgent;
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
      const isTouchDevice = 'ontouchstart' in window;
      setIsMobile(isMobileDevice || isTouchDevice);
    };

    // Detect slow connection
    const checkConnection = () => {
      if ('connection' in navigator) {
        const connection = navigator.connection;
        const isSlow = connection.effectiveType === 'slow-2g' || 
                      connection.effectiveType === '2g' ||
                      connection.downlink < 1;
        setIsSlowConnection(isSlow);
      }
    };

    // Detect low memory
    const checkMemory = () => {
      if ('deviceMemory' in navigator) {
        const memory = navigator.deviceMemory;
        setIsLowMemory(memory < 4); // Less than 4GB
      }
    };

    // Monitor battery
    const monitorBattery = () => {
      if ('getBattery' in navigator) {
        navigator.getBattery().then((battery) => {
          setBatteryLevel(battery.level);
          setIsCharging(battery.charging);
          
          const updateBattery = () => {
            setBatteryLevel(battery.level);
            setIsCharging(battery.charging);
          };
          
          battery.addEventListener('levelchange', updateBattery);
          battery.addEventListener('chargingchange', updateBattery);
        });
      }
    };

    checkMobile();
    checkConnection();
    checkMemory();
    monitorBattery();

    // Listen for connection changes
    if ('connection' in navigator) {
      const connection = navigator.connection;
      connection.addEventListener('change', checkConnection);
    }

    return () => {
      if ('connection' in navigator) {
        const connection = navigator.connection;
        connection.removeEventListener('change', checkConnection);
      }
    };
  }, []);

  return {
    isMobile,
    isSlowConnection,
    isLowMemory,
    batteryLevel,
    isCharging,
    shouldOptimize: isMobile || isSlowConnection || isLowMemory
  };
};

// Hook for lazy loading with intersection observer
export const useLazyLoading = (options = {}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (!hasLoaded) {
            setHasLoaded(true);
          }
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [hasLoaded, options]);

  return { elementRef, isVisible, hasLoaded };
};

// Hook for virtual scrolling
export const useVirtualScroll = (items, itemHeight, containerHeight) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerRef, setContainerRef] = useState(null);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );

  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;
  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  useEffect(() => {
    const container = containerRef;
    if (!container) return;

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [containerRef, handleScroll]);

  return {
    visibleItems,
    offsetY,
    totalHeight,
    setContainerRef
  };
};

// Hook for image optimization
export const useImageOptimization = (src, options = {}) => {
  const [optimizedSrc, setOptimizedSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    quality = 0.8,
    format = 'webp',
    width,
    height,
    lazy = true
  } = options;

  useEffect(() => {
    if (!src) return;

    const optimizeImage = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Create optimized image URL
        let optimizedUrl = src;
        
        // Add quality parameter if supported
        if (src.includes('?')) {
          optimizedUrl += `&q=${quality}`;
        } else {
          optimizedUrl += `?q=${quality}`;
        }

        // Add format parameter if supported
        if (format !== 'webp' || !src.includes('format=')) {
          optimizedUrl += `&format=${format}`;
        }

        // Add dimensions if specified
        if (width) optimizedUrl += `&w=${width}`;
        if (height) optimizedUrl += `&h=${height}`;

        setOptimizedSrc(optimizedUrl);
      } catch (err) {
        setError(err);
        setOptimizedSrc(src); // Fallback to original
      } finally {
        setIsLoading(false);
      }
    };

    optimizeImage();
  }, [src, quality, format, width, height]);

  return {
    src: optimizedSrc,
    isLoading,
    error
  };
};

// Hook for touch gestures
export const useTouchGestures = (options = {}) => {
  const [gesture, setGesture] = useState(null);
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);
  const elementRef = useRef(null);

  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    onTap,
    onLongPress,
    longPressDelay = 500
  } = options;

  const handleTouchStart = useCallback((e) => {
    setTouchStart(e.targetTouches[0]);
    setTouchEnd(null);
  }, []);

  const handleTouchMove = useCallback((e) => {
    setTouchEnd(e.targetTouches[0]);
  }, []);

  const handleTouchEnd = useCallback((e) => {
    if (!touchStart || !touchEnd) return;

    const deltaX = touchStart.clientX - touchEnd.clientX;
    const deltaY = touchStart.clientY - touchEnd.clientY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    // Determine gesture type
    if (distance < 10) {
      // Tap
      if (onTap) {
        onTap(e);
      }
      setGesture('tap');
    } else if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      if (deltaX > 0) {
        if (onSwipeLeft) onSwipeLeft(e);
        setGesture('swipeLeft');
      } else {
        if (onSwipeRight) onSwipeRight(e);
        setGesture('swipeRight');
      }
    } else {
      // Vertical swipe
      if (deltaY > 0) {
        if (onSwipeUp) onSwipeUp(e);
        setGesture('swipeUp');
      } else {
        if (onSwipeDown) onSwipeDown(e);
        setGesture('swipeDown');
      }
    }
  }, [touchStart, touchEnd, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, onTap]);

  const handleLongPress = useCallback((e) => {
    if (onLongPress) {
      onLongPress(e);
    }
    setGesture('longPress');
  }, [onLongPress]);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    let longPressTimer;

    const startLongPress = () => {
      longPressTimer = setTimeout(() => {
        handleLongPress();
      }, longPressDelay);
    };

    const cancelLongPress = () => {
      clearTimeout(longPressTimer);
    };

    element.addEventListener('touchstart', handleTouchStart);
    element.addEventListener('touchstart', startLongPress);
    element.addEventListener('touchmove', handleTouchMove);
    element.addEventListener('touchmove', cancelLongPress);
    element.addEventListener('touchend', handleTouchEnd);
    element.addEventListener('touchend', cancelLongPress);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchstart', startLongPress);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchmove', cancelLongPress);
      element.removeEventListener('touchend', handleTouchEnd);
      element.removeEventListener('touchend', cancelLongPress);
      clearTimeout(longPressTimer);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, handleLongPress, longPressDelay]);

  return {
    elementRef,
    gesture,
    touchStart,
    touchEnd
  };
};

// Hook for mobile-specific optimizations
export const useMobileOptimizations = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [isActive, setIsActive] = useState(true);
  const [isBackground, setIsBackground] = useState(false);

  useEffect(() => {
    // Handle visibility change
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
      setIsActive(!document.hidden);
    };

    // Handle page focus/blur
    const handleFocus = () => setIsActive(true);
    const handleBlur = () => setIsActive(false);

    // Handle app state changes
    const handleAppStateChange = () => {
      if (document.hidden) {
        setIsBackground(true);
      } else {
        setIsBackground(false);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleAppStateChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('visibilitychange', handleAppStateChange);
    };
  }, []);

  return {
    isVisible,
    isActive,
    isBackground,
    shouldPause: !isVisible || !isActive || isBackground
  };
};

// Hook for memory management
export const useMemoryManagement = () => {
  const [memoryUsage, setMemoryUsage] = useState(null);
  const [isLowMemory, setIsLowMemory] = useState(false);

  useEffect(() => {
    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = performance.memory;
        setMemoryUsage({
          used: memory.usedJSHeapSize,
          total: memory.totalJSHeapSize,
          limit: memory.jsHeapSizeLimit
        });
        
        // Consider low memory if using more than 80% of limit
        const usagePercentage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
        setIsLowMemory(usagePercentage > 80);
      }
    };

    checkMemory();
    const interval = setInterval(checkMemory, 5000);

    return () => clearInterval(interval);
  }, []);

  const clearCache = useCallback(() => {
    // Clear various caches
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => {
          caches.delete(name);
        });
      });
    }

    // Clear localStorage if needed
    if (isLowMemory) {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('temp_') || key.startsWith('cache_')) {
          localStorage.removeItem(key);
        }
      });
    }
  }, [isLowMemory]);

  return {
    memoryUsage,
    isLowMemory,
    clearCache
  };
};