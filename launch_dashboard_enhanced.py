"""Launch the enhanced IUU Fishing Detection Dashboard with animations"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.dashboard.app_enhanced import main

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Launching Enhanced IUU Fishing Detection Dashboard v3.0")
    print("=" * 70)
    print("📊 Dashboard Features:")
    print("   • Smooth animations and transitions")
    print("   • Modern glassmorphism design")
    print("   • Interactive hover effects")
    print("   • Real-time vessel tracking")
    print("   • Advanced anomaly detection")
    print("   • Model performance comparison")
    print("   • Detailed anomaly reports")
    print("")
    print("🌐 Access the dashboard at:")
    print("   http://localhost:9090")
    print("")
    print("💡 Tips:")
    print("   • Hover over cards for smooth animations")
    print("   • Adjust threshold slider for sensitivity")
    print("   • Select specific vessels for detailed view")
    print("   • Click refresh to update data")
    print("=" * 70)
    print("Starting server...")
    print("=" * 70)
    
    main()
