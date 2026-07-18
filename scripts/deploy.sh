#!/usr/bin/env bash
#
# Vitmain Production Deployment Script
#
# Usage:
#   ./scripts/deploy.sh                    # deploy current main branch
#   ./scripts/deploy.sh v1.2.3             # deploy specific tag
#   ./scripts/deploy.sh --rollback <tag>   # rollback to a previous tag
#
# Prerequisites on the target server:
#   - Docker 24+ and Docker Compose v2
#   - /opt/vitmain/ directory with .env file
#   - This script must be run from /opt/vitmain/
#
set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================
DEPLOY_DIR="${DEPLOY_DIR:-/opt/vitmain}"
REPO_URL="https://github.com/TadresRadi/Vitmain_Test.git"
BRANCH="${BRANCH:-main}"
TAG="${1:-}"
ROLLBACK_TAG="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn()   { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARN:${NC} $1"; }
error()  { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; exit 1; }

# ============================================================================
# Pre-flight checks
# ============================================================================
preflight() {
    log "Running pre-flight checks..."

    [[ -d "$DEPLOY_DIR" ]] || error "Deploy dir $DEPLOY_DIR does not exist"
    [[ -f "$DEPLOY_DIR/.env" ]] || error ".env file not found in $DEPLOY_DIR"
    command -v docker >/dev/null || error "docker not installed"
    command -v docker-compose >/dev/null || error "docker-compose not installed"

    # Verify required env vars
    source "$DEPLOY_DIR/.env"
    [[ -n "$SECRET_KEY" ]] || error "SECRET_KEY not set in .env"
    [[ -n "$DB_PASSWORD" ]] || error "DB_PASSWORD not set in .env"
    [[ "$DEBUG" == "false" ]] || error "DEBUG must be 'false' in production .env"

    log "Pre-flight checks passed."
}

# ============================================================================
# Backup current state (for rollback)
# ============================================================================
backup_current() {
    local backup_tag="pre-deploy-$(date +%Y%m%d-%H%M%S)"
    local backup_dir="$DEPLOY_DIR/.backups/$backup_tag"

    log "Backing up current deployment to $backup_dir..."
    mkdir -p "$backup_dir"

    # Save current git commit
    cd "$DEPLOY_DIR"
    if [[ -d ".git" ]]; then
        git rev-parse HEAD > "$backup_dir/git_commit.txt"
        log "Current commit: $(cat $backup_dir/git_commit.txt)"
    fi

    # Save current docker-compose.yml and .env
    cp docker-compose.yml "$backup_dir/" 2>/dev/null || true
    cp .env "$backup_dir/" 2>/dev/null || true

    log "Backup saved."
    echo "$backup_tag" > /tmp/vitmain_last_backup_tag.txt
}

# ============================================================================
# Deploy
# ============================================================================
deploy() {
    cd "$DEPLOY_DIR"

    log "Pulling latest code..."
    if [[ -n "$TAG" && "$TAG" != "" && "$TAG" != "--rollback" ]]; then
        log "Deploying tag: $TAG"
        git fetch --tags
        git checkout "$TAG"
    else
        log "Deploying branch: $BRANCH"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
    fi

    log "Building Docker images..."
    docker-compose build --no-cache backend frontend

    log "Starting services..."
    docker-compose up -d

    log "Waiting for backend to be healthy..."
    for i in $(seq 1 30); do
        if docker-compose exec -T backend python -c "import django; django.setup()" 2>/dev/null; then
            log "Backend is up."
            break
        fi
        sleep 2
        if [[ $i -eq 30 ]]; then
            error "Backend failed to start within 60 seconds"
        fi
    done

    log "Running database migrations..."
    docker-compose exec -T backend python manage.py migrate --noinput

    log "Collecting static files..."
    docker-compose exec -T backend python manage.py collectstatic --noinput

    log "Health check..."
    local health_response
    health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/)
    if [[ "$health_response" == "200" ]]; then
        log "Health check passed (HTTP 200)."
    else
        error "Health check failed (HTTP $health_response)"
    fi

    log "Deployment complete!"
    log "  Frontend: http://localhost"
    log "  Backend:  http://localhost:8000"
    log "  Health:   http://localhost:8000/health/"
}

# ============================================================================
# Rollback
# ============================================================================
rollback() {
    if [[ -z "$ROLLBACK_TAG" ]]; then
        error "Rollback requires a tag: ./deploy.sh --rollback <tag>"
    fi

    cd "$DEPLOY_DIR"

    log "Rolling back to tag: $ROLLBACK_TAG"
    git fetch --tags
    git checkout "$ROLLBACK_TAG"

    log "Rebuilding images..."
    docker-compose build --no-cache backend frontend

    log "Restarting services..."
    docker-compose up -d

    log "Running migrations (in case of rollback schema changes)..."
    docker-compose exec -T backend python manage.py migrate --noinput

    log "Health check..."
    local health_response
    health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/)
    if [[ "$health_response" == "200" ]]; then
        log "Rollback complete and healthy."
    else
        error "Rollback health check failed (HTTP $health_response)"
    fi
}

# ============================================================================
# Main
# ============================================================================
main() {
    if [[ "$TAG" == "--rollback" ]]; then
        preflight
        rollback
    else
        preflight
        backup_current
        deploy
    fi
}

main "$@"