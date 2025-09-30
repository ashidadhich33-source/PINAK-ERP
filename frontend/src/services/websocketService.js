class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
    this.listeners = new Map();
    this.isConnected = false;
  }

  connect(url = null) {
    const wsUrl = url || `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws`;
    
    try {
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = (event) => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.emit('connection', { status: 'connected', event });
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.emit('connection', { status: 'disconnected', event });
        
        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnect();
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this.emit('error', error);
    }
  }

  reconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      this.connect();
    }, delay);
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  handleMessage(data) {
    const { type, payload } = data;
    
    // Emit specific event types
    if (type) {
      this.emit(type, payload);
    }
    
    // Emit general message event
    this.emit('message', data);
  }

  // Event system
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
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  // Specific message types
  subscribe(channel) {
    this.send({
      type: 'subscribe',
      channel: channel
    });
  }

  unsubscribe(channel) {
    this.send({
      type: 'unsubscribe',
      channel: channel
    });
  }

  // Real-time features
  subscribeToNotifications() {
    this.subscribe('notifications');
  }

  subscribeToSales() {
    this.subscribe('sales');
  }

  subscribeToInventory() {
    this.subscribe('inventory');
  }

  subscribeToCustomers() {
    this.subscribe('customers');
  }

  subscribeToPos() {
    this.subscribe('pos');
  }

  // Send real-time updates
  sendNotification(notification) {
    this.send({
      type: 'notification',
      payload: notification
    });
  }

  sendSalesUpdate(sale) {
    this.send({
      type: 'sales_update',
      payload: sale
    });
  }

  sendInventoryUpdate(item) {
    this.send({
      type: 'inventory_update',
      payload: item
    });
  }

  sendCustomerUpdate(customer) {
    this.send({
      type: 'customer_update',
      payload: customer
    });
  }

  sendPosUpdate(transaction) {
    this.send({
      type: 'pos_update',
      payload: transaction
    });
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;