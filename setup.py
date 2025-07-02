"""
Setup script for Imamother Forum Scraper
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        print("🔧 Setting up environment configuration...")
        
        # Copy .env.example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your Imamother credentials")
        return True
    elif env_file.exists():
        print("✅ Environment file already exists")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["scraped_data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def validate_setup():
    """Validate the setup"""
    print("\n🔍 Validating setup...")
    
    # Check if all required files exist
    required_files = [
        "main.py", "scraper.py", "data_extractor.py", "utils.py",
        "config.py", "business_analyzer.py", "requirements.txt", ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # Check if credentials are set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        username = os.getenv('IMAMOTHER_USERNAME')
        password = os.getenv('IMAMOTHER_PASSWORD')
        
        if not username or not password:
            print("⚠️  Credentials not set in .env file")
            print("Please edit .env file with your Imamother credentials")
            return False
        
        print("✅ Credentials configured")
        
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping credential check")
    
    print("✅ Setup validation complete")
    return True

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🚀 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your Imamother forum credentials")
    print("2. Test the setup with: python main.py --dry-run")
    print("3. Start scraping with: python main.py")
    print("\n📖 Usage Examples:")
    print("• Scrape all sections: python main.py")
    print("• Scrape specific sections: python main.py --sections pregnancy_childbirth married_life")
    print("• Limit pages: python main.py --max-pages 10")
    print("• Generate business report: python business_analyzer.py")
    print("\n📚 For more information, see README.md")
    print("="*60)

def main():
    """Main setup function"""
    print("🔧 Imamother Forum Scraper Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed during environment configuration")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Validate setup
    if not validate_setup():
        print("⚠️  Setup completed with warnings")
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()