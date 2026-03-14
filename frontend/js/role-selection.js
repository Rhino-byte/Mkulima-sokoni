/**
 * Role selection form for new users (cold start handling)
 * This handles the case when a user signs in with Google for the first time
 */

/**
 * Show role selection modal/form
 */
function showRoleSelectionForm(firebaseUid, email) {
  // Create modal overlay
  const overlay = document.createElement('div');
  overlay.id = 'role-selection-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
  `;
  
  // Create modal content
  const modal = document.createElement('div');
  modal.style.cssText = `
    background: white;
    padding: 2rem;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  `;
  
  modal.innerHTML = `
    <h2 style="margin-bottom: 1rem; color: #27AE60;">Welcome to Mkulima-Bora!</h2>
    <p style="margin-bottom: 1.5rem; color: #6b7280;">
      Please select your role to get started. You can select multiple roles if applicable.
    </p>
    
    <form id="role-selection-form">
      <div style="margin-bottom: 1rem;">
        <label style="display: flex; align-items: center; margin-bottom: 0.5rem; cursor: pointer;">
          <input type="checkbox" name="role" value="farmer" id="role-farmer" style="margin-right: 0.5rem;">
          <span style="font-weight: 500;">🌾 Farmer</span>
        </label>
        <p style="margin-left: 1.5rem; color: #6b7280; font-size: 0.9rem;">
          Sell your produce directly to buyers
        </p>
      </div>
      
      <div style="margin-bottom: 1.5rem;">
        <label style="display: flex; align-items: center; margin-bottom: 0.5rem; cursor: pointer;">
          <input type="checkbox" name="role" value="buyer" id="role-buyer" style="margin-right: 0.5rem;">
          <span style="font-weight: 500;">🛒 Buyer</span>
        </label>
        <p style="margin-left: 1.5rem; color: #6b7280; font-size: 0.9rem;">
          Purchase fresh produce from farmers
        </p>
      </div>
      
      <div style="margin-bottom: 1.5rem;">
        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">
          Phone Number (Optional)
        </label>
        <input 
          type="tel" 
          name="phone_number" 
          id="phone-number"
          placeholder="+254 700 000 000"
          style="width: 100%; padding: 0.75rem; border: 1px solid #e5e7eb; border-radius: 6px;"
        >
      </div>
      
      <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
        <button 
          type="submit" 
          id="submit-role"
          style="
            flex: 1;
            padding: 0.75rem;
            background: #27AE60;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
          "
        >
          Continue
        </button>
      </div>
    </form>
  `;
  
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  
  // Handle form submission
  const form = modal.querySelector('#role-selection-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selectedRoles = Array.from(form.querySelectorAll('input[name="role"]:checked'))
      .map(checkbox => checkbox.value);
    
    if (selectedRoles.length === 0) {
      alert('Please select at least one role');
      return;
    }
    
    const phoneNumber = form.querySelector('#phone-number').value;
    const role = selectedRoles.join(','); // Multi-role support
    
    // Disable submit button
    const submitBtn = form.querySelector('#submit-role');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    
    try {
      // Complete registration
      const result = await completeRegistration(firebaseUid, email, phoneNumber, role);
      
      // Store user data
      localStorage.setItem('user', JSON.stringify(result.user));
      localStorage.setItem('userRole', role);
      
      // Remove modal
      document.body.removeChild(overlay);
      
      // Redirect to dashboard
      redirectToDashboard(result.dashboard);
    } catch (error) {
      console.error('Error completing registration:', error);
      alert('An error occurred. Please try again.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Continue';
    }
  });
  
  // Close on overlay click (optional)
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      // Prevent closing - user must select a role
      // document.body.removeChild(overlay);
    }
  });
}

/**
 * Check if user needs role selection (cold start)
 */
async function handleColdStart(authResult) {
  if (authResult.newUser) {
    // Show role selection form
    showRoleSelectionForm(authResult.firebaseUid, authResult.email);
  } else {
    // Existing user - redirect to dashboard
    if (authResult.dashboard) {
      localStorage.setItem('user', JSON.stringify(authResult.user));
      localStorage.setItem('userRole', authResult.user.role);
      redirectToDashboard(authResult.dashboard);
    }
  }
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    showRoleSelectionForm,
    handleColdStart
  };
}

