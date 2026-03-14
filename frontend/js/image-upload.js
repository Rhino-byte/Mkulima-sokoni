/**
 * Image upload module for Cloudinary integration
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
 * Upload image file to Cloudinary
 * @param {File} file - Image file to upload
 * @param {string} folder - Cloudinary folder (optional)
 * @returns {Promise<Object>} Upload result with image URL
 */
async function uploadImageFile(file, folder = 'mkulima-bora') {
  try {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('folder', folder);
    
    const response = await fetch(`${API_BASE_URL}/uploads/image`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to upload image');
    }
    
    return data;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
}

/**
 * Upload image from URL to Cloudinary
 * @param {string} imageUrl - URL of the image
 * @param {string} folder - Cloudinary folder (optional)
 * @returns {Promise<Object>} Upload result with image URL
 */
async function uploadImageFromUrl(imageUrl, folder = 'mkulima-bora') {
  try {
    const response = await fetch(`${API_BASE_URL}/uploads/image/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: imageUrl,
        folder: folder
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to upload image from URL');
    }
    
    return data;
  } catch (error) {
    console.error('Error uploading image from URL:', error);
    throw error;
  }
}

/**
 * Upload profile image
 * @param {File} file - Image file to upload
 * @param {string} userType - 'farmer' or 'buyer'
 * @returns {Promise<string>} Image URL
 */
async function uploadProfileImage(file, userType = 'profile') {
  try {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('user_type', userType);
    
    const response = await fetch(`${API_BASE_URL}/uploads/profile-image`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to upload profile image');
    }
    
    return data.image_url;
  } catch (error) {
    console.error('Error uploading profile image:', error);
    throw error;
  }
}

/**
 * Create image preview
 * @param {File} file - Image file
 * @returns {Promise<string>} Data URL for preview
 */
function createImagePreview(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Validate image file
 * @param {File} file - Image file to validate
 * @returns {Object} Validation result
 */
function validateImageFile(file) {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  
  if (!file) {
    return { valid: false, error: 'No file selected' };
  }
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Invalid file type. Allowed: JPG, PNG, GIF, WEBP' };
  }
  
  if (file.size > maxSize) {
    return { valid: false, error: 'File size too large. Maximum: 5MB' };
  }
  
  return { valid: true };
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    uploadImageFile,
    uploadImageFromUrl,
    uploadProfileImage,
    createImagePreview,
    validateImageFile
  };
}

