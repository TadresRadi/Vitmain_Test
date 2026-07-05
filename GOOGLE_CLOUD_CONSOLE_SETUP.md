# Google Cloud Console Setup for OAuth

## Critical: Configure Authorized JavaScript Origins

The error **"The given origin is not allowed for the given client ID"** means your Google Cloud Console OAuth credentials are not configured with the correct origins.

### Steps to Fix:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project (or create a new one)

2. **Navigate to Credentials**
   - Go to: **APIs & Services** → **Credentials**
   - Or directly: https://console.cloud.google.com/apis/credentials

3. **Find Your OAuth 2.0 Client ID**
   - Look for the OAuth 2.0 Client ID you're using (usually named "Web client" or similar)
   - Click on it to edit

4. **Add Authorized JavaScript Origins**
   
   Under **"Authorized JavaScript origins"**, add ALL of the following:
   ```
   http://localhost:5173
   http://localhost:5174
   http://127.0.0.1:5173
   http://127.0.0.1:5174
   ```
   
   **Important**: 
   - Click "Add URI" for each one
   - Do NOT include trailing slashes (e.g., `http://localhost:5173/` is WRONG)
   - Make sure to use `http://` not `https://` for local development

5. **Add Authorized Redirect URIs**
   
   Under **"Authorized redirect URIs"**, add:
   ```
   http://localhost:5173
   http://localhost:5174
   http://127.0.0.1:5173
   http://127.0.0.1:5174
   ```

6. **Save Changes**
   - Click the **"Save"** button at the bottom

7. **Wait for Propagation**
   - Changes may take 1-5 minutes to take effect
   - If it still doesn't work, try:
     - Clear browser cache
     - Restart the frontend dev server
     - Wait a few minutes and try again

## Verification

After configuring, test by:

1. Starting your backend: `cd backend && .\venv\Scripts\python.exe manage.py runserver`
2. Starting your frontend: `cd frontend && npm run dev`
3. Going to your login page
4. Clicking "Sign in with Google"
5. The Google popup should appear without the "origin not allowed" error

## Common Issues

### Issue: "redirect_uri_mismatch"
- Make sure the redirect URI in Google Console exactly matches your frontend URL
- No trailing slashes!

### Issue: Still getting "origin not allowed" after adding
- Wait 5 minutes for changes to propagate
- Clear browser cache and cookies
- Try in an incognito/private window
- Make sure you're using the correct OAuth client ID (check your backend `.env` file)

### Issue: Button not showing
- Check that `GOOGLE_CLIENT_ID` is set correctly in `backend/.env`
- Check browser console for errors
- Verify the `/api/auth/google/config` endpoint returns the correct client ID

## Production Setup

For production, you'll need to add your production domain:

**Authorized JavaScript origins:**
```
https://yourdomain.com
https://www.yourdomain.com
```

**Authorized redirect URIs:**
```
https://yourdomain.com
https://www.yourdomain.com
```

## Security Notes

- Never commit your `GOOGLE_CLIENT_SECRET` to version control
- Use separate OAuth clients for development and production
- Keep your client secret secure