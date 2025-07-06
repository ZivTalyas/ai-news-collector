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
    
    env_file = Path("config/.env")
    config_dir = Path("config")
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(exist_ok=True)
    
    if env_file.exists():
        print("✅ config/.env file already exists")
        return True
    
    # Create a basic .env template
    try:
        env_content = """# PostgreSQL Database Connection String
# Get this from your PostgreSQL provider (e.g., Neon, Supabase, AWS RDS, etc.)
DATABASE_URL=postgresql://username:password@host:port/database_name?sslmode=require

# Optional: Additional configuration
SCRAPER_MAX_ARTICLES=10
SCRAPER_SLEEP_INTERVAL=2

# Instructions:
# 1. Replace the DATABASE_URL with your actual PostgreSQL connection string
# 2. Popular PostgreSQL providers:
#    - Neon: https://neon.tech (free tier available)
#    - Supabase: https://supabase.com (free tier available)
#    - AWS RDS: https://aws.amazon.com/rds/
#    - Google Cloud SQL: https://cloud.google.com/sql
#    - Heroku Postgres: https://www.heroku.com/postgres
# 3. Update other values as needed
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created config/.env file from template")
        print("⚠️  IMPORTANT: Edit config/.env file with your PostgreSQL connection string!")
        print("   Popular free options:")
        print("   - Neon: https://neon.tech")
        print("   - Supabase: https://supabase.com")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create config/.env file: {e}")
        return False

def check_project_structure():
    """Verify the project structure is correct"""
    print("\n📁 Checking project structure...")
    
    required_dirs = ['app', 'config', 'static', 'tests', 'scripts']
    required_files = [
        'app/dashboard.py',
        'app/database.py', 
        'app/scraper.py',
        'static/dashboard.css',
        'requirements.txt'
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ Missing directory: {dir_name}")
            return False
    
    # Check files
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
    
    print("✅ Project structure is correct")
    return True

def run_setup_test():
    """Run setup verification tests"""
    print("\n🧪 Running setup tests...")
    try:
        result = subprocess.run([sys.executable, "tests/test_setup.py"], 
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
    print("1. Edit config/.env file with your PostgreSQL connection string")
    print("2. Test setup: python3 tests/test_setup.py")
    print("3. Run scraper: python3 app/scraper.py")
    print("4. Start dashboard: python3 -m streamlit run app/dashboard.py")
    print()
    print("📚 For detailed instructions, see README.md")
    print()
    print("🌐 Access dashboard at: http://localhost:8501")
    print("⏰ Set up GitHub Actions for daily automation")
    print()
    print("💾 Database Options:")
    print("   Free PostgreSQL providers:")
    print("   - Neon: https://neon.tech (recommended)")
    print("   - Supabase: https://supabase.com")
    print("   - ElephantSQL: https://www.elephantsql.com")
    print()
    print("📁 Project Structure:")
    print("   app/        - Main application code")
    print("   config/     - Configuration files (.env)")
    print("   static/     - CSS and assets")
    print("   tests/      - Test files")
    print("   scripts/    - Utility scripts")

def main():
    """Main quick start workflow"""
    print_banner()
    
    # Step 1: Check project structure
    if not check_project_structure():
        print("❌ Project structure is incorrect. Please check your installation.")
        sys.exit(1)
    
    # Step 2: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("💡 Try running: pip3 install -r requirements.txt")
        sys.exit(1)
    
    # Step 4: Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Step 5: Run tests (optional, may fail without PostgreSQL setup)
    print("\n🔍 Would you like to run setup tests? (requires PostgreSQL setup)")
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