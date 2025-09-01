#!/usr/bin/env python3
"""
Database Inspector for Quizgenix
This script helps you check all the data stored in the backend database
"""

import sqlite3
import os
import json
from datetime import datetime

def connect_to_database():
    """Connect to the Quizgenix database"""
    db_paths = [
        'instance/quizgenix.db',
        'backend/instance/quizgenix.db',
        'backend/app/instance/quizgenix.db'
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            print(f"✅ Found database at: {path}")
            return sqlite3.connect(path)
    
    print("❌ Database not found in any of the expected locations:")
    for path in db_paths:
        print(f"   - {path}")
    return None

def inspect_database():
    """Inspect all tables and data in the database"""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("🔍 QUIZGENIX DATABASE INSPECTION REPORT")
    print("="*60)
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Found {len(tables)} tables in the database:")
    for table in tables:
        print(f"   - {table[0]}")
    
    print("\n" + "-"*60)
    
    # Inspect each table
    for table_name in [t[0] for t in tables]:
        print(f"\n📋 TABLE: {table_name}")
        print("-" * 30)
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("📝 Schema:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) {'- PRIMARY KEY' if col[5] else ''}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"📊 Total Records: {count}")
        
        if count > 0:
            # Show sample data (first 5 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            
            print("📋 Sample Data (first 5 rows):")
            for i, row in enumerate(rows, 1):
                print(f"   Row {i}: {row}")
            
            if count > 5:
                print(f"   ... and {count - 5} more rows")
    
    print("\n" + "="*60)
    print("✅ Database inspection complete!")
    conn.close()

def check_specific_data():
    """Check specific types of data"""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    print("\n🔍 DETAILED DATA ANALYSIS")
    print("="*40)
    
    # Check Users
    try:
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"👥 Total Users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT role, COUNT(*) FROM user GROUP BY role")
            roles = cursor.fetchall()
            print("   By Role:")
            for role, count in roles:
                print(f"     - {role}: {count} users")
    except:
        print("👥 Users table not found or error")
    
    # Check Quizzes
    try:
        cursor.execute("SELECT COUNT(*) FROM quiz")
        quiz_count = cursor.fetchone()[0]
        print(f"📝 Total Quizzes: {quiz_count}")
        
        if quiz_count > 0:
            cursor.execute("SELECT topic, COUNT(*) FROM quiz GROUP BY topic")
            topics = cursor.fetchall()
            print("   By Topic:")
            for topic, count in topics:
                print(f"     - {topic}: {count} quizzes")
    except:
        print("📝 Quiz table not found or error")
    
    # Check Quiz Results
    try:
        cursor.execute("SELECT COUNT(*) FROM quiz_result")
        result_count = cursor.fetchone()[0]
        print(f"📊 Total Quiz Results: {result_count}")
        
        if result_count > 0:
            cursor.execute("SELECT AVG(score) FROM quiz_result")
            avg_score = cursor.fetchone()[0]
            print(f"   Average Score: {avg_score:.2f}%")
    except:
        print("📊 Quiz Results table not found or error")
    
    # Check Bookmarks
    try:
        cursor.execute("SELECT COUNT(*) FROM bookmark")
        bookmark_count = cursor.fetchone()[0]
        print(f"🔖 Total Bookmarks: {bookmark_count}")
    except:
        print("🔖 Bookmarks table not found or error")
    
    conn.close()

def export_data_to_json():
    """Export all data to JSON for easy viewing"""
    conn = connect_to_database()
    if not conn:
        return
    
    cursor = conn.cursor()
    data_export = {}
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Convert to list of dictionaries
        table_data = []
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[columns[i]] = value
            table_data.append(row_dict)
        
        data_export[table] = {
            'count': len(table_data),
            'data': table_data
        }
    
    # Save to file
    export_file = 'database_export.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(data_export, f, indent=2, default=str)
    
    print(f"\n💾 Data exported to: {export_file}")
    conn.close()

if __name__ == "__main__":
    print("🚀 Starting Quizgenix Database Inspection...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all inspections
    inspect_database()
    check_specific_data()
    export_data_to_json()
    
    print("\n✨ Inspection complete! Check the database_export.json file for detailed data.")
