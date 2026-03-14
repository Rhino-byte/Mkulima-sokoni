/**
 * Configuration file for Mkulima-Bora frontend
 * Handles API base URL configuration for different environments
 */

// Detect environment and set API base URL
// For production/Vercel: use relative URLs or environment variable
// For development: use localhost

function getApiBaseUrl() {
  // Check if we're in production (Vercel deployment)
  const isProduction = window.location.hostname !== 'localhost' && 
                       window.location.hostname !== '127.0.0.1';
  
  // Check for environment variable (set in Vercel or build process)
  if (window.API_BASE_URL) {
    return window.API_BASE_URL;
  }
  
  // For production, use relative URLs (same origin)
  if (isProduction) {
    // If backend is on same domain, use relative path
    // If backend is on different domain, you need to set API_BASE_URL in Vercel
    return '/api';
  }
  
  // For development, use localhost
  return 'http://localhost:5000/api';
}

// Export API base URL
const API_BASE_URL = getApiBaseUrl();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_BASE_URL };
}

