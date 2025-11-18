#!/usr/bin/env python3
"""
Database Restore Script
Restores PostgreSQL database from SQL backup file
"""

import os
import sys
from datetime import datetime

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 not installed")
    sys.exit(1)


def restore_database_backup(backup_file):
    """Restore database from SQL backup file"""
    
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    # Get database credentials from environment
    db_config = {
        'host': os.environ.get('PGHOST'),
        'port': os.environ.get('PGPORT'),
        'database': os.environ.get('PGDATABASE'),
        'user': os.environ.get('PGUSER'),
        'password': os.environ.get('PGPASSWORD')
    }
    
    # Validate credentials
    if not all(db_config.values()):
        print("Error: Missing database credentials")
        sys.exit(1)
    
    print(f"Restoring database from: {backup_file}")
    print(f"Target database: {db_config['database']}")
    print(f"Host: {db_config['host']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read backup file
        with open(backup_file, 'r') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        print(f"\nExecuting {len(statements)} SQL statements...")
        
        executed = 0
        errors = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement or statement.startswith('--'):
                continue
            
            try:
                cursor.execute(statement)
                executed += 1
                
                if executed % 10 == 0:
                    print(f"  Progress: {executed}/{len(statements)} statements")
                    
            except Exception as e:
                errors += 1
                print(f"  Warning: Statement {i} failed: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✓ Restore completed!")
        print(f"  Executed: {executed} statements")
        print(f"  Errors: {errors}")
        
        if errors > 0:
            print(f"\n⚠ Some statements failed. Check logs for details.")
        
        return executed, errors
        
    except Exception as e:
        print(f"Error restoring backup: {e}")
        sys.exit(1)


def list_available_backups():
    """List all available backup files"""
    
    backups_dir = 'backups'
    
    if not os.path.exists(backups_dir):
        print("No backups directory found")
        return []
    
    backup_files = [
        f for f in os.listdir(backups_dir)
        if f.startswith('database_') and f.endswith('.sql')
    ]
    
    if not backup_files:
        print("No database backup files found")
        return []
    
    print("\nAvailable database backups:")
    for i, filename in enumerate(sorted(backup_files, reverse=True), 1):
        filepath = os.path.join(backups_dir, filename)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"  {i}. {filename}")
        print(f"     Size: {size} bytes ({size/1024:.2f} KB)")
        print(f"     Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return backup_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Restore PostgreSQL database from backup')
    parser.add_argument('--file', '-f', help='Backup file to restore')
    parser.add_argument('--list', '-l', action='store_true', help='List available backups')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_backups()
    elif args.file:
        restore_database_backup(args.file)
    else:
        backups = list_available_backups()
        if backups:
            print("\nUsage: python restore_database.py --file backups/database_backup_xxx.sql")
        else:
            print("\nNo backups found. Create a backup first using backup_database.py")
