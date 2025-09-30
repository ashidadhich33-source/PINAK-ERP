import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: true,
  error: null,
};

// Action types
const ActionTypes = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case ActionTypes.LOGIN_START:
      return {
        ...state,
        loading: true,
        error: null,
      };
    
    case ActionTypes.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      };
    
    case ActionTypes.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload,
      };
    
    case ActionTypes.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };
    
    case ActionTypes.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        loading: false,
      };
    
    case ActionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    
    case ActionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
}

// Context
const AuthContext = createContext();

// Provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      if (state.token) {
        try {
          const user = await authService.getCurrentUser();
          dispatch({ type: ActionTypes.SET_USER, payload: user });
        } catch (error) {
          // Token is invalid, clear it
          localStorage.removeItem('token');
          dispatch({ type: ActionTypes.LOGOUT });
        }
      } else {
        dispatch({ type: ActionTypes.SET_LOADING, payload: false });
      }
    };

    checkAuth();
  }, [state.token]);

  // Actions
  const actions = {
    login: async (credentials) => {
      dispatch({ type: ActionTypes.LOGIN_START });
      
      try {
        const response = await authService.login(credentials);
        localStorage.setItem('token', response.access_token);
        dispatch({
          type: ActionTypes.LOGIN_SUCCESS,
          payload: {
            user: response.user,
            token: response.access_token,
          },
        });
        return response;
      } catch (error) {
        dispatch({
          type: ActionTypes.LOGIN_FAILURE,
          payload: error.message || 'Login failed',
        });
        throw error;
      }
    },
    
    logout: async () => {
      try {
        await authService.logout();
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        localStorage.removeItem('token');
        dispatch({ type: ActionTypes.LOGOUT });
      }
    },
    
    changePassword: async (passwordData) => {
      try {
        await authService.changePassword(passwordData);
        return true;
      } catch (error) {
        throw error;
      }
    },
    
    clearError: () => dispatch({ type: ActionTypes.CLEAR_ERROR }),
    
    hasPermission: (permission) => {
      if (!state.user) return false;
      if (state.user.is_superuser) return true;
      return state.user.roles?.some(role => 
        role.permissions?.some(perm => perm.name === permission)
      ) || false;
    },
    
    hasRole: (roleName) => {
      if (!state.user) return false;
      return state.user.roles?.some(role => role.name === roleName) || false;
    },
  };

  const value = {
    ...state,
    ...actions,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;