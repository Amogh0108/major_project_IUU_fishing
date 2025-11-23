#!/usr/bin/env python3
"""
Quick launcher for IUU Fishing Detection Dashboard
Provides easy access to the interactive visualization system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the dashboard"""
    print("=" * 70)
    print("IUU FISHING DETECTION SYSTEM - DASHBOARD")
    print("=" * 70)
    print()
    print("🚀 Launching interactive dashboard...")
    print()
    print("Features:")
    print("  ✓ Real-time vessel tracking")
    print("  ✓ Anomaly detection visualization")
    print("  ✓ Risk level classification")
    print("  ✓ Interactive maps and charts")
    print("  ✓ Export functionality")
    print()
    print("=" * 70)
    print()
    
    try:
        from src.dashboard.app import main as dashboard_main
        dashboard_main()
    except ImportError as e:
        print("❌ Error: Required packages not installed")
        print(f"   {e}")
        print()
        print("Solution: Install requirements")
        print("   pip install -r requirements.txt")
        print()
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("Dashboard stopped by user")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print()
        print("Check logs/dashboard.log for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
