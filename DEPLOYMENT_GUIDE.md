# Google OAuth Deployment Guide

This document provides complete deployment instructions for the Google OAuth 2.0 authentication system.

## Pre-Deployment Checklist

### Backend Requirements

- [x] Django 4.2.30 installed
- [x] django-allauth 0.61.1 installed
- [x] Database migrations applied
- [x] Environment variables configured
- [x] Google OAuth credentials obtained

### Frontend Requirements

- [x] @react-oauth/google 0.12.1 installed
- [x] Google Auth components created
- [x] Login/Register pages updated
- [x] i18n translations added

### Configuration Files

- [x] backend/settings.py updated with allauth configuration
- [x] backend/.env contains GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- [x] frontend/package.json includes @react-oauth/google

## Installation Commands

### Backend Installation

```bash
cd D:\Vitmain\backend

# Install required packages
D:\Vitmain\backend\venv\Scripts\python.exe -m pip install django-allauth==0.61.1 requests-oauthlib==2.0.0

# Apply database migrations
D:\Vitmain\backend\venv\Scripts\python.exe manage.py migrate

# Create superuser (if needed)
D:\Vitmain\backend\venv\Scripts\python.exe manage.py createsuperuser
```

### Frontend Installation

```bash
cd D:\Vitmain\frontend

# Install Google OAuth library
npm install @react-oauth/google@0.12.1

# Build for production
npm run build
```

## Database Migration Commands

```bash
# Create migrations for new fields
D:\Vitmain\backend\venv\Scripts\python.exe manage.py makemigrations users

# Apply migrations
D:\Vitmain\backend\venv\Scripts\python.exe manage.py migrate

# Verify migrations
D:\Vitmain\backend\venv\Scripts\python.exe manage.py showmigrations
```

## Local Development Testing

### 1. Start Backend Server

```bash
cd D:\Vitmain\backend
D:\Vitmain\backend\venv\Scripts\python.exe manage.py runserver
```

The backend will run on `http://127.0.0.1:8000`

### 2. Start Frontend Development Server

```bash
cd D:\Vitmain\frontend
npm run dev
```

The frontend will run on `http://localhost:5173`

### 3. Test Google Authentication Flow

1. Navigate to `http://localhost:5173/login`
2. Click "Sign in with Google" button
3. Complete Google OAuth flow
4. Verify successful authentication and redirect
5. Check that user appears in Django admin panel with auth_provider="google"

### 4. Test Account Linking

1. Register a user with email/password
2. Logout
3. Login with Google using the same email
4. Verify that the Google account is linked to the existing user
5. Check admin panel to confirm auth_provider remains "local" but social account is linked

## Production Deployment

### Environment Variables

Set the following environment variables in your production environment:

```bash
# Backend Environment Variables
SECRET_KEY=your-production-secret-key
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DB_NAME=production_db_name
DB_USER=production_db_user
DB_PASSWORD=production_db_password
DB_HOST=production_db_host
DB_PORT=5432

# Google OAuth Configuration
GOOGLE_CLIENT_ID=production-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=production-client-secret

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS=false
CORS_ALLOW_CREDENTIALS=true
```

### Google Cloud Console Production Setup

1. Create a separate OAuth 2.0 client for production
2. Add production domains to Authorized JavaScript Origins:
   ```
   https://yourdomain.com
   https://www.yourdomain.com
   ```
3. Add production domains to Authorized Redirect URIs:
   ```
   https://yourdomain.com
   https://www.yourdomain.com
   ```
4. Copy production Client ID and Client Secret
5. Update production environment variables

### Backend Deployment

#### Using Gunicorn (Recommended)

```bash
# Install gunicorn
D:\Vitmain\backend\venv\Scripts\python.exe -m pip install gunicorn

# Run with gunicorn
D:\Vitmain\backend\venv\Scripts\gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

#### Using uWSGI

```bash
# Install uwsgi
D:\Vitmain\backend\venv\Scripts\python.exe -m pip install uwsgi

# Run with uwsgi
D:\Vitmain\backend\venv\Scripts\uwsgi --http :8000 --wsgi-file backend/wsgi.py --callable application
```

### Frontend Deployment

#### Build for Production

```bash
cd D:\Vitmain\frontend
npm run build
```

The build output will be in the `dist/` directory.

#### Serve with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Frontend static files
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django static files
    location /static/ {
        alias /path/to/backend/staticfiles/;
    }

    # Django media files
    location /media/ {
        alias /path/to/backend/media/;
    }
}
```

### SSL/HTTPS Configuration

Google OAuth requires HTTPS for production. Ensure:

1. Valid SSL certificate installed
2. HTTPS properly configured
3. SSL certificate chain complete
4. HTTP to HTTPS redirect configured

### Security Headers

Add security headers to your Nginx configuration:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self' https://accounts.google.com https://*.googleapis.com; script-src 'self' 'unsafe-inline' https://accounts.google.com https://*.googleapis.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.googleapis.com;" always;
```

## Post-Deployment Verification

### 1. Verify Backend Health

```bash
curl https://yourdomain.com/api/auth/google/config
```

Expected response:
```json
{
  "google_client_id": "your-production-client-id.apps.googleusercontent.com",
  "enabled": true
}
```

### 2. Verify Frontend Loading

Navigate to `https://yourdomain.com/login` and verify:
- Google Sign In button appears
- No console errors
- Google OAuth configuration loads correctly

### 3. Test Complete OAuth Flow

1. Click "Sign in with Google"
2. Complete Google OAuth flow
3. Verify successful authentication
4. Check redirect to appropriate page
5. Verify JWT token is stored in localStorage

### 4. Verify Admin Panel

1. Access Django admin at `https://yourdomain.com/admin/`
2. Navigate to Users section
3. Verify auth_provider column displays correctly
4. Verify profile pictures display for Google users
5. Verify last_login timestamps update correctly

### 5. Test Account Linking

1. Create a local account with email/password
2. Logout
3. Login with Google using same email
4. Verify account linking works
5. Check admin panel for linked social account

## Monitoring and Maintenance

### Log Monitoring

Monitor Django logs for OAuth-related errors:

```bash
tail -f /var/log/django/application.log | grep -i "google\|oauth\|allauth"
```

### Google Cloud Console Monitoring

1. Navigate to APIs & Services > Credentials
2. Monitor OAuth usage statistics
3. Check for unusual authentication patterns
4. Set up alerts for suspicious activity

### Database Maintenance

Regular database maintenance tasks:

```bash
# Backup database
pg_dump -U postgres -d vitmain_db > backup.sql

# Analyze database
D:\Vitmain\backend\venv\Scripts\python.exe manage.py dbshell
ANALYZE;

# Clean up old sessions
D:\Vitmain\backend\venv\Scripts\python.exe manage.py clearsessions
```

## Troubleshooting Production Issues

### Issue: Google OAuth Button Not Showing

**Symptoms:** Google Sign In button doesn't appear on login page

**Solutions:**
1. Verify GOOGLE_CLIENT_ID is set in production environment
2. Check `/api/auth/google/config` endpoint returns client ID
3. Verify frontend can reach backend API
4. Check browser console for errors
5. Verify @react-oauth/google is properly installed

### Issue: redirect_uri_mismatch Error

**Symptoms:** Google OAuth returns "redirect_uri_mismatch" error

**Solutions:**
1. Verify authorized redirect URIs in Google Cloud Console
2. Check for trailing slashes or protocol differences
3. Ensure production domain matches exactly
4. Verify no extra characters in redirect URI

### Issue: Invalid Client Error

**Symptoms:** Google OAuth returns "Invalid Client" error

**Solutions:**
1. Verify GOOGLE_CLIENT_ID is correct
2. Check that client ID belongs to correct project
3. Verify client is not deleted or disabled
4. Check Google Cloud Console for client status

### Issue: Access Denied Error

**Symptoms:** Google OAuth returns "Access Denied" error

**Solutions:**
1. Verify OAuth consent screen is configured
2. Check application type is "Web application"
3. Verify user email is not blocked
4. Check Google account security settings

### Issue: JWT Token Not Generated

**Symptoms:** User authenticates with Google but no JWT token returned

**Solutions:**
1. Check Django logs for backend errors
2. Verify SECRET_KEY is set correctly
3. Check JWT configuration in settings
4. Verify user creation/update logic works
5. Test backend endpoint directly with curl

## Rollback Procedure

If issues arise after deployment:

### Backend Rollback

```bash
# Revert to previous migration
D:\Vitmain\backend\venv\Scripts\python.exe manage.py migrate users 0002

# Remove django-allauth from requirements.txt
# Restart backend server
```

### Frontend Rollback

```bash
# Revert package.json changes
git checkout HEAD -- package.json package-lock.json

# Reinstall dependencies
npm install

# Rebuild
npm run build
```

## Performance Optimization

### Backend Optimization

1. Enable database connection pooling
2. Configure caching for Google OAuth config
3. Optimize database queries with select_related/prefetch_related
4. Enable gzip compression for API responses

### Frontend Optimization

1. Lazy load Google Auth component
2. Cache Google OAuth configuration
3. Optimize bundle size with code splitting
4. Use CDN for Google OAuth library

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use HTTPS** for all OAuth flows in production
3. **Rotate secrets** regularly
4. **Monitor OAuth usage** for suspicious activity
5. **Implement rate limiting** on OAuth endpoints
6. **Log all OAuth attempts** for audit trail
7. **Use separate credentials** for development and production
8. **Keep dependencies updated** for security patches

## Support Resources

- Django Allauth Documentation: https://docs.allauth.org/
- Google OAuth 2.0 Documentation: https://developers.google.com/identity/protocols/oauth2
- React OAuth Google Documentation: https://react-oauth.github.io/react-oauth/google/
- Django REST Framework SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/

## Summary of Changes

### Modified Files

**Backend:**
- `backend/users/models/custom_user.py` - Added auth_provider, profile_picture, last_login fields
- `backend/users/adapters.py` - Created custom adapters for account linking
- `backend/users/views/google_auth_view.py` - Created Google OAuth callback view
- `backend/users/views/__init__.py` - Added Google auth view imports
- `backend/users/urls.py` - Added Google OAuth endpoints
- `backend/users/admin.py` - Updated admin panel to display auth provider
- `backend/backend/settings.py` - Configured django-allauth and middleware
- `backend/requirements.txt` - Added django-allauth and requests-oauthlib
- `backend/.env` - Added Google OAuth environment variables

**Frontend:**
- `frontend/package.json` - Added @react-oauth/google dependency
- `frontend/src/components/GoogleAuthButton.tsx` - Created Google Auth component
- `frontend/src/pages/Login.tsx` - Added Google Sign In button
- `frontend/src/pages/Register.tsx` - Added Google Sign Up button
- `frontend/src/i18n/locales/en.json` - Added Google Auth translations
- `frontend/src/i18n/locales/ar.json` - Added Google Auth translations

### New Files

- `backend/users/adapters.py` - Custom allauth adapters
- `backend/users/views/google_auth_view.py` - Google OAuth views
- `frontend/src/components/GoogleAuthButton.tsx` - Google Auth component
- `GOOGLE_OAUTH_SETUP.md` - Google Cloud Console setup guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions (this file)

### Database Changes

- Migration `users.0003_customuser_auth_provider_customuser_profile_picture_and_more.py` applied
- django-allauth migrations applied (account, socialaccount, sites)

### API Endpoints Added

- `GET /api/auth/google/config` - Returns Google OAuth configuration
- `POST /api/auth/google/callback` - Handles Google OAuth callback

## Conclusion

The Google OAuth 2.0 authentication system is now fully integrated into the Vitmain application. The system provides:

- Secure Google authentication with JWT tokens
- Automatic account creation for new Google users
- Account linking for existing users
- Profile picture and name synchronization
- Admin panel integration
- Production-ready deployment configuration
- Comprehensive error handling and logging

Follow this deployment guide to deploy the system to production and ensure all security best practices are followed.
