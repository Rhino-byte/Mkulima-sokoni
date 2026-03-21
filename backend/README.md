# Backend API - Mkulima-Bora

Python Flask backend for Mkulima-Bora authentication system.

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database connection utilities
├── migrate.py             # Database migration script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── models/
│   └── user.py           # User model and database operations
├── routes/
│   └── auth.py           # Authentication routes
├── auth/
│   └── firebase_auth.py  # Firebase authentication utilities
└── migrations/
    └── 001_create_users_table.sql  # Database migration SQL
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Set `DATABASE_URL` with your Neon database connection string
   - Configure other settings as needed

3. **Run Migration**
   ```bash
   python migrate.py
   ```

4. **Start Server**
   ```bash
   python app.py
   ```

## API Endpoints

See [API Routes Documentation](../docs/API_ROUTES.md) for detailed endpoint documentation.

### Marketplace (products)

- `GET /api/products/meta` — lightweight aggregate for polling: `{ "count": number, "latest_updated_at": string | null }`. Query params: `status` (default `active`), optional `category`, `product_type` (same filters as the listing query).
- `GET /api/products` — full active (or filtered) listings as a JSON array (unchanged).
- `PUT /api/products/<id>/status` — update listing status; requires JSON body `{ "firebase_uid": "...", "status": "active" | "draft" | "sold_out" | "archived" }` (seller must own the product). Aliases: `sold` → `sold_out`, `paused` → `archived`.

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/google-signin` - Google sign-in
- `POST /api/auth/complete-registration` - Complete registration (cold start)
- `POST /api/auth/dashboard-route` - Get dashboard route based on role
- `GET /api/auth/user/<firebase_uid>` - Get user by Firebase UID

### Health Check

- `GET /api/health` - API health status

## Environment Variables

- `DATABASE_URL` - Neon database connection string (required). Prefer the **pooler** endpoint (hostname contains `-pooler`) for serverless hosts like Vercel so connections are multiplexed; the app also uses a small in-process `ThreadedConnectionPool` when possible.
- `SECRET_KEY` - Flask secret key
- `DEBUG` - Debug mode (True/False)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `FIREBASE_SERVICE_ACCOUNT_PATH` - Path to Firebase service account JSON file (optional)
- `ADMIN_FIREBASE_UIDS` - Comma-separated Firebase UIDs allowed to use `/api/auth/admin/*` (recommended in production)
- `ADMIN_ALLOW_ANY_FIREBASE_USER` - Set to `true` only on local dev to allow any valid Firebase user to call admin APIs (never in production)

## Twilio SMS (optional)

Verification and support-ticket SMS are documented in [docs/TWILIO.md](../docs/TWILIO.md). Enable with `TWILIO_VERIFICATION_SMS_ENABLED` / `TWILIO_SUPPORT_SMS_ENABLED` and set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, plus a Messaging Service or `TWILIO_FROM_NUMBER`. Set `PUBLIC_APP_URL` for support deep links.

## Firebase Service Account

For full Firebase Admin SDK functionality, place `firebase_service_account.json` in the `backend/` directory. The code will automatically detect and use it.

**To get your service account file:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file as `firebase_service_account.json` in the `backend/` directory

**Note:** Without the service account file, the system will use REST API for token verification (which still works).

## Database Schema

See migration file: `migrations/001_create_users_table.sql`

## Development

```bash
# Run with auto-reload
export FLASK_ENV=development
python app.py
```

## Testing

Test endpoints using curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Register user (requires Firebase token)
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"firebase_uid": "test", "email": "test@example.com", "role": "farmer"}'
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper CORS origins
4. Use environment variables for sensitive data
5. Enable HTTPS

```bash
# Example with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

