#!/usr/bin/env python3
"""
Simple script to run the AI News Collector dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit dashboard"""
    
    # Check if we're in the correct directory
    if not Path('app/dashboard.py').exists():
        print("❌ Error: app/dashboard.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if config/.env exists
    if not Path('config/.env').exists():
        print("❌ Error: config/.env not found")
        print("Please create config/.env file with your PostgreSQL connection string")
        print("You can run: python3 scripts/quick_start.py")
        sys.exit(1)
    
    print("🚀 Starting AI News Collector Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        # Run the dashboard
        subprocess.run([
            sys.executable, 
            "-m", "streamlit", "run", 
            "app/dashboard.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 