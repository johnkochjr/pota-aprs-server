#!/bin/bash

LOG_FILE="/volume1/docker/pota-aprs-server/logs/auto-update.log"
PROJECT_DIR="/volume1/docker/pota-aprs-server"

echo "$(date): Checking for updates..." >> "$LOG_FILE"

cd "$PROJECT_DIR"

# Fetch latest changes
git fetch origin main

# Check if there are updates
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "$(date): Updates found! Pulling changes..." >> "$LOG_FILE"
    
    # Pull changes
    git pull origin main
    
    # Rebuild and restart container
    echo "$(date): Rebuilding container..." >> "$LOG_FILE"
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    echo "$(date): ✓ Update complete!" >> "$LOG_FILE"
else
    echo "$(date): No updates available" >> "$LOG_FILE"
fi
