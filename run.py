"""
YouTube Bot Video Extractor - Main Entry Point
Run this script to start the application
"""
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import and run main application
from main import ApplicationController

if __name__ == "__main__":
    controller = ApplicationController()
    
    if not controller.initialize():
        sys.exit(1)
    
    sys.exit(controller.run())
