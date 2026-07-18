#!/usr/bin/env bash
#
# Vitmain PostgreSQL Backup Script
#
# Runs pg_dump inside the postgres container, compresses the output,
# and retains only the last 30 days of backups.
#
# Usage:
#   ./scripts/backup_db.sh
#
# Cron (daily at 3 AM):
#   0 3 * * * /opt/vitmain/scripts/backup_db.sh >> /var/log/vitmain-backup.log 2>&1
#
# Optional: copy to offsite storage (e.g. AWS S3)
#   Set S3_BUCKET env var to enable: S3_BUCKET=my-backup-bucket ./scripts/backup_db.sh
#
set -euo pipefail

DEPLOY_DIR="${DEPLOY_DIR:-/opt/vitmain}"
BACKUP_DIR="${BACKUP_DIR:-$DEPLOY_DIR/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vitmain_db_$TIMESTAMP.sql.gz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log()   { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"; exit 1; }

# Load env
[[ -f "$DEPLOY_DIR/.env" ]] || error ".env not found at $DEPLOY_DIR/.env"
source "$DEPLOY_DIR/.env"

[[ -n "$DB_NAME" ]] || error "DB_NAME not set"
[[ -n "$DB_USER" ]] || error "DB_USER not set"

# Create backup dir
mkdir -p "$BACKUP_DIR"

log "Starting backup of database: $DB_NAME"

# Find the postgres container
PG_CONTAINER=$(docker-compose -f "$DEPLOY_DIR/docker-compose.yml" ps -q db 2>/dev/null || true)
if [[ -z "$PG_CONTAINER" ]]; then
    error "Postgres container not running. Is docker-compose up?"
fi

# Dump and compress
log "Running pg_dump..."
docker exec "$PG_CONTAINER" \
    pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges \
    | gzip > "$BACKUP_FILE"

# Verify the backup is non-empty
if [[ ! -s "$BACKUP_FILE" ]]; then
    error "Backup file is empty — something went wrong"
fi

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup complete: $BACKUP_FILE ($BACKUP_SIZE)"

# Cleanup old backups
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "vitmain_db_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
log "Cleanup complete."

# Optional: copy to S3
if [[ -n "${S3_BUCKET:-}" ]]; then
    log "Copying backup to S3 bucket: $S3_BUCKET"
    aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/vitmain-backups/$(basename $BACKUP_FILE)" \
        --sse AES256 \
        || warn "S3 copy failed (continuing — local backup is safe)"
    log "S3 copy complete."
fi

log "Backup process finished successfully."