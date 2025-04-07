import subprocess
import sys
import os
from pathlib import Path

def check_sam_installation():
    """Check if SAM-HQ package is installed."""
    try:
        import segment_anything
        print("✓ SAM-HQ package is installed")
        return True
    except ImportError:
        print("✗ SAM-HQ package is not installed")
        print("Please install it first by running: pip install -e . from the root directory")
        return False

def install_dependencies():
    """Install required Python packages."""
    requirements = [
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "opencv-python>=4.7.0",
        "numpy>=1.23.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0",
        "tqdm>=4.65.0",
    ]
    
    print("Installing FastAPI application dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)

def main():
    """Main setup function."""
    print("Starting FastAPI application setup...")
    
    # Check if SAM-HQ is installed
    if not check_sam_installation():
        sys.exit(1)
    
    # Install FastAPI-specific dependencies
    install_dependencies()
    
    # Import ModelDownloader after installing dependencies
    from serve.src.model_downloader import ModelDownloader
    
    # Initialize and use ModelDownloader
    downloader = ModelDownloader()
    downloaded_paths = downloader.download_all_models()
    
    print("\nSetup completed successfully!")
    print(f"✓ Downloaded {len(downloaded_paths)} models to the 'models' directory")
    print("\nTo start the FastAPI server:")
    print("1. Navigate to the serve directory: cd serve")
    print("2. Run: python -m uvicorn main:app --reload")
    print("\nThe server will be available at: http://localhost:8000")

if __name__ == "__main__":
    main() 