#!/bin/bash

# Generic Backup Script
# Configurable backup system for multiple sources

# Configuration
BACKUP_BASE_DIR="$HOME/Documents/admin/backup"
LOG_FILE="/Users/joe/dev/ai/content/logs/backup.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to backup a directory
backup_directory() {
    local name="$1"
    local source_dir="$2"
    local backup_file="$BACKUP_BASE_DIR/$name.zip"
    
    # Check if source directory exists
    if [ ! -d "$source_dir" ]; then
        log "ERROR: [$name] Source directory $source_dir does not exist"
        return 1
    fi
    
    log "Starting backup: $name"
    
    # Remove existing backup file if it exists
    if [ -f "$backup_file" ]; then
        log "[$name] Removing existing backup file"
        rm "$backup_file"
    fi
    
    # Create the backup
    log "[$name] Creating backup from $source_dir"
    if cd "$source_dir" && zip -r "$backup_file" . > /dev/null 2>&1; then
        # Get backup file size for logging
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "SUCCESS: [$name] Backup completed (Size: $backup_size)"
        return 0
    else
        log "ERROR: [$name] Backup failed"
        return 1
    fi
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_BASE_DIR"

log "Starting backup run"

# =============================================================================
# BACKUP CONFIGURATIONS - Add your backup jobs here
# =============================================================================

# Docker data backup
backup_directory "docker-data" "/Users/joe/dev/docker/data"

# Add more backups here as needed:
# backup_directory "project-configs" "$HOME/.config"
# backup_directory "scripts" "/Users/joe/scripts"

# =============================================================================

log "Backup run completed"
