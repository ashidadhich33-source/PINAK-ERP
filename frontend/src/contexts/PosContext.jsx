import React, { createContext, useContext, useReducer } from 'react';

// Initial state
const initialState = {
  session: null,
  cart: [],
  customer: null,
  paymentMethod: null,
  discount: 0,
  tax: 0,
  total: 0,
  loading: false,
  error: null,
};

// Action types
const ActionTypes = {
  SET_SESSION: 'SET_SESSION',
  ADD_TO_CART: 'ADD_TO_CART',
  REMOVE_FROM_CART: 'REMOVE_FROM_CART',
  UPDATE_CART_ITEM: 'UPDATE_CART_ITEM',
  CLEAR_CART: 'CLEAR_CART',
  SET_CUSTOMER: 'SET_CUSTOMER',
  SET_PAYMENT_METHOD: 'SET_PAYMENT_METHOD',
  SET_DISCOUNT: 'SET_DISCOUNT',
  SET_TAX: 'SET_TAX',
  CALCULATE_TOTAL: 'CALCULATE_TOTAL',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  RESET_POS: 'RESET_POS',
};

// Reducer
function posReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_SESSION:
      return { ...state, session: action.payload };
    
    case ActionTypes.ADD_TO_CART:
      const existingItem = state.cart.find(item => item.id === action.payload.id);
      if (existingItem) {
        return {
          ...state,
          cart: state.cart.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + (action.payload.quantity || 1) }
              : item
          ),
        };
      }
      return {
        ...state,
        cart: [...state.cart, { ...action.payload, quantity: action.payload.quantity || 1 }],
      };
    
    case ActionTypes.REMOVE_FROM_CART:
      return {
        ...state,
        cart: state.cart.filter(item => item.id !== action.payload),
      };
    
    case ActionTypes.UPDATE_CART_ITEM:
      return {
        ...state,
        cart: state.cart.map(item =>
          item.id === action.payload.id
            ? { ...item, ...action.payload.updates }
            : item
        ),
      };
    
    case ActionTypes.CLEAR_CART:
      return { ...state, cart: [] };
    
    case ActionTypes.SET_CUSTOMER:
      return { ...state, customer: action.payload };
    
    case ActionTypes.SET_PAYMENT_METHOD:
      return { ...state, paymentMethod: action.payload };
    
    case ActionTypes.SET_DISCOUNT:
      return { ...state, discount: action.payload };
    
    case ActionTypes.SET_TAX:
      return { ...state, tax: action.payload };
    
    case ActionTypes.CALCULATE_TOTAL:
      const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      const discountAmount = (subtotal * state.discount) / 100;
      const taxAmount = ((subtotal - discountAmount) * state.tax) / 100;
      const total = subtotal - discountAmount + taxAmount;
      return { ...state, total };
    
    case ActionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ActionTypes.CLEAR_ERROR:
      return { ...state, error: null };
    
    case ActionTypes.RESET_POS:
      return {
        ...initialState,
        session: state.session, // Keep session
      };
    
    default:
      return state;
  }
}

// Context
const PosContext = createContext();

// Provider component
export function PosProvider({ children }) {
  const [state, dispatch] = useReducer(posReducer, initialState);

  // Actions
  const actions = {
    setSession: (session) => dispatch({ type: ActionTypes.SET_SESSION, payload: session }),
    
    addToCart: (item) => {
      dispatch({ type: ActionTypes.ADD_TO_CART, payload: item });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    removeFromCart: (itemId) => {
      dispatch({ type: ActionTypes.REMOVE_FROM_CART, payload: itemId });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    updateCartItem: (itemId, updates) => {
      dispatch({ type: ActionTypes.UPDATE_CART_ITEM, payload: { id: itemId, updates } });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    clearCart: () => {
      dispatch({ type: ActionTypes.CLEAR_CART });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    setCustomer: (customer) => dispatch({ type: ActionTypes.SET_CUSTOMER, payload: customer }),
    
    setPaymentMethod: (method) => dispatch({ type: ActionTypes.SET_PAYMENT_METHOD, payload: method }),
    
    setDiscount: (discount) => {
      dispatch({ type: ActionTypes.SET_DISCOUNT, payload: discount });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    setTax: (tax) => {
      dispatch({ type: ActionTypes.SET_TAX, payload: tax });
      dispatch({ type: ActionTypes.CALCULATE_TOTAL });
    },
    
    calculateTotal: () => dispatch({ type: ActionTypes.CALCULATE_TOTAL }),
    
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    
    clearError: () => dispatch({ type: ActionTypes.CLEAR_ERROR }),
    
    resetPos: () => dispatch({ type: ActionTypes.RESET_POS }),
  };

  const value = {
    ...state,
    ...actions,
  };

  return (
    <PosContext.Provider value={value}>
      {children}
    </PosContext.Provider>
  );
}

// Custom hook
export function usePos() {
  const context = useContext(PosContext);
  if (!context) {
    throw new Error('usePos must be used within a PosProvider');
  }
  return context;
}

export default PosContext;