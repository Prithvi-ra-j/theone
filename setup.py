#!/usr/bin/env python3
"""
Dristhi Platform Setup Script
Automates the initial setup process for the Dristhi platform
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print the Dristhi setup banner"""
    print("""
🎯 Dristhi Platform Setup
==========================
AI-Powered Career & Life Improvement Platform
""")

def check_prerequisites():
    """Check if required software is installed"""
    print("🔍 Checking prerequisites...")
    
    required_tools = {
        'python': 'Python 3.11+',
        'node': 'Node.js 18+',
        'docker': 'Docker',
        'docker-compose': 'Docker Compose',
        'git': 'Git'
    }
    
    missing_tools = []
    
    for tool, description in required_tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✅ {description} - Found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {description} - Missing")
            missing_tools.append(description)
    
    if missing_tools:
        print(f"\n❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install the missing tools and run this script again.")
        sys.exit(1)
    
    print("✅ All prerequisites are satisfied!\n")

def create_env_files():
    """Create environment files from examples"""
    print("📝 Creating environment files...")
    
    # Backend environment
    backend_env_example = Path("backend/.env.example")
    backend_env = Path("backend/.env")
    
    if backend_env_example.exists() and not backend_env.exists():
        shutil.copy(backend_env_example, backend_env)
        print("✅ Created backend/.env")
    elif backend_env.exists():
        print("ℹ️  backend/.env already exists")
    else:
        print("⚠️  backend/.env.example not found, creating basic .env")
        create_basic_backend_env()
    
    # Frontend environment
    frontend_env_example = Path("frontend/.env.example")
    frontend_env = Path("frontend/.env")
    
    if frontend_env_example.exists() and not frontend_env.exists():
        shutil.copy(frontend_env_example, frontend_env)
        print("✅ Created frontend/.env")
    elif frontend_env.exists():
        print("ℹ️  frontend/.env already exists")
    else:
        print("⚠️  frontend/.env.example not found, creating basic .env")
        create_basic_frontend_env()
    
    print()

def create_basic_backend_env():
    """Create a basic backend environment file"""
    env_content = """# Backend Environment Variables
DATABASE_URL=postgresql://postgres:password@localhost:5432/dristhi
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-here-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
OLLAMA_BASE_URL=http://localhost:11434
DEBUG=true
"""
    
    with open("backend/.env", "w") as f:
        f.write(env_content)

def create_basic_frontend_env():
    """Create a basic frontend environment file"""
    env_content = """# Frontend Environment Variables
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Dristhi
VITE_DEBUG_MODE=true
"""
    
    with open("frontend/.env", "w") as f:
        f.write(env_content)

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("📦 Installing dependencies...")
    
    # Backend dependencies
    print("🐍 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    # Frontend dependencies
    print("📱 Installing Node.js dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", shell=True, check=True)
        print("✅ Node.js dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    print()
    return True

def setup_database():
    """Set up the database with migrations"""
    print("🗄️  Setting up database...")
    
    try:
        # Start database services
        print("🚀 Starting database services...")
        subprocess.run(["docker-compose", "-f", "infra/docker-compose.yml", "up", "-d", "postgres", "redis"], check=True)

        # Wait for database to be ready
        print("⏳ Waiting for database to become healthy (up to 60s)...")
        import time
        for i in range(30):
            # Use the container name from docker-compose.yml
            result = subprocess.run(["docker", "inspect", "--format", "{{.State.Health.Status}}", "dristhi-postgres"], capture_output=True, text=True)
            if "healthy" in result.stdout:
                print("✅ Database is healthy!")
                break
            time.sleep(2)
        else:
            print("❌ Timed out waiting for the database to become healthy. Please check Docker logs.")
            return False

        # Run migrations
        print("🔄 Running database migrations...")
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd="backend", check=True)
        
        print("✅ Database setup completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    print()
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("""
🎉 Setup completed successfully!

🚀 Next steps:
1. Review and update environment variables in:
   - backend/.env
   - frontend/.env

2. Start all services:
   make dev

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001 (admin/admin)

4. Create your first user account through the registration page

📚 For more information, see README.md and PROJECT_STATUS.md

Happy coding! 🚀
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    check_prerequisites()
    
    # Create environment files
    create_env_files()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed during database setup")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
