import sqlite3
import json
import os
from datetime import datetime
from shutil import copy2

def backup_database():
    """Create a backup of the database"""
    db_file = 'smart_bus_management.db'
    
    if not os.path.exists(db_file):
        print("❌ Database file not found!")
        return
    
    # Create backups directory
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'smart_bus_{timestamp}.db')
    
    # Copy database file
    copy2(db_file, backup_file)
    print(f"✅ Database backed up to: {backup_file}")
    
    return backup_file


def restore_database(backup_file):
    """Restore database from backup"""
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return
    
    db_file = 'smart_bus_management.db'
    
    # Confirm restoration
    response = input(f"Restore from {backup_file}? This will overwrite current database. (yes/no): ")
    
    if response.lower() != 'yes':
        print("Restoration cancelled.")
        return
    
    # Backup current database
    if os.path.exists(db_file):
        copy2(db_file, f'{db_file}.backup')
        print(f"✅ Current database backed up to: {db_file}.backup")
    
    # Restore from backup
    copy2(backup_file, db_file)
    print(f"✅ Database restored from: {backup_file}")


def export_to_json(output_file='export.json'):
    """Export database to JSON"""
    db_file = 'smart_bus_management.db'
    
    if not os.path.exists(db_file):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    export_data = {}
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        export_data[table_name] = [dict(row) for row in rows]
    
    conn.close()
    
    # Convert datetime objects to strings
    def default_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=default_handler)
    
    print(f"✅ Database exported to: {output_file}")


def get_database_stats():
    """Get database statistics"""
    db_file = 'smart_bus_management.db'
    
    if not os.path.exists(db_file):
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    total_rows = 0
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   {table_name}: {count} rows")
        total_rows += count
    
    # Get database file size
    db_size = os.path.getsize(db_file) / (1024 * 1024)  # Convert to MB
    
    print("=" * 50)
    print(f"   Total Rows: {total_rows}")
    print(f"   Database Size: {db_size:.2f} MB")
    
    conn.close()


if __name__ == '__main__':
    import sys
    
    print("Smart Bus Management System - Database Tools")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            backup_database()
        elif command == 'restore':
            if len(sys.argv) > 2:
                restore_database(sys.argv[2])
            else:
                print("Usage: python backup_database.py restore <backup_file>")
        elif command == 'export':
            output = sys.argv[2] if len(sys.argv) > 2 else 'export.json'
            export_to_json(output)
        elif command == 'stats':
            get_database_stats()
        else:
            print(f"Unknown command: {command}")
    else:
        print("\nOptions:")
        print("   python backup_database.py backup          - Create database backup")
        print("   python backup_database.py restore <file>  - Restore from backup")
        print("   python backup_database.py export [file]   - Export to JSON")
        print("   python backup_database.py stats           - Show database statistics")
        