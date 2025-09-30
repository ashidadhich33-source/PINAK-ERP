class CrossPlatformService {
  constructor() {
    this.platform = this.detectPlatform();
    this.capabilities = this.detectCapabilities();
    this.listeners = new Map();
  }

  detectPlatform() {
    const userAgent = navigator.userAgent;
    
    if (/iPad|iPhone|iPod/.test(userAgent)) {
      return 'ios';
    } else if (/Android/.test(userAgent)) {
      return 'android';
    } else if (/Windows/.test(userAgent)) {
      return 'windows';
    } else if (/Mac/.test(userAgent)) {
      return 'mac';
    } else if (/Linux/.test(userAgent)) {
      return 'linux';
    } else {
      return 'web';
    }
  }

  detectCapabilities() {
    return {
      // PWA capabilities
      pwa: 'serviceWorker' in navigator && 'PushManager' in window,
      
      // Touch capabilities
      touch: 'ontouchstart' in window,
      
      // Device capabilities
      camera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
      microphone: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
      geolocation: 'geolocation' in navigator,
      vibration: 'vibrate' in navigator,
      
      // Storage capabilities
      localStorage: typeof Storage !== 'undefined',
      indexedDB: 'indexedDB' in window,
      webSQL: 'openDatabase' in window,
      
      // Network capabilities
      online: 'onLine' in navigator,
      connection: 'connection' in navigator,
      
      // Battery capabilities
      battery: 'getBattery' in navigator,
      
      // File capabilities
      fileAPI: 'File' in window && 'FileReader' in window,
      dragDrop: 'draggable' in document.createElement('div'),
      
      // WebRTC capabilities
      webrtc: 'RTCPeerConnection' in window,
      
      // WebGL capabilities
      webgl: this.checkWebGL(),
      
      // WebAssembly capabilities
      wasm: 'WebAssembly' in window
    };
  }

  checkWebGL() {
    try {
      const canvas = document.createElement('canvas');
      return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
    } catch (e) {
      return false;
    }
  }

  // Platform-specific optimizations
  getOptimizations() {
    const optimizations = {
      ios: {
        viewport: 'width=device-width, initial-scale=1, viewport-fit=cover',
        touchAction: 'manipulation',
        userSelect: 'none',
        webkitUserSelect: 'none',
        webkitTouchCallout: 'none',
        webkitTapHighlightColor: 'transparent'
      },
      android: {
        viewport: 'width=device-width, initial-scale=1',
        touchAction: 'manipulation',
        userSelect: 'none',
        webkitUserSelect: 'none'
      },
      web: {
        viewport: 'width=device-width, initial-scale=1',
        touchAction: 'auto'
      }
    };

    return optimizations[this.platform] || optimizations.web;
  }

  // Device-specific features
  getDeviceFeatures() {
    const features = {
      ios: {
        safeArea: true,
        statusBar: true,
        homeIndicator: true,
        hapticFeedback: true,
        biometrics: true
      },
      android: {
        statusBar: true,
        navigationBar: true,
        hapticFeedback: true,
        biometrics: true,
        backButton: true
      },
      web: {
        keyboard: true,
        mouse: true,
        scroll: true
      }
    };

    return features[this.platform] || features.web;
  }

  // Platform-specific styling
  getPlatformStyles() {
    const styles = {
      ios: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSize: '16px', // Prevents zoom on input focus
        touchAction: 'manipulation',
        webkitAppearance: 'none'
      },
      android: {
        fontFamily: 'Roboto, sans-serif',
        fontSize: '16px',
        touchAction: 'manipulation'
      },
      web: {
        fontFamily: 'system-ui, -apple-system, sans-serif',
        fontSize: '14px'
      }
    };

    return styles[this.platform] || styles.web;
  }

  // Event handling
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  // Platform-specific utilities
  isIOS() {
    return this.platform === 'ios';
  }

  isAndroid() {
    return this.platform === 'android';
  }

  isMobile() {
    return this.isIOS() || this.isAndroid();
  }

  isDesktop() {
    return !this.isMobile();
  }

  // Capability checks
  hasCapability(capability) {
    return this.capabilities[capability] || false;
  }

  // Platform-specific implementations
  async requestPermission(permission) {
    if (!this.hasCapability(permission)) {
      throw new Error(`Permission ${permission} not supported on this platform`);
    }

    switch (permission) {
      case 'camera':
        return await this.requestCameraPermission();
      case 'microphone':
        return await this.requestMicrophonePermission();
      case 'geolocation':
        return await this.requestGeolocationPermission();
      case 'notifications':
        return await this.requestNotificationPermission();
      default:
        throw new Error(`Unknown permission: ${permission}`);
    }
  }

  async requestCameraPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      return false;
    }
  }

  async requestMicrophonePermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      return false;
    }
  }

  async requestGeolocationPermission() {
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        () => resolve(true),
        () => resolve(false),
        { timeout: 1000 }
      );
    });
  }

  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  // Platform-specific UI adjustments
  adjustForPlatform() {
    const optimizations = this.getOptimizations();
    const styles = this.getPlatformStyles();

    // Apply viewport meta tag
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', optimizations.viewport);
    }

    // Apply platform-specific styles
    const root = document.documentElement;
    Object.entries(styles).forEach(([property, value]) => {
      root.style.setProperty(`--${property}`, value);
    });

    // Add platform class to body
    document.body.classList.add(`platform-${this.platform}`);
  }

  // Get platform info
  getPlatformInfo() {
    return {
      platform: this.platform,
      capabilities: this.capabilities,
      userAgent: navigator.userAgent,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
  }
}

// Create singleton instance
const crossPlatformService = new CrossPlatformService();

export default crossPlatformService;