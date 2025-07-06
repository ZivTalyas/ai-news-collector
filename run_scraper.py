#!/usr/bin/env python3
"""
Simple script to run the AI News Collector scraper
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the AI News Scraper"""
    
    # Check if we're in the correct directory
    if not Path('app/scraper.py').exists():
        print("❌ Error: app/scraper.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if config/.env exists
    if not Path('config/.env').exists():
        print("❌ Error: config/.env not found")
        print("Please create config/.env file with your MongoDB connection string")
        print("You can run: python3 scripts/quick_start.py")
        sys.exit(1)
    
    print("🤖 Starting AI News Scraper...")
    print("🔍 Searching for latest AI news articles...")
    print()
    
    try:
        # Run the scraper
        result = subprocess.run([
            sys.executable, 
            "app/scraper.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Scraper completed successfully!")
            print("📊 Check the dashboard for newly collected articles")
        else:
            print(f"\n❌ Scraper failed with exit code: {result.returncode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Scraper stopped by user")
    except Exception as e:
        print(f"\n❌ Error running scraper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 