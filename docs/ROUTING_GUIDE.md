# Dashboard Routing Guide

## Overview

This guide explains how users are routed to different dashboards based on their roles after authentication.

## Routing Logic

The routing system determines which dashboard a user should access based on their role(s). The routing happens automatically after successful authentication.

## Route Mapping

| User Role(s) | Dashboard Route | Priority |
|--------------|----------------|----------|
| `admin` | `/admin-support.html` | Highest |
| `farmer` | `/farmer.html` | Medium |
| `buyer` | `/buyer.html` | Lowest |
| `farmer,buyer` | `/farmer.html` | Farmer prioritized |
| `admin,farmer` | `/admin-support.html` | Admin prioritized |
| `admin,buyer` | `/admin-support.html` | Admin prioritized |
| `farmer,buyer,admin` | `/admin-support.html` | Admin prioritized |

## Implementation

### Backend Routing

The routing logic is implemented in `backend/routes/auth.py`:

```python
@auth_bp.route('/dashboard-route', methods=['POST'])
def get_dashboard_route():
    # Determine dashboard route
    roles_list = [r.strip() for r in role.split(',')] if ',' in role else [role]
    
    if 'admin' in roles_list:
        dashboard = '/admin-support.html'
    elif 'farmer' in roles_list:
        dashboard = '/farmer.html'
    elif 'buyer' in roles_list:
        dashboard = '/buyer.html'
    else:
        dashboard = '/index.html'
```

### Frontend Routing

After authentication, the frontend calls the dashboard route endpoint and redirects:

```javascript
const dashboardResponse = await getDashboardRoute(firebaseUid);
redirectToDashboard(dashboardResponse.dashboard);
```

## Multi-Role Priority

When a user has multiple roles, the system uses the following priority:

1. **Admin** (highest priority)
   - If user has admin role, always route to admin dashboard
   
2. **Farmer** (medium priority)
   - If user has farmer role (and not admin), route to farmer dashboard
   
3. **Buyer** (lowest priority)
   - If user only has buyer role, route to buyer dashboard

## Examples

### Example 1: Single Role
```javascript
// User with only farmer role
role: "farmer"
→ Dashboard: /farmer.html
```

### Example 2: Multi-Role (Farmer + Buyer)
```javascript
// User who is both farmer and buyer
role: "farmer,buyer"
→ Dashboard: /farmer.html (farmer prioritized)
```

### Example 3: Admin Role
```javascript
// User with admin role (even if they have other roles)
role: "admin,farmer"
→ Dashboard: /admin-support.html (admin prioritized)
```

## Role Selection During Registration

### Email/Password Registration

Users select their role(s) during registration:
- Checkbox for "Farmer"
- Checkbox for "Buyer"
- Can select both

### Google Sign-In (Cold Start)

New users signing in with Google:
1. Complete Google authentication
2. See role selection form
3. Select role(s) and optionally phone number
4. Automatically redirected to appropriate dashboard

## Changing Dashboard

Users with multiple roles can switch dashboards by:
1. Using navigation links in the header
2. Directly accessing dashboard URLs (if authenticated)
3. Using a dashboard switcher (to be implemented)

## Protected Routes

Each dashboard should check:
1. User is authenticated (Firebase token valid)
2. User has appropriate role for that dashboard
3. User is active in database

## Future Enhancements

- [ ] Dashboard switcher component for multi-role users
- [ ] Remember last visited dashboard
- [ ] Role-based navigation menu
- [ ] Quick switch between dashboards

## Testing Routes

You can test the routing logic using the API:

```bash
# Test farmer route
curl -X POST http://localhost:5000/api/auth/dashboard-route \
  -H "Content-Type: application/json" \
  -d '{"role": "farmer"}'

# Test multi-role route
curl -X POST http://localhost:5000/api/auth/dashboard-route \
  -H "Content-Type: application/json" \
  -d '{"role": "farmer,buyer"}'

# Test admin route
curl -X POST http://localhost:5000/api/auth/dashboard-route \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

## Integration with Dashboards

To protect dashboard pages, add authentication check:

```javascript
// Check if user is authenticated
onAuthStateChange(async (user) => {
  if (!user) {
    window.location.href = '/frontend/auth.html';
    return;
  }
  
  // Get user role from backend
  const userData = await getUserProfile(user.uid);
  
  // Verify user has access to this dashboard
  const currentPage = window.location.pathname;
  if (currentPage.includes('farmer.html') && !userData.roles.includes('farmer') && !userData.roles.includes('admin')) {
    // Redirect to appropriate dashboard
    const route = await getDashboardRoute(user.uid);
    window.location.href = route.dashboard;
  }
});
```

