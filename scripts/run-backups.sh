#!/bin/bash

# Generic Backup Script
# Configurable backup system for multiple sources

# Configuration
BACKUP_BASE_DIR="$HOME/Documents/admin/backup"
LOG_FILE="/Users/joe/dev/ai/content/logs/backup.log"
KEEP_BACKUPS=7  # Number of recent backups to keep

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to find the most recent backup file for a given name pattern
find_latest_backup() {
    local name="$1"
    local backup_dir="${BACKUP_BASE_DIR}/${name}"
    local pattern="${backup_dir}/*-${name}.zip"
    # Find most recent backup matching pattern, sorted by modification time
    ls -t $pattern 2>/dev/null | head -1
}

# Function to check if backup is stale (older than 24 hours)
is_backup_stale() {
    local name="$1"
    local latest_backup=$(find_latest_backup "$name")
    local max_age_hours=24
    
    # If no backup exists, it's stale
    if [ -z "$latest_backup" ] || [ ! -f "$latest_backup" ]; then
        return 0
    fi
    
    # Get file age in hours
    local file_age=$(($(date +%s) - $(stat -f %m "$latest_backup" 2>/dev/null || echo 0)))
    local file_age_hours=$((file_age / 3600))
    
    # Return 0 (stale) if older than max_age_hours
    [ $file_age_hours -ge $max_age_hours ]
}

# Function to clean up old backups, keeping only the most recent N
cleanup_old_backups() {
    local name="$1"
    local backup_dir="${BACKUP_BASE_DIR}/${name}"
    local pattern="${backup_dir}/*-${name}.zip"
    
    # Get all backups sorted by modification time (newest first)
    local backups=($(ls -t $pattern 2>/dev/null))
    local count=${#backups[@]}
    
    # If we have more backups than we want to keep, delete the oldest ones
    if [ $count -gt $KEEP_BACKUPS ]; then
        local to_delete=$(($count - $KEEP_BACKUPS))
        log "[$name] Cleaning up $to_delete old backup(s), keeping $KEEP_BACKUPS most recent"
        
        for ((i=$KEEP_BACKUPS; i<$count; i++)); do
            local old_backup="${backups[$i]}"
            if rm "$old_backup" 2>/dev/null; then
                log "[$name] Deleted old backup: $(basename "$old_backup")"
            else
                log "WARNING: [$name] Failed to delete old backup: $(basename "$old_backup")"
            fi
        done
    fi
}

# Function to backup a directory
backup_directory() {
    local name="$1"
    local source_dir="$2"
    local backup_dir="${BACKUP_BASE_DIR}/${name}"
    local date_prefix=$(date '+%Y-%m-%d')
    local backup_file="${backup_dir}/${date_prefix}-${name}.zip"
    
    # Create backup directory for this backup type
    mkdir -p "$backup_dir"
    
    # Check if source directory exists
    if [ ! -d "$source_dir" ]; then
        log "ERROR: [$name] Source directory $source_dir does not exist"
        return 1
    fi
    
    # Check if backup is stale (older than 24 hours)
    if ! is_backup_stale "$name"; then
        log "[$name] Backup is fresh, skipping (backup is less than 24 hours old)"
        return 0
    fi
    
    log "Starting backup: $name"
    
    # Create the backup with date prefix in name-specific folder
    log "[$name] Creating backup from $source_dir"
    if cd "$source_dir" && zip -r "$backup_file" . > /dev/null 2>&1; then
        # Get backup file size for logging
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "SUCCESS: [$name] Backup completed (Size: $backup_size, File: $(basename "$backup_file"))"
        
        # Clean up old backups
        cleanup_old_backups "$name"
        
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
