import subprocess
import sys

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
    
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)

def main():
    """Main setup function."""
    print("Starting setup...")
    
    # Install dependencies
    install_dependencies()
    
    # Import ModelDownloader after installing dependencies
    from serve.src.model_downloader import ModelDownloader
    
    # Initialize and use ModelDownloader
    downloader = ModelDownloader()
    downloaded_paths = downloader.download_all_models()
    
    print("\nSetup completed successfully!")
    print(f"Downloaded {len(downloaded_paths)} models to the 'models' directory.")
    print("You can now run the FastAPI server using: python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main() 