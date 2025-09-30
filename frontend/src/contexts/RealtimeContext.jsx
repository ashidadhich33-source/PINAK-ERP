import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';
import { useApp } from './AppContext';
import websocketService from '../services/websocketService';

const RealtimeContext = createContext();

export function RealtimeProvider({ children }) {
  const { isAuthenticated, user } = useAuth();
  const { addNotification } = useApp();
  const [isConnected, setIsConnected] = useState(false);
  const [realtimeData, setRealtimeData] = useState({
    notifications: [],
    sales: [],
    inventory: [],
    customers: [],
    pos: [],
  });

  // Connect to WebSocket when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      websocketService.connect();
      
      // Connection event listeners
      websocketService.on('connection', (data) => {
        setIsConnected(data.status === 'connected');
      });

      websocketService.on('error', (error) => {
        console.error('WebSocket error:', error);
        addNotification({
          type: 'danger',
          title: 'Connection Error',
          message: 'Real-time connection failed',
        });
      });

      // Subscribe to real-time channels
      websocketService.subscribeToNotifications();
      websocketService.subscribeToSales();
      websocketService.subscribeToInventory();
      websocketService.subscribeToCustomers();
      websocketService.subscribeToPos();

      // Message event listeners
      websocketService.on('notification', (notification) => {
        setRealtimeData(prev => ({
          ...prev,
          notifications: [notification, ...prev.notifications.slice(0, 49)] // Keep last 50
        }));
        
        addNotification({
          type: notification.type || 'info',
          title: notification.title,
          message: notification.message,
        });
      });

      websocketService.on('sales_update', (sale) => {
        setRealtimeData(prev => ({
          ...prev,
          sales: [sale, ...prev.sales.slice(0, 49)]
        }));
      });

      websocketService.on('inventory_update', (item) => {
        setRealtimeData(prev => ({
          ...prev,
          inventory: [item, ...prev.inventory.slice(0, 49)]
        }));
      });

      websocketService.on('customer_update', (customer) => {
        setRealtimeData(prev => ({
          ...prev,
          customers: [customer, ...prev.customers.slice(0, 49)]
        }));
      });

      websocketService.on('pos_update', (transaction) => {
        setRealtimeData(prev => ({
          ...prev,
          pos: [transaction, ...prev.pos.slice(0, 49)]
        }));
      });

    } else {
      // Disconnect when not authenticated
      websocketService.disconnect();
      setIsConnected(false);
    }

    return () => {
      websocketService.disconnect();
    };
  }, [isAuthenticated, user]);

  // Real-time actions
  const actions = {
    // Send notifications
    sendNotification: (notification) => {
      websocketService.sendNotification(notification);
    },

    // Send sales updates
    sendSalesUpdate: (sale) => {
      websocketService.sendSalesUpdate(sale);
    },

    // Send inventory updates
    sendInventoryUpdate: (item) => {
      websocketService.sendInventoryUpdate(item);
    },

    // Send customer updates
    sendCustomerUpdate: (customer) => {
      websocketService.sendCustomerUpdate(customer);
    },

    // Send POS updates
    sendPosUpdate: (transaction) => {
      websocketService.sendPosUpdate(transaction);
    },

    // Clear real-time data
    clearNotifications: () => {
      setRealtimeData(prev => ({
        ...prev,
        notifications: []
      }));
    },

    clearSales: () => {
      setRealtimeData(prev => ({
        ...prev,
        sales: []
      }));
    },

    clearInventory: () => {
      setRealtimeData(prev => ({
        ...prev,
        inventory: []
      }));
    },

    clearCustomers: () => {
      setRealtimeData(prev => ({
        ...prev,
        customers: []
      }));
    },

    clearPos: () => {
      setRealtimeData(prev => ({
        ...prev,
        pos: []
      }));
    },

    // Reconnect
    reconnect: () => {
      websocketService.connect();
    },

    // Get real-time data
    getNotifications: () => realtimeData.notifications,
    getSales: () => realtimeData.sales,
    getInventory: () => realtimeData.inventory,
    getCustomers: () => realtimeData.customers,
    getPos: () => realtimeData.pos,
  };

  const value = {
    isConnected,
    realtimeData,
    ...actions,
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
}

export default RealtimeContext;