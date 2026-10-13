#!/usr/bin/env python3
"""
SQLite Database Inspection & Export CLI Tool
---------------------------------------------
Allows project coordinators, evaluators, and engineers to inspect and query
the persistent SQLite database (`oracle/database.db`) outside of the web dashboard.

Usage:
  python db_viewer.py --summary        # Show database summary & total counts
  python db_viewer.py --telemetry      # View recent raw sensor telemetry records
  python db_viewer.py --attacks        # View all logged anomaly and attack events
  python db_viewer.py --aggregations   # View historical validated median updates & Web3 hashes
  python db_viewer.py --export         # Export all database tables to CSV format
"""

import os
import sys
import csv
import sqlite3
import argparse
from datetime import datetime

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}. Run oracle_service.py first.")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def show_summary():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("      DATABASE SUMMARY (Outside Web Interface)")
    print("="*60)
    print(f"Database File: {DB_PATH}\n")

    cursor.execute("SELECT COUNT(*) FROM sensor_telemetry")
    t_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomaly_events")
    a_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM oracle_aggregations")
    g_count = cursor.fetchone()[0]

    print(f"  [1] Total Raw Sensor Telemetry Logs:  {t_count}")
    print(f"  [2] Total Anomaly & Attack Events:   {a_count}")
    print(f"  [3] Total On-Chain Aggregations:     {g_count}")
    print("="*60 + "\n")
    conn.close()

def view_telemetry(limit: int = 15):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"\n--- RECENT SENSOR TELEMETRY LOGS (Last {limit}) ---")
    cursor.execute("SELECT id, timestamp, node_id, temperature, humidity, status FROM sensor_telemetry ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    if not rows:
        print("No telemetry records found.")
    else:
        print(f"{'ID':<6} {'Time':<20} {'Node ID':<16} {'Temp (°C)':<10} {'Hum (%)':<10} {'Status':<12}")
        print("-" * 75)
        for r in rows:
            time_str = datetime.fromtimestamp(r[1]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{r[0]:<6} {time_str:<20} {r[2]:<16} {r[3]:<10.2f} {r[4]:<10.1f} {r[5]:<12}")
    print("-" * 75 + "\n")
    conn.close()

def view_attacks():
    conn = get_connection()
    cursor = conn.cursor()
    print("\n" + "🚨"*30)
    print("       LOGGED ANOMALY & ATTACK EVENTS TABLE")
    print("🚨"*30)
    cursor.execute("SELECT id, timestamp, node_id, offending_value, z_score, action_taken FROM anomaly_events ORDER BY id DESC")
    rows = cursor.fetchall()

    if not rows:
        print("No attack/anomaly events logged yet.")
    else:
        print(f"{'ID':<6} {'Timestamp':<20} {'Compromised Node':<18} {'Value (°C)':<12} {'Z-Score':<10} {'Action Taken':<30}")
        print("-" * 96)
        for r in rows:
            time_str = datetime.fromtimestamp(r[1]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{r[0]:<6} {time_str:<20} {r[2]:<18} {r[3]:<12.2f} {r[4]:<10.2f} {r[5]:<30}")
    print("-" * 96 + "\n")
    conn.close()

def view_aggregations(limit: int = 15):
    conn = get_connection()
    cursor = conn.cursor()
    print(f"\n--- VALIDATED ORACLE MEDIAN AGGREGATIONS & WEB3 HASHES ---")
    cursor.execute("SELECT id, timestamp, aggregated_median, healthy_node_count, tx_hash FROM oracle_aggregations ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()

    if not rows:
        print("No aggregation records found.")
    else:
        print(f"{'ID':<6} {'Time':<20} {'Validated Median (°C)':<22} {'Healthy Nodes':<15} {'Transaction Hash':<30}")
        print("-" * 95)
        for r in rows:
            time_str = datetime.fromtimestamp(r[1]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{r[0]:<6} {time_str:<20} {r[2]:<22.2f} {r[3]:<15} {r[4]:<30}")
    print("-" * 95 + "\n")
    conn.close()

def export_csv():
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = ["sensor_telemetry", "anomaly_events", "oracle_aggregations"]
    for t in tables:
        filename = f"export_{t}.csv"
        cursor.execute(f"SELECT * FROM {t}")
        rows = cursor.fetchall()
        col_names = [description[0] for description in cursor.description]
        
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(col_names)
            writer.writerows(rows)
        print(f"Exported table '{t}' to file: {filename}")
    
    conn.close()
    print("\nDatabase export completed successfully.\n")

def main():
    parser = argparse.ArgumentParser(description="SQLite Database Viewer for Trusted Oracle Project")
    parser.add_argument("--summary", action="store_true", help="Show database summary statistics")
    parser.add_argument("--telemetry", action="store_true", help="Show raw sensor telemetry records")
    parser.add_argument("--attacks", action="store_true", help="Show logged anomaly & attack events")
    parser.add_argument("--aggregations", action="store_true", help="Show validated median aggregations")
    parser.add_argument("--export", action="store_true", help="Export all tables to CSV files")
    
    args = parser.parse_args()

    # Default to summary if no flags given
    if not any(vars(args).values()):
        show_summary()
        view_attacks()
        view_aggregations(5)
    else:
        if args.summary:
            show_summary()
        if args.telemetry:
            view_telemetry()
        if args.attacks:
            view_attacks()
        if args.aggregations:
            view_aggregations()
        if args.export:
            export_csv()

if __name__ == "__main__":
    main()
