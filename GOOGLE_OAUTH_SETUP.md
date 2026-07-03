# Google OAuth 2.0 Setup Guide

This document provides complete instructions for configuring Google OAuth 2.0 authentication for the Vitmain application.

## Prerequisites

- Google Cloud Console account
- Backend server running on a domain (localhost for development)
- Frontend application running on a domain (localhost for development)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Vitmain Auth")
5. Click "Create"

## Step 2: Enable Google+ API

1. In the Google Cloud Console, navigate to:
   - APIs & Services > Library
2. Search for "Google+ API"
3. Click on it and click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Navigate to:
   - APIs & Services > Credentials
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Click "Create"
   - Fill in the required fields:
     - App name: "Vitmain"
     - User support email: your email
     - Developer contact information: your email
   - Click "Save and Continue" through all steps
4. Back to creating credentials:
   - Application type: "Web application"
   - Name: "Vitmain Web Client"
5. **Authorized JavaScript Origins** (Development):
   ```
   http://localhost:5173
   http://127.0.0.1:5173
   ```
6. **Authorized Redirect URIs** (Development):
   ```
   http://localhost:5173
   http://127.0.0.1:5173
   ```
7. Click "Create"
8. Copy the **Client ID** and **Client Secret**

## Step 4: Configure Production Origins and URIs

For production deployment, add your production domains:

**Authorized JavaScript Origins** (Production):
```
https://yourdomain.com
https://www.yourdomain.com
```

**Authorized Redirect URIs** (Production):
```
https://yourdomain.com
https://www.yourdomain.com
```

## Step 5: Update Environment Variables

Add the Google OAuth credentials to your backend `.env` file:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

## Step 6: Restart Backend Server

After updating the `.env` file, restart the Django development server:

```bash
cd D:\Vitmain\backend
D:\Vitmain\backend\venv\Scripts\python.exe manage.py runserver
```

## Step 7: Test Google Authentication

1. Navigate to the frontend login page: `http://localhost:5173/login`
2. Click "Sign in with Google" button
3. Complete the Google OAuth flow
4. Verify that you are successfully authenticated and redirected

## Security Considerations

### Best Practices

1. **Never commit credentials to version control**
   - The `.env` file should be in `.gitignore`
   - Use environment variables in production

2. **Use separate credentials for development and production**
   - Create separate OAuth clients for each environment
   - This prevents accidental production data exposure

3. **Enable Google email verification**
   - Google OAuth automatically verifies email addresses
   - This prevents users from registering with fake emails

4. **Monitor OAuth usage**
   - Check Google Cloud Console for unusual activity
   - Set up alerts for suspicious authentication attempts

### Token Security

- Access tokens expire after 1 day (configurable in SIMPLE_JWT settings)
- Refresh tokens expire after 7 days (configurable in SIMPLE_JWT settings)
- Tokens are stored in localStorage on the client
- Consider implementing token rotation for enhanced security

## Troubleshooting

### Common Issues

**1. "redirect_uri_mismatch" Error**
- Ensure the redirect URI in Google Console matches exactly
- Check for trailing slashes or protocol differences (http vs https)

**2. "Invalid Client" Error**
- Verify the GOOGLE_CLIENT_ID is correct
- Check that the client ID is not from a different project

**3. "Access Denied" Error**
- Ensure the OAuth consent screen is properly configured
- Verify the application type is set to "Web application"

**4. Frontend Button Not Showing**
- Check that GOOGLE_CLIENT_ID is set in backend
- Verify the `/auth/google/config` endpoint returns the client ID
- Check browser console for errors

### Debug Mode

Enable debug logging in Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Deployment

### Environment Variables

Set the following environment variables in your production environment:

```bash
GOOGLE_CLIENT_ID=production-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=production-client-secret
```

### Domain Configuration

Update the authorized origins and redirect URIs in Google Cloud Console to include your production domain.

### SSL/HTTPS

Google OAuth requires HTTPS for production applications. Ensure your production server:
- Has a valid SSL certificate
- Uses HTTPS protocol
- Has proper domain configuration

## API Endpoints

### Google OAuth Configuration

**GET** `/api/auth/google/config`

Returns the Google OAuth configuration for the frontend:

```json
{
  "google_client_id": "your-client-id.apps.googleusercontent.com",
  "enabled": true
}
```

### Google OAuth Callback

**POST** `/api/auth/google/callback`

Handles the Google OAuth callback and returns JWT tokens:

**Request Body:**
```json
{
  "access_token": "google-oauth-access-token",
  "user_info": {
    "sub": "google-user-id",
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://profile-picture-url"
  }
}
```

**Response:**
```json
{
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "full_name": "User Name",
    "role": "user",
    "onboarding_completed": false,
    "auth_provider": "google",
    "profile_picture": "https://profile-picture-url"
  }
}
```

## Account Linking

The system automatically links Google accounts to existing users based on email address:

1. If a user exists with the same email via local registration:
   - The Google account is linked to the existing user
   - User can log in with either method
   - Profile picture and name are updated if missing

2. If no user exists with the email:
   - A new user is created with Google auth provider
   - User is marked as Google-authenticated
   - User must complete onboarding

## Admin Panel Integration

The Django admin panel displays:
- Authentication provider (Local/Google)
- Profile picture (if available)
- Last login timestamp
- All other user information

Users can be filtered by authentication provider in the admin panel.

## Support

For issues with Google OAuth configuration:
- Check Django logs: `tail -f logs/django.log`
- Check browser console for frontend errors
- Verify Google Cloud Console configuration
- Review allauth documentation: https://docs.allauth.org/
