#!/usr/bin/env python3
"""
🚀 DEPLOYMENT SCRIPT - Deploy Bot to Server
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class BotDeployer:
    def __init__(self):
        self.project_dir = Path(__file__).parent.parent
        self.deploy_log = self.project_dir / "logs/deploy.log"
        
        # Ensure log directory exists
        (self.project_dir / "logs").mkdir(exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        # Write to log file
        with open(self.deploy_log, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log("Checking prerequisites...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            self.log(f"Python 3.8+ required (found {python_version.major}.{python_version.minor})", "ERROR")
            return False
        
        # Check required commands
        required_commands = ["git", "pip", "npm"]
        for cmd in required_commands:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True)
                self.log(f"✓ {cmd} found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.log(f"✗ {cmd} not found", "ERROR")
                return False
        
        # Check required directories
        required_dirs = ["bot_core", "web_dashboard", "config", "scripts"]
        for dir_name in required_dirs:
            dir_path = self.project_dir / dir_name
            if not dir_path.exists():
                self.log(f"✗ Directory not found: {dir_name}", "ERROR")
                return False
        
        self.log("✓ All prerequisites satisfied")
        return True
    
    def backup_existing(self, backup_name=None):
        """Backup existing deployment"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.project_dir / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"Creating backup: {backup_name}")
        
        # Files to backup
        important_files = [
            "data/",
            "config/",
            ".env",
            "logs/",
            "requirements.txt",
            "package.json"
        ]
        
        backed_up = []
        for item in important_files:
            source = self.project_dir / item
            if source.exists():
                try:
                    if source.is_dir():
                        dest = backup_dir / source.name
                        shutil.copytree(source, dest)
                    else:
                        shutil.copy2(source, backup_dir)
                    backed_up.append(item)
                except Exception as e:
                    self.log(f"⚠️ Could not backup {item}: {e}", "WARNING")
        
        self.log(f"✓ Backup created: {len(backed_up)} items backed up")
        return backup_dir
    
    def install_dependencies(self):
        """Install Python and Node.js dependencies"""
        self.log("Installing dependencies...")
        
        # Python dependencies
        try:
            self.log("Installing Python packages...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✓ Python dependencies installed")
            else:
                self.log(f"✗ Python dependency installation failed: {result.stderr}", "ERROR")
                return False
        
        except Exception as e:
            self.log(f"✗ Error installing Python dependencies: {e}", "ERROR")
            return False
        
        # Node.js dependencies
        try:
            self.log("Installing Node.js packages...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✓ Node.js dependencies installed")
            else:
                self.log(f"✗ Node.js dependency installation failed: {result.stderr}", "ERROR")
                return False
        
        except Exception as e:
            self.log(f"✗ Error installing Node.js dependencies: {e}", "ERROR")
            return False
        
        return True
    
    def setup_environment(self):
        """Setup environment configuration"""
        self.log("Setting up environment...")
        
        env_file = self.project_dir / ".env"
        env_example = self.project_dir / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy2(env_example, env_file)
                self.log("✓ Created .env file from example")
                self.log("⚠️ Please edit .env file with your credentials", "WARNING")
            else:
                self.log("✗ .env.example not found", "ERROR")
                return False
        else:
            self.log("✓ .env file already exists")
        
        # Create necessary directories
        directories = [
            "data/knowledge",
            "data/conversations",
            "data/diagrams",
            "data/images",
            "data/backups",
            "templates",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.log("✓ Environment setup completed")
        return True
    
    def run_tests(self):
        """Run deployment tests"""
        self.log("Running deployment tests...")
        
        tests = [
            self.test_python_imports,
            self.test_web_files,
            self.test_config_files,
            self.test_database_connection
        ]
        
        passed = 0
        failed = 0
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"Test error: {e}", "ERROR")
                failed += 1
        
        self.log(f"Tests: {passed} passed, {failed} failed")
        
        if failed == 0:
            self.log("✓ All tests passed")
            return True
        else:
            self.log("✗ Some tests failed", "ERROR")
            return False
    
    def test_python_imports(self):
        """Test Python module imports"""
        try:
            # Try to import main modules
            import sys
            sys.path.insert(0, str(self.project_dir / "bot_core"))
            
            test_modules = [
                "master_ultra",
                "facebook_ultra",
                "diagram_generator",
                "image_creator",
                "bengali_nlp_advanced"
            ]
            
            for module in test_modules:
                __import__(module)
            
            self.log("✓ Python imports successful")
            return True
        
        except ImportError as e:
            self.log(f"✗ Python import failed: {e}", "ERROR")
            return False
    
    def test_web_files(self):
        """Test web dashboard files"""
        web_dir = self.project_dir / "web_dashboard"
        
        required_files = [
            "index.html",
            "dashboard.html",
            "css/master.css",
            "js/master.js"
        ]
        
        missing_files = []
        for file in required_files:
            if not (web_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log(f"✗ Missing web files: {missing_files}", "ERROR")
            return False
        
        self.log("✓ Web files check passed")
        return True
    
    def test_config_files(self):
        """Test configuration files"""
        config_dir = self.project_dir / "config"
        
        required_files = [
            "master_config.json",
            "security_config.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (config_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.log(f"✗ Missing config files: {missing_files}", "ERROR")
            return False
        
        self.log("✓ Config files check passed")
        return True
    
    def test_database_connection(self):
        """Test database connections"""
        try:
            # Test Firebase
            import firebase_admin
            from firebase_admin import credentials
            
            # Just test import, actual connection will happen at runtime
            self.log("✓ Database imports successful")
            return True
        
        except ImportError as e:
            self.log(f"✗ Database import failed: {e}", "ERROR")
            return False
    
    def start_bot(self):
        """Start the bot after deployment"""
        self.log("Starting bot...")
        
        try:
            # Make runner executable
            runner = self.project_dir / "run_ultra.py"
            runner.chmod(0o755)
            
            # Start bot in background
            import subprocess
            process = subprocess.Popen(
                [sys.executable, str(runner)],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit to see if it starts
            import time
            time.sleep(5)
            
            if process.poll() is None:
                self.log("✓ Bot started successfully")
                return process
            else:
                stdout, stderr = process.communicate()
                self.log(f"✗ Bot failed to start: {stderr.decode()}", "ERROR")
                return None
        
        except Exception as e:
            self.log(f"✗ Error starting bot: {e}", "ERROR")
            return None
    
    def deploy(self, options):
        """Main deployment method"""
        self.log("=" * 50)
        self.log("🚀 MASTER BOT DEPLOYMENT STARTED")
        self.log("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("Deployment failed: Prerequisites not met", "ERROR")
            return False
        
        # Create backup
        if options.backup:
            self.backup_existing()
        
        # Install dependencies
        if not self.install_dependencies():
            self.log("Deployment failed: Dependency installation failed", "ERROR")
            return False
        
        # Setup environment
        if not self.setup_environment():
            self.log("Deployment failed: Environment setup failed", "ERROR")
            return False
        
        # Run tests
        if options.test and not self.run_tests():
            self.log("Deployment failed: Tests failed", "ERROR")
            return False
        
        # Start bot
        if options.start:
            bot_process = self.start_bot()
            if not bot_process and options.strict:
                self.log("Deployment failed: Bot failed to start", "ERROR")
                return False
        
        self.log("=" * 50)
        self.log("✅ DEPLOYMENT COMPLETED SUCCESSFULLY")
        self.log("=" * 50)
        
        # Show next steps
        self.show_next_steps()
        
        return True
    
    def show_next_steps(self):
        """Show next steps after deployment"""
        print("\n" + "=" * 50)
        print("📋 NEXT STEPS:")
        print("=" * 50)
        print("1. Edit .env file with your credentials:")
        print("   - Facebook credentials")
        print("   - Firebase configuration")
        print("   - Cloudinary API keys")
        print()
        print("2. Start the bot manually:")
        print("   python run_ultra.py")
        print()
        print("3. Access the web dashboard:")
        print("   http://localhost:8080")
        print()
        print("4. Monitor bot logs:")
        print("   tail -f logs/bot.log")
        print()
        print("5. Check bot status:")
        print("   python scripts/status_check.py")
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Deploy MASTER 🪓 Bot")
    
    parser.add_argument("--backup", action="store_true", 
                       help="Create backup before deployment")
    parser.add_argument("--no-test", dest="test", action="store_false",
                       help="Skip deployment tests")
    parser.add_argument("--no-start", dest="start", action="store_false",
                       help="Don't start bot after deployment")
    parser.add_argument("--strict", action="store_true",
                       help="Fail deployment if any step fails")
    
    args = parser.parse_args()
    
    deployer = BotDeployer()
    
    try:
        success = deployer.deploy(args)
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()