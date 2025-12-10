"""
💾 BACKUP SYSTEM - Automatic Data Backup
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import hashlib

class BackupSystem:
    def __init__(self):
        self.backup_dir = "data/backups"
        self.max_backups = 10  # Keep last 10 backups
        self.backup_files = [
            "data/knowledge_base.json",
            "data/conversations/",
            "data/images/",
            "data/diagrams/",
            "config/master_config.json",
            "data/fb_cookies.pkl",
            "templates/",
            "logs/"
        ]
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """Create a new backup"""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        print(f"📦 Creating backup: {backup_name}")
        
        backed_up_files = []
        
        # Copy files and directories
        for item in self.backup_files:
            source_path = item
            dest_path = os.path.join(backup_path, os.path.basename(item))
            
            try:
                if os.path.exists(source_path):
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                        backed_up_files.append(f"📁 {item}")
                    else:
                        shutil.copy2(source_path, dest_path)
                        backed_up_files.append(f"📄 {item}")
                else:
                    print(f"⚠️  Skipping (not found): {item}")
            except Exception as e:
                print(f"❌ Error backing up {item}: {e}")
        
        # Create backup info file
        backup_info = {
            "name": backup_name,
            "created": datetime.now().isoformat(),
            "files": backed_up_files,
            "total_size": self.get_directory_size(backup_path),
            "hash": self.generate_backup_hash(backup_path)
        }
        
        info_file = os.path.join(backup_path, "backup_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        # Create zip archive
        zip_path = f"{backup_path}.zip"
        self.create_zip_archive(backup_path, zip_path)
        
        # Clean up temporary directory
        shutil.rmtree(backup_path)
        
        print(f"✅ Backup created: {zip_path}")
        print(f"   Files backed up: {len(backed_up_files)}")
        print(f"   Total size: {self.format_size(os.path.getsize(zip_path))}")
        
        # Clean old backups
        self.clean_old_backups()
        
        return zip_path
    
    def create_zip_archive(self, source_dir, zip_path):
        """Create zip archive of backup"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
    
    def restore_backup(self, backup_path):
        """Restore from backup"""
        if not os.path.exists(backup_path):
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        print(f"🔄 Restoring from backup: {backup_path}")
        
        # Extract backup
        extract_dir = "temp_restore"
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Read backup info
            info_file = os.path.join(extract_dir, "backup_info.json")
            if os.path.exists(info_file):
                with open(info_file, 'r') as f:
                    backup_info = json.load(f)
                print(f"📋 Backup info: {backup_info['name']}")
                print(f"   Created: {backup_info['created']}")
            
            # Restore files
            restored_files = []
            
            for item in os.listdir(extract_dir):
                if item != "backup_info.json":
                    source = os.path.join(extract_dir, item)
                    dest = os.path.join(".", item)
                    
                    if os.path.exists(dest):
                        if os.path.isdir(dest):
                            shutil.rmtree(dest)
                        else:
                            os.remove(dest)
                    
                    if os.path.isdir(source):
                        shutil.copytree(source, dest)
                    else:
                        shutil.copy2(source, dest)
                    
                    restored_files.append(item)
            
            # Clean up
            shutil.rmtree(extract_dir)
            
            print(f"✅ Restore completed!")
            print(f"   Files restored: {len(restored_files)}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Clean up on error
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            return False
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                backup_path = os.path.join(self.backup_dir, file)
                backup_info = {
                    "name": file,
                    "path": backup_path,
                    "size": os.path.getsize(backup_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(backup_path))
                }
                backups.append(backup_info)
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        return backups
    
    def clean_old_backups(self):
        """Remove old backups keeping only max_backups"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            backups_to_delete = backups[self.max_backups:]
            
            for backup in backups_to_delete:
                try:
                    os.remove(backup['path'])
                    print(f"🗑️  Deleted old backup: {backup['name']}")
                except Exception as e:
                    print(f"⚠️  Could not delete {backup['name']}: {e}")
    
    def get_directory_size(self, directory):
        """Calculate directory size in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def generate_backup_hash(self, directory):
        """Generate hash for backup integrity check"""
        hash_md5 = hashlib.md5()
        
        # Get sorted list of all files
        all_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                all_files.append(filepath)
        
        all_files.sort()
        
        # Hash each file
        for filepath in all_files:
            try:
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
            except Exception as e:
                print(f"⚠️  Error hashing {filepath}: {e}")
        
        return hash_md5.hexdigest()
    
    def format_size(self, size_bytes):
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def auto_backup(self):
        """Automatic backup (call this periodically)"""
        print(f"\n{'='*50}")
        print("🤖 AUTOMATIC BACKUP SYSTEM")
        print(f"{'='*50}")
        
        backup_path = self.create_backup()
        
        # Upload to cloud (optional)
        if self.should_upload_to_cloud():
            self.upload_to_cloud(backup_path)
        
        return backup_path
    
    def should_upload_to_cloud(self):
        """Check if should upload to cloud storage"""
        # Implement your logic here
        # Check config, available space, etc.
        return False
    
    def upload_to_cloud(self, backup_path):
        """Upload backup to cloud storage"""
        # Implement cloud upload (Google Drive, Dropbox, etc.)
        print("☁️  Cloud upload not implemented yet")
    
    def run(self):
        """Run backup system"""
        print("\n" + "="*50)
        print("💾 MASTER BOT BACKUP SYSTEM")
        print("="*50)
        
        print("\nOptions:")
        print("1. Create new backup")
        print("2. List backups")
        print("3. Restore backup")
        print("4. Auto cleanup")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            backup_name = input("Backup name (leave empty for auto): ").strip()
            if not backup_name:
                backup_name = None
            self.create_backup(backup_name)
            
        elif choice == "2":
            backups = self.list_backups()
            print(f"\n📚 Available backups ({len(backups)}):")
            for i, backup in enumerate(backups, 1):
                print(f"\n{i}. {backup['name']}")
                print(f"   Size: {self.format_size(backup['size'])}")
                print(f"   Modified: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            
        elif choice == "3":
            backups = self.list_backups()
            if backups:
                print("\nSelect backup to restore:")
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup['name']}")
                
                try:
                    selection = int(input("\nEnter number: ")) - 1
                    if 0 <= selection < len(backups):
                        self.restore_backup(backups[selection]['path'])
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Invalid input")
            else:
                print("❌ No backups found")
                
        elif choice == "4":
            self.clean_old_backups()
            print("✅ Cleanup completed")
            
        else:
            print("👋 Exiting backup system")

if __name__ == "__main__":
    backup_system = BackupSystem()
    backup_system.run()