import React, { createContext, useContext, useReducer } from 'react';

// Initial state
const initialState = {
  loading: false,
  error: null,
  company: null,
  theme: 'light',
  sidebarCollapsed: false,
  notifications: [],
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_COMPANY: 'SET_COMPANY',
  SET_THEME: 'SET_THEME',
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  CLEAR_NOTIFICATIONS: 'CLEAR_NOTIFICATIONS',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ActionTypes.CLEAR_ERROR:
      return { ...state, error: null };
    
    case ActionTypes.SET_COMPANY:
      return { ...state, company: action.payload };
    
    case ActionTypes.SET_THEME:
      return { ...state, theme: action.payload };
    
    case ActionTypes.TOGGLE_SIDEBAR:
      return { ...state, sidebarCollapsed: !state.sidebarCollapsed };
    
    case ActionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload],
      };
    
    case ActionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload),
      };
    
    case ActionTypes.CLEAR_NOTIFICATIONS:
      return { ...state, notifications: [] };
    
    default:
      return state;
  }
}

// Context
const AppContext = createContext();

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions
  const actions = {
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    
    clearError: () => dispatch({ type: ActionTypes.CLEAR_ERROR }),
    
    setCompany: (company) => dispatch({ type: ActionTypes.SET_COMPANY, payload: company }),
    
    setTheme: (theme) => dispatch({ type: ActionTypes.SET_THEME, payload: theme }),
    
    toggleSidebar: () => dispatch({ type: ActionTypes.TOGGLE_SIDEBAR }),
    
    addNotification: (notification) => {
      const id = Date.now().toString();
      dispatch({
        type: ActionTypes.ADD_NOTIFICATION,
        payload: { ...notification, id },
      });
      
      // Auto remove after 5 seconds
      if (notification.autoClose !== false) {
        setTimeout(() => {
          dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id });
        }, 5000);
      }
    },
    
    removeNotification: (id) => dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id }),
    
    clearNotifications: () => dispatch({ type: ActionTypes.CLEAR_NOTIFICATIONS }),
  };

  const value = {
    ...state,
    ...actions,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// Custom hook
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export default AppContext;