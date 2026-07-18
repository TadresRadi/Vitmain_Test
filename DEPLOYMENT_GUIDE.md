Deployment Guide — Vitmain
This guide covers deploying Vitmain to a production server using Docker Compose.

Prerequisites
A Linux server (Ubuntu 22.04+ recommended) with:
Docker 24+ and Docker Compose v2+
At least 2GB RAM (4GB recommended for AI features)
20GB+ disk space
Open ports 80 (HTTP) and 443 (HTTPS)
A domain name pointing to the server's IP address
SMTP credentials for transactional emails (Gmail, SendGrid, etc.)
API keys for AI providers (Groq, at minimum one image provider)
Google OAuth credentials (if using Google login)
Vodafone Cash merchant number + webhook secret
Environment Variables
Create a .env file at the repo root. Never commit this file.

Required (application will not boot without these)
Variable	Description	Example
SECRET_KEY	Django secret key, 50+ random characters	django-insecure-<random_50_chars>
DEBUG	Must be false in production	false
ALLOWED_HOSTS	Comma-separated allowed hosts	api.yourdomain.com,yourdomain.com
DB_NAME	PostgreSQL database name	vitmain_db
DB_USER	PostgreSQL user	vitmain_user
DB_PASSWORD	PostgreSQL password (strong, 32+ chars)	<random_32_chars>
DB_HOST	Database host	db (in Docker) or localhost
DB_PORT	Database port	5432
REDIS_URL	Redis connection URL	redis://redis:6379/1
VODAFONE_WEBHOOK_SECRET_TOKEN	Secret token for Vodafone webhook	<random_64_chars>
VODAFONE_RECEIVER_NUMBER	Vodafone Cash merchant number	010XXXXXXXXX
Required for features
Variable	Description	Notes
CORS_ALLOWED_ORIGINS	Comma-separated frontend origins	https://yourdomain.com
CSRF_TRUSTED_ORIGINS	Same as CORS, with scheme	https://yourdomain.com
FRONTEND_BASE_URL	Frontend base URL	https://yourdomain.com
GROQ_API_KEY	Groq API key	Required for AI post generation
REPLICATE_API_TOKEN	Replicate API token	Optional, for image generation
STABILITY_API_TOKEN	Stability AI token	Optional, for image generation
DEEPAI_API_TOKEN	DeepAI token	Optional, for image generation
GOOGLE_CLIENT_ID	Google OAuth client ID	Required for Google login
GOOGLE_CLIENT_SECRET	Google OAuth client secret	Required for Google login
Optional (recommended)
Variable	Description	Default
SENTRY_DSN	Sentry error tracking DSN	(disabled if not set)
SENTRY_TRACES_SAMPLE_RATE	Sentry performance sample rate	0.0
EMAIL_HOST	SMTP host	smtp.gmail.com
EMAIL_PORT	SMTP port	587
EMAIL_USE_TLS	Use TLS	true
EMAIL_HOST_USER	SMTP username	(none)
EMAIL_HOST_PASSWORD	SMTP password	(none)
DEFAULT_FROM_EMAIL	Sender address	noreply@yourdomain.com
ENABLE_PROMETHEUS	Enable Prometheus metrics	false
USE_JSON_LOGS	JSON-formatted logs	false
SLOW_QUERY_THRESHOLD_MS	Slow query threshold	200
SECURE_SSL_REDIRECT	Force HTTPS redirect	false (set true with TLS)
SECURE_HSTS_SECONDS	HSTS duration	31536000 (when not DEBUG)
Generate strong secrets
# SECRET_KEYpython -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"# VODAFONE_WEBHOOK_SECRET_TOKENopenssl rand -hex 32# DB_PASSWORDopenssl rand -base64 24
Deployment Steps
1. Clone the repository
bash

git clone https://github.com/TadresRadi/Vitmain_Test.git
cd Vitmain_Test
2. Create and review .env
bash

cp .env.example .env  # if .env.example exists, otherwise create manually
nano .env
Fill in all required variables. Double-check DEBUG=false.

3. Build and start the stack
bash

docker-compose up -d --build
This starts:

PostgreSQL (port 5432, internal)
Redis (port 6379, internal)
Backend / Django + Gunicorn (port 8000)
Frontend / Nginx (port 80)
4. Run database migrations
bash

docker-compose exec backend python manage.py migrate
5. Collect static files
bash

docker-compose exec backend python manage.py collectstatic --noinput
6. Create a superuser
bash

docker-compose exec backend python manage.py createsuperuser
7. Verify the deployment
bash

# Health check
curl http://localhost/health/

# Should return JSON with status "healthy"

# Frontend
curl -I http://localhost/
# Should return 200 OK
8. (Optional) Seed sample data
bash

docker-compose exec backend python manage.py add_sample_brands
TLS / HTTPS Setup
Option A: Caddy (recommended — automatic Let's Encrypt)
Create a Caddyfile:

text

yourdomain.com {
    reverse_proxy frontend:80
}

api.yourdomain.com {
    reverse_proxy backend:8000
}
Add Caddy to docker-compose.yml:

yaml

  caddy:
    image: caddy:2-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - frontend
      - backend
Then set SECURE_SSL_REDIRECT=true in .env.

Option B: Nginx + Certbot
See standard Certbot setup. Point Nginx reverse proxy to port 80 (frontend) and port 8000 (backend).

Database Backups
Automated daily backup (cron)
Create /opt/vitmain/backup.sh:

bash

#!/bin/bash
set -e

BACKUP_DIR="/opt/vitmain/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vitmain_db_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

# Dump and compress
docker-compose -f /opt/vitmain/docker-compose.yml exec -T db \
  pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# Keep only the last 30 days
find "$BACKUP_DIR" -name "vitmain_db_*.sql.gz" -mtime +30 -delete

# Optional: copy to offsite storage
# aws s3 cp "$BACKUP_FILE" s3://your-bucket/vitmain-backups/
Add to crontab:

bash

# Run daily at 3 AM
0 3 * * * /opt/vitmain/backup.sh >> /opt/vitmain/backups/backup.log 2>&1
Restore from backup
bash

gunzip < /opt/vitmain/backups/vitmain_db_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose exec -T db psql -U "$DB_USER" "$DB_NAME"
Monitoring (optional but recommended)
Start the monitoring stack
bash

docker-compose -f docker-compose.yml -f docker-compose.monitor.yml up -d
This starts Prometheus, Grafana, and Alertmanager.

Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
Alertmanager: http://localhost:9093
Set ENABLE_PROMETHEUS=true in .env to expose metrics at /metrics.

Sentry
Set SENTRY_DSN in .env to enable error tracking.

Updating the Deployment
bash

cd /opt/vitmain
git pull origin main
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
Rollback
If a deployment breaks:

bash

# Option 1: Roll back code
git log --oneline -5  # find the last known-good commit
git checkout <commit-hash>
docker-compose up -d --build

# Option 2: Roll back database
# Stop the backend
docker-compose stop backend
# Restore from the most recent backup (see "Restore from backup" above)
# Restart
docker-compose start backend
Troubleshooting
Backend won't start
bash

# Check logs
docker-compose logs backend

# Common issues:
# - Missing required env var → check .env
# - Database connection refused → check DB_HOST, DB_PASSWORD
# - Settings validation failed → check logs for SECURITY CONFIGURATION ERRORS
Frontend can't reach backend
bash

# Check Nginx config
docker-compose exec frontend nginx -t

# Check backend is running
docker-compose ps backend

# Check CORS
curl -I -X OPTIONS -H "Origin: https://yourdomain.com" https://api.yourdomain.com/api/
Database migrations fail
bash

# Check migration status
docker-compose exec backend python manage.py showmigrations

# Roll back to a specific migration
docker-compose exec backend python manage.py migrate <app> <migration_name>
Email not sending
bash

# Test email
docker-compose exec backend python manage.py sendtestemail your@email.com

# Check SMTP credentials
docker-compose exec backend python -c "
import smtplib
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('$EMAIL_HOST_USER', '$EMAIL_HOST_PASSWORD')
print('SMTP OK')
"
Post-Deployment Checklist
 DEBUG=false in .env
 ALLOWED_HOSTS set correctly
 CORS_ALLOWED_ORIGINS set to your domain
 CSRF_TRUSTED_ORIGINS set to your domain
 SECRET_KEY is 50+ random characters (not dev-secret-key)
 DB_PASSWORD is strong (not postgres)
 HTTPS/TLS configured and working
 SECURE_SSL_REDIRECT=true
 Database backup cron job configured
 Sentry DSN configured
 Health check returns 200 (curl https://yourdomain.com/health/)
 Test user registration works
 Test Google OAuth works
 Test Vodafone Cash payment flow
 Test admin login at /admin/
text


  ### Verify

  ```bash
  wc -l DEPLOYMENT_GUIDE.md
  # Expected: ~250+ lines
  head -1 DEPLOYMENT_GUIDE.md
  # Expected: # Deployment Guide — Vitmain

  Vodafone Cash Webhook
  Webhook Contract
  The webhook endpoint is POST /api/payments/vodafone-cash/webhook.

  Authentication: HMAC-SHA256 signature over the raw request body, sent in the X-Vodafone-Signature header. The shared secret is VODAFONE_WEBHOOK_SECRET_TOKEN from your .env.

  Headers:

  Content-Type: application/json
  X-Vodafone-Signature: <hex HMAC-SHA256 of raw body>

  text


  **Body:**
  ```json
  {
      "sender_number": "01012345678",
      "amount": "200.00",
      "transaction_id": "TX123456",
      "raw_sms": "Full SMS text from Vodafone",
      "reference_code": "VITMAIN-ABC123"
  }
  reference_code is optional but recommended — it enables Priority 1 matching.

  Computing the signature (Python example):

  python

  import hashlib
  import hmac
  import json

  secret = "your-webhook-secret"
  body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
  signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

  # Send as: X-Vodafone-Signature: <signature>
  Responses:

  200 OK — transaction processed (matched, unmatched, or ignored duplicate)
  400 Bad Request — missing required fields or invalid payload
  401 Unauthorized — missing or invalid signature
  500 Internal Server Error — webhook secret not configured or server error