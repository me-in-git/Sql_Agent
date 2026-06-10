#!/usr/bin/env python
"""Verify all project files and database are set up correctly."""

import os
import sys

def verify_setup():
    """Verify QueryMind project setup."""
    print("🔍 Verifying QueryMind setup...\n")
    
    required_files = [
        "README.md",
        "app.py",
        "agent.py",
        "utils.py",
        "setup_db.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "CONFIG.md",
        "DEPLOYMENT.md",
        "DEVELOPMENT.md",
    ]
    
    required_dirs = [
        "database",
        ".streamlit"
    ]
    
    required_in_database = [
        "chinook.db"
    ]
    
    all_ok = True
    
    # Check files
    print("📄 Checking files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (MISSING)")
            all_ok = False
    
    print("\n📁 Checking directories...")
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"  ✅ {dir}/")
        else:
            print(f"  ❌ {dir}/ (MISSING)")
            all_ok = False
    
    print("\n🗄️  Checking database...")
    for db_file in required_in_database:
        db_path = os.path.join("database", db_file)
        if os.path.exists(db_path):
            size = os.path.getsize(db_path) / 1024  # KB
            print(f"  ✅ {db_file} ({size:.1f} KB)")
        else:
            print(f"  ❌ {db_file} (MISSING)")
            all_ok = False
    
    print("\n📋 Checking .env...")
    if os.path.exists(".env"):
        print("  ✅ .env configured")
    else:
        print("  ⚠️  .env not found (copy from .env.example and add your API key)")
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Project setup complete!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI or Groq API key to .env")
        print("3. Run: streamlit run app.py")
        return 0
    else:
        print("❌ Setup incomplete. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(verify_setup())
