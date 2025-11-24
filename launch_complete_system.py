"""
Launch Complete IUU Fishing Detection System
Starts both live monitoring and dashboard simultaneously
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import subprocess
import time
from threading import Thread

def start_live_monitoring():
    """Start live monitoring system in background"""
    print("🌊 Starting Live Monitoring System...")
    subprocess.Popen([
        sys.executable,
        "src/realtime/live_monitoring_system.py",
        "--interval", "15"
    ])
    time.sleep(2)
    print("✅ Live Monitoring Started")

def start_dashboard():
    """Start enhanced dashboard"""
    print("📊 Starting Enhanced Dashboard...")
    time.sleep(3)  # Wait for monitoring to initialize
    subprocess.run([
        sys.executable,
        "launch_dashboard_enhanced.py"
    ])

def main():
    print("=" * 70)
    print("🚀 IUU FISHING DETECTION - COMPLETE SYSTEM LAUNCHER")
    print("=" * 70)
    print()
    print("This will start:")
    print("  1. Live Monitoring System (fetches real-time AIS data)")
    print("  2. Enhanced Dashboard (visualizes detections)")
    print()
    print("=" * 70)
    print()
    
    # Start monitoring in background thread
    monitor_thread = Thread(target=start_live_monitoring, daemon=True)
    monitor_thread.start()
    
    # Start dashboard (blocking)
    start_dashboard()

if __name__ == '__main__':
    main()
