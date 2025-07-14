#!/usr/bin/env python3
"""
AgentArena Platform Startup Script
Complete setup and launch for the AI agent evaluation platform similar to realevals.xyz
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def print_banner():
    """Print the platform banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║    █████╗  ██████╗ ███████╗███╗   ██╗████████╗     █████╗       ║
    ║   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝    ██╔══██╗      ║
    ║   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║       ███████║      ║
    ║   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║       ██╔══██║      ║
    ║   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║       ██║  ██║      ║
    ║   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚═╝  ╚═╝      ║
    ║                                                                  ║
    ║               🤖 AI Agent Evaluation Platform 🤖                 ║
    ║                                                                  ║
    ║                    Similar to realevals.xyz                     ║
    ║          🎯 Real Agents • Real Tasks • Real Results 🎯          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 
        'passlib', 'python-jose', 'loguru', 'psutil', 'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies!")
            print("Please run: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies satisfied!")

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# AgentArena Environment Configuration
APP_NAME=AgentArena
ENVIRONMENT=development
DEBUG=true
API_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./agentarena.db
DATABASE_LOGGING=false

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO

# Admin Configuration
ADMIN_SECRET_KEY=admin-secret-key-change-in-production-2024

# Feature Flags
ENABLE_REAL_TIME_MONITORING=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_WEBSOCKETS=true
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")
    else:
        print("✅ .env file already exists")

def setup_database_and_admin():
    """Set up database and create admin account"""
    print("\n🗄️  Setting up database and admin account...")
    
    try:
        # Import and run setup script
        from setup_admin import setup_platform
        
        print("Running platform setup...")
        success = setup_platform()
        
        if success:
            print("✅ Database and admin setup completed successfully!")
            return True
        else:
            print("❌ Setup completed with warnings")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        print("Please check the error and try again")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AgentArena server...")
    
    try:
        import uvicorn
        from main import app
        
        print("✅ Server starting...")
        print("📡 API Documentation: http://localhost:8000/docs")
        print("🔧 Admin Dashboard: http://localhost:8000/api/v1/admin/dashboard")
        print("🌐 Frontend (if running): http://localhost:5173")
        print("\n" + "="*60)
        print("🎉 PLATFORM READY!")
        print("="*60)
        print("📧 Admin Login: sumit@gmail.com")
        print("🔑 Admin Password: sumit@12345")
        print("="*60)
        
        # Start the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        sys.exit(1)

def check_frontend():
    """Check if frontend is available and provide instructions"""
    print("\n🎨 Frontend Setup Instructions:")
    
    client_dir = Path("../client")
    if client_dir.exists():
        print("✅ Frontend directory found!")
        print("\nTo start the frontend:")
        print("1. cd ../client")
        print("2. npm install")
        print("3. npm run dev")
        print("\nFrontend will be available at: http://localhost:5173")
    else:
        print("⚠️  Frontend directory not found")
        print("You can still use the API directly at: http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")

def show_platform_info():
    """Show platform information and capabilities"""
    print("\n" + "="*60)
    print("🎯 PLATFORM FEATURES")
    print("="*60)
    print("🤖 Enhanced Agent Collection (similar to realevals.xyz)")
    print("   • Comprehensive agent metadata")
    print("   • Performance tracking")
    print("   • Advanced configuration options")
    print()
    print("📋 REAL-Style Evaluation Tasks")
    print("   • E-commerce workflows")
    print("   • Travel booking")
    print("   • Email management")
    print("   • Professional networking")
    print("   • Real estate analysis")
    print("   • And 7 more challenging tasks!")
    print()
    print("⚡ Admin Features")
    print("   • Real-time monitoring")
    print("   • Advanced analytics")
    print("   • Performance insights")
    print("   • User management")
    print("   • WebSocket updates")
    print("   • Data export capabilities")
    print()
    print("🏆 Cool Features")
    print("   • Activity heatmaps")
    print("   • Agent performance insights")
    print("   • Real-time WebSocket updates")
    print("   • Advanced leaderboards")
    print("   • ML-style analytics")
    print("="*60)

def main():
    """Main setup and startup function"""
    print_banner()
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Check dependencies
    check_dependencies()
    
    # Step 3: Set up environment
    setup_environment()
    
    # Step 4: Set up database and admin
    setup_success = setup_database_and_admin()
    
    if not setup_success:
        print("\n⚠️  Setup completed with warnings. You can still start the server.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(1)
    
    # Step 5: Show platform info
    show_platform_info()
    
    # Step 6: Check frontend
    check_frontend()
    
    # Step 7: Start server
    input("\nPress Enter to start the server...")
    start_server()

if __name__ == "__main__":
    main()