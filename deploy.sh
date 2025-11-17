#!/bin/bash
export PATH="/opt/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

LOG_FILE="/volume1/docker/pota-aprs-server/logs/deploy.log"

echo "$(date): Webhook triggered - Starting deployment..." >> "$LOG_FILE"

cd /volume1/docker/pota-aprs-server

# Pull latest changes
git pull origin main >> "$LOG_FILE" 2>&1

# Rebuild and restart
docker-compose down >> "$LOG_FILE" 2>&1
docker-compose build --no-cache >> "$LOG_FILE" 2>&1
docker-compose up -d >> "$LOG_FILE" 2>&1

echo "$(date): ✓ Deployment complete!" >> "$LOG_FILE"
