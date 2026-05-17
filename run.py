#!/usr/bin/env python3
"""Quick start script for the Text-to-SQL Agent."""
import subprocess
import sys
from pathlib import Path

def main():
    print("🚀 Starting Text-to-SQL Agent...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating from .env.example...")
        Path(".env").write_text(Path(".env.example").read_text())
        print("📝 Please edit .env and add your OPENROUTER_API_KEY")
        sys.exit(1)
    
    # Check if database exists
    if not Path("business_db.sqlite").exists():
        print("📦 Setting up database...")
        from src.utils.setup_db import setup_database
        setup_database()
    
    # Run Streamlit
    print("🌐 Launching Streamlit app at http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/streamlit_ui.py"])

if __name__ == "__main__":
    main()
