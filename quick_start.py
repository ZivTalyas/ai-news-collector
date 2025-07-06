#!/usr/bin/env python3
"""
Quick Start Script for AI News Collector
Helps users set up and run the application step by step
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("🤖" + "="*60)
    print("    AI NEWS COLLECTOR - QUICK START")
    print("="*62)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ env_template.txt not found")
        return False
    
    # Copy template to .env
    try:
        with open(template_file, 'r') as src, open(env_file, 'w') as dst:
            content = src.read()
            dst.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  IMPORTANT: Edit .env file with your MongoDB Atlas connection string!")
        print("   Get it from: https://www.mongodb.com/atlas")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_setup_test():
    """Run setup verification tests"""
    print("\n🧪 Running setup tests...")
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🚀 NEXT STEPS:")
    print("="*40)
    print("1. Edit .env file with your MongoDB Atlas connection string")
    print("2. Test setup: python test_setup.py")
    print("3. Run scraper: python scraper.py")
    print("4. Start dashboard: streamlit run dashboard.py")
    print()
    print("📚 For detailed instructions, see README.md")
    print()
    print("🌐 Access dashboard at: http://localhost:8501")
    print("⏰ Set up GitHub Actions for daily automation")

def main():
    """Main quick start workflow"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 3: Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Step 4: Run tests (optional, may fail without MongoDB setup)
    print("\n🔍 Would you like to run setup tests? (requires MongoDB setup)")
    response = input("Run tests now? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_setup_test()
    else:
        print("⏭️  Skipping tests for now")
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 