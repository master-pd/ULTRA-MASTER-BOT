"""
🔄 AUTO UPDATE SYSTEM
Automatically update bot from GitHub
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class AutoUpdater:
    def __init__(self):
        self.github_repo = "https://github.com/your-username/ULTRA-MASTER-BOT"
        self.config_file = "config/github_sync.json"
        self.last_update_file = "data/last_update.json"
        
    def check_for_updates(self):
        """Check for updates on GitHub"""
        print("🔍 Checking for updates...")
        
        try:
            # Get latest commit info from GitHub API
            api_url = f"https://api.github.com/repos/your-username/ULTRA-MASTER-BOT/commits/main"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                latest_commit = response.json()
                latest_hash = latest_commit['sha']
                latest_date = latest_commit['commit']['committer']['date']
                
                # Load last update info
                if os.path.exists(self.last_update_file):
                    with open(self.last_update_file, 'r') as f:
                        last_info = json.load(f)
                    last_hash = last_info.get('last_hash', '')
                else:
                    last_hash = ''
                
                if latest_hash != last_hash:
                    print(f"🔄 New update available!")
                    print(f"   Latest commit: {latest_hash[:8]}")
                    print(f"   Date: {latest_date}")
                    return True, latest_hash
                else:
                    print("✅ Bot is up to date!")
                    return False, latest_hash
            else:
                print("❌ Could not check for updates")
                return False, None
                
        except Exception as e:
            print(f"❌ Error checking updates: {e}")
            return False, None
    
    def update_bot(self):
        """Update bot from GitHub"""
        print("🚀 Updating bot from GitHub...")
        
        try:
            # Save current state
            self.backup_current_state()
            
            # Pull latest changes
            commands = [
                ["git", "stash"],  # Stash local changes
                ["git", "pull", "origin", "main"],  # Pull latest
                ["git", "stash", "pop"]  # Restore local changes
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️ Command failed: {' '.join(cmd)}")
                    print(f"   Error: {result.stderr}")
            
            # Update dependencies
            print("📦 Updating dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"])
            
            # Update last update info
            update_info = {
                "last_update": datetime.now().isoformat(),
                "last_hash": self.get_current_hash(),
                "update_count": self.get_update_count() + 1
            }
            
            with open(self.last_update_file, 'w') as f:
                json.dump(update_info, f, indent=2)
            
            print("✅ Update completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def backup_current_state(self):
        """Backup current bot state"""
        print("💾 Backing up current state...")
        
        backup_dir = f"data/backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Important files to backup
        important_files = [
            "data/knowledge_base.json",
            "data/conversations/",
            "data/images/",
            "data/diagrams/",
            "config/master_config.json",
            "data/fb_cookies.pkl"
        ]
        
        import shutil
        for item in important_files:
            try:
                if os.path.exists(item):
                    if os.path.isdir(item):
                        shutil.copytree(item, f"{backup_dir}/{os.path.basename(item)}")
                    else:
                        shutil.copy2(item, backup_dir)
            except Exception as e:
                print(f"⚠️ Could not backup {item}: {e}")
        
        print(f"✅ Backup saved to: {backup_dir}")
    
    def get_current_hash(self):
        """Get current git hash"""
        try:
            result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def get_update_count(self):
        """Get total update count"""
        if os.path.exists(self.last_update_file):
            with open(self.last_update_file, 'r') as f:
                data = json.load(f)
            return data.get("update_count", 0)
        return 0
    
    def run(self):
        """Main update process"""
        print("\n" + "="*50)
        print("🔄 MASTER BOT AUTO-UPDATE SYSTEM")
        print("="*50)
        
        needs_update, latest_hash = self.check_for_updates()
        
        if needs_update:
            print("\n📥 Update available! Do you want to update? (y/n)")
            choice = input("> ").lower().strip()
            
            if choice == 'y':
                success = self.update_bot()
                if success:
                    print("\n✅ Update completed!")
                    print("🔄 Please restart the bot to apply changes.")
                else:
                    print("\n❌ Update failed!")
            else:
                print("\n⏸️ Update cancelled.")
        else:
            print("\n✅ Bot is already up to date!")

if __name__ == "__main__":
    updater = AutoUpdater()
    updater.run()