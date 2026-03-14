/**
 * Profile management module for Mkulima-Bora
 * Handles profile loading, saving, and form management
 */

// API base URL - use environment-aware configuration
let API_BASE_URL;
if (typeof window !== 'undefined' && window.API_BASE_URL) {
  API_BASE_URL = window.API_BASE_URL;
} else {
  const isProduction = typeof window !== 'undefined' && 
    window.location.hostname !== 'localhost' && 
    window.location.hostname !== '127.0.0.1';
  API_BASE_URL = isProduction ? '/api' : 'http://localhost:5000/api';
}

/**
 * Load farmer profile
 */
async function loadFarmerProfile(firebaseUid) {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/farmer/${firebaseUid}`);
    const data = await response.json();
    
    if (data.success && data.profile) {
      return data.profile;
    }
    return null;
  } catch (error) {
    console.error('Error loading farmer profile:', error);
    return null;
  }
}

/**
 * Load buyer profile
 */
async function loadBuyerProfile(firebaseUid) {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/buyer/${firebaseUid}`);
    const data = await response.json();
    
    if (data.success && data.profile) {
      return data.profile;
    }
    return null;
  } catch (error) {
    console.error('Error loading buyer profile:', error);
    return null;
  }
}

/**
 * Save farmer profile
 */
async function saveFarmerProfile(firebaseUid, profileData) {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/farmer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        firebase_uid: firebaseUid,
        ...profileData
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to save farmer profile');
    }
    
    return data;
  } catch (error) {
    console.error('Error saving farmer profile:', error);
    throw error;
  }
}

/**
 * Save buyer profile
 */
async function saveBuyerProfile(firebaseUid, profileData) {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/buyer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        firebase_uid: firebaseUid,
        ...profileData
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to save buyer profile');
    }
    
    return data;
  } catch (error) {
    console.error('Error saving buyer profile:', error);
    throw error;
  }
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    return JSON.parse(userStr);
  }
  return null;
}

/**
 * Get Firebase UID from current user
 */
function getFirebaseUid() {
  const user = getCurrentUser();
  if (user && user.firebase_uid) {
    return user.firebase_uid;
  }
  
  // Try to get from stored user data
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      const userData = JSON.parse(userStr);
      if (userData.firebase_uid) {
        return userData.firebase_uid;
      }
    } catch (e) {
      console.error('Error parsing user data:', e);
    }
  }
  
  // Try Firebase auth if available
  if (typeof firebase !== 'undefined' && firebase.auth) {
    const currentUser = firebase.auth().currentUser;
    if (currentUser) {
      return currentUser.uid;
    }
  }
  
  return null;
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadFarmerProfile,
    loadBuyerProfile,
    saveFarmerProfile,
    saveBuyerProfile,
    getCurrentUser,
    getFirebaseUid
  };
}

