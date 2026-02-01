// API Configuration
// For local development, use localhost
// For production, update with your Cloud Run backend URL

const getApiBaseUrl = () => {
  // Check if we're in development or production
  if (import.meta.env.DEV) {
    // Local development - backend runs on localhost:8000
    return 'http://localhost:8000';
  }
  
  // Production - use environment variable or fallback
  return import.meta.env.VITE_API_URL || 'https://backend-XXXXX.run.app';
};

export const API_CONFIG = {
  baseURL: getApiBaseUrl(),
  timeout: 60000, // 60 seconds for script generation
  
  // WebSocket configuration
  wsURL: import.meta.env.DEV 
    ? 'ws://localhost:8000' 
    : (import.meta.env.VITE_WS_URL || 'wss://backend-XXXXX.run.app'),
};

// Access code for authentication
// In production, this would come from environment variables or user input
export const ACCESS_CODE = import.meta.env.VITE_ACCESS_CODE || 'default-code';
