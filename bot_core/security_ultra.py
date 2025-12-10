"""
🛡️ SECURITY ULTRA - Advanced Security & Anti-Detection
Military Grade Protection
"""

import os
import time
import random
import hashlib
import secrets
from datetime import datetime
from typing import Dict, List, Optional
import requests
from cryptography.fernet import Fernet
import json

class SecurityLayer:
    def __init__(self):
        self.security_config = self.load_security_config()
        self.encryption_key = self.get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.proxy_list = []
        self.current_proxy = None
        self.detection_count = 0
        self.last_activity = datetime.now()
        
        self.load_proxy_list()
        self.setup_firewall()
    
    def load_security_config(self) -> Dict:
        """Load security configuration"""
        config_path = "config/security_config.json"
        default_config = {
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256",
                "key_rotation_days": 7
            },
            "stealth": {
                "user_agent_rotation": True,
                "ip_rotation": True,
                "behavior_mimicking": True,
                "random_delays": True,
                "mouse_movement": True
            },
            "firewall": {
                "block_suspicious_ips": True,
                "rate_limiting": True,
                "max_requests_per_minute": 60,
                "geo_blocking": False
            },
            "monitoring": {
                "log_all_activities": True,
                "alert_on_suspicious": True,
                "auto_backup_on_alert": True,
                "shutdown_on_detection": False
            }
        }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            return default_config
    
    def get_encryption_key(self):
        """Get or generate encryption key"""
        key_path = "config/encryption.key"
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
        
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.security_config["encryption"]["enabled"]:
            return data
        
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        if not self.security_config["encryption"]["enabled"]:
            return encrypted_data
        
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def load_proxy_list(self):
        """Load proxy list from file or environment"""
        proxy_sources = [
            os.getenv("PROXY_LIST", ""),
            "config/proxies.txt",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http"
        ]
        
        for source in proxy_sources:
            if source.startswith("http"):
                try:
                    response = requests.get(source, timeout=10)
                    proxies = response.text.strip().split('\n')
                    self.proxy_list.extend([p.strip() for p in proxies if p.strip()])
                except:
                    pass
            elif os.path.exists(source):
                with open(source, 'r') as f:
                    self.proxy_list.extend([line.strip() for line in f if line.strip()])
            elif source:  # Direct proxy string
                self.proxy_list.extend([p.strip() for p in source.split(',') if p.strip()])
        
        # Remove duplicates
        self.proxy_list = list(set(self.proxy_list))
        print(f"🔒 Loaded {len(self.proxy_list)} proxies")
    
    def rotate_proxy(self):
        """Rotate to a new proxy"""
        if not self.proxy_list:
            return None
        
        self.current_proxy = random.choice(self.proxy_list)
        
        # Set proxy in environment
        os.environ['HTTP_PROXY'] = self.current_proxy
        os.environ['HTTPS_PROXY'] = self.current_proxy
        
        print(f"🔄 Proxy rotated: {self.current_proxy}")
        return self.current_proxy
    
    def setup_firewall(self):
        """Setup firewall rules"""
        if self.security_config["firewall"]["block_suspicious_ips"]:
            self.blocked_ips = set()
        
        if self.security_config["firewall"]["rate_limiting"]:
            self.request_timestamps = []
            self.max_requests = self.security_config["firewall"]["max_requests_per_minute"]
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        if not self.security_config["firewall"]["rate_limiting"]:
            return True
        
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [t for t in self.request_timestamps 
                                  if current_time - t < 60]
        
        if len(self.request_timestamps) >= self.max_requests:
            return False
        
        self.request_timestamps.append(current_time)
        return True
    
    def mimic_human_behavior(self):
        """Mimic human behavior patterns"""
        if not self.security_config["stealth"]["behavior_mimicking"]:
            return
        
        # Random delays
        if self.security_config["stealth"]["random_delays"]:
            delay = random.uniform(0.5, 3.0)
            time.sleep(delay)
        
        # Simulate human thinking time
        if random.random() < 0.3:
            thinking_time = random.uniform(1.0, 5.0)
            time.sleep(thinking_time)
    
    def generate_fake_user_agent(self) -> str:
        """Generate random user agent"""
        user_agents = [
            # Windows Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Mac Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            # Linux Firefox
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            # Mobile Android
            "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            # Mobile iOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        ]
        
        return random.choice(user_agents)
    
    def detect_suspicious_activity(self, activity: str) -> bool:
        """Detect suspicious activity"""
        suspicious_patterns = [
            "too_many_requests",
            "unusual_timing",
            "repetitive_pattern",
            "automation_detected"
        ]
        
        # Simple detection logic
        if "automation" in activity.lower():
            self.detection_count += 1
            return True
        
        return False
    
    def handle_detection(self, detection_type: str):
        """Handle detection event"""
        print(f"🚨 Detection Alert: {detection_type}")
        
        self.detection_count += 1
        
        # Log detection
        self.log_security_event("detection", {
            "type": detection_type,
            "count": self.detection_count,
            "timestamp": datetime.now().isoformat()
        })
        
        # Take action based on severity
        if self.detection_count >= 3:
            print("⚠️ Multiple detections! Taking protective measures...")
            
            if self.security_config["monitoring"]["auto_backup_on_alert"]:
                self.trigger_backup()
            
            if self.security_config["monitoring"]["shutdown_on_detection"]:
                print("🛑 Shutting down due to multiple detections")
                self.emergency_shutdown()
        
        # Rotate proxy
        self.rotate_proxy()
        
        # Add random cooldown
        cooldown = random.uniform(30, 120)
        print(f"⏸️ Cooldown for {cooldown:.1f} seconds")
        time.sleep(cooldown)
    
    def log_security_event(self, event_type: str, data: Dict):
        """Log security event"""
        log_entry = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "detection_count": self.detection_count
        }
        
        log_file = "logs/security.log"
        os.makedirs("logs", exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def trigger_backup(self):
        """Trigger emergency backup"""
        print("💾 Triggering emergency backup...")
        
        try:
            # Import and use backup system
            from scripts.backup_system import BackupSystem
            backup = BackupSystem()
            backup.create_backup(f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            print("✅ Emergency backup completed")
            
        except Exception as e:
            print(f"❌ Emergency backup failed: {e}")
    
    def emergency_shutdown(self):
        """Emergency shutdown procedure"""
        print("🛑 EMERGENCY SHUTDOWN INITIATED")
        
        # Log shutdown
        self.log_security_event("emergency_shutdown", {
            "reason": "multiple_detections",
            "detection_count": self.detection_count
        })
        
        # Clean sensitive data
        self.clean_sensitive_data()
        
        # Exit program
        os._exit(1)
    
    def clean_sensitive_data(self):
        """Clean sensitive data from system"""
        sensitive_files = [
            "data/fb_cookies.pkl",
            "config/credentials.enc",
            "data/conversations/",
            "logs/security.log"
        ]
        
        for file_path in sensitive_files:
            try:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                    else:
                        # Overwrite with random data before deletion
                        with open(file_path, 'wb') as f:
                            f.write(os.urandom(os.path.getsize(file_path)))
                        os.remove(file_path)
                        
                    print(f"🧹 Cleaned: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not clean {file_path}: {e}")
    
    def generate_fingerprint(self) -> Dict:
        """Generate system fingerprint"""
        fingerprint = {
            "system": {
                "platform": os.name,
                "processor": os.environ.get('PROCESSOR_IDENTIFIER', 'unknown'),
                "username": os.environ.get('USERNAME', 'unknown'),
                "hostname": os.environ.get('COMPUTERNAME', 'unknown')
            },
            "network": {
                "public_ip": self.get_public_ip(),
                "local_ip": self.get_local_ip(),
                "mac_address": self.get_mac_address()
            },
            "timing": {
                "timezone": time.timezone,
                "timestamp": datetime.now().timestamp(),
                "clock_resolution": self.get_clock_resolution()
            }
        }
        
        return fingerprint
    
    def get_public_ip(self) -> str:
        """Get public IP address"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            return "unknown"
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "unknown"
    
    def get_mac_address(self) -> str:
        """Get MAC address"""
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,8*6,8)][::-1])
            return mac
        except:
            return "unknown"
    
    def get_clock_resolution(self) -> float:
        """Get system clock resolution"""
        times = []
        for _ in range(100):
            start = time.perf_counter()
            while time.perf_counter() == start:
                pass
            end = time.perf_counter()
            times.append(end - start)
        
        return min(times)
    
    def validate_environment(self) -> bool:
        """Validate running environment"""
        # Check for virtual machine
        vm_indicators = [
            "VMware", "VirtualBox", "qemu", "xen", "kvm",
            "docker", "container", "hyperv", "hyper-v"
        ]
        
        try:
            # Check CPU
            import platform
            cpu_info = platform.processor().lower()
            
            for indicator in vm_indicators:
                if indicator.lower() in cpu_info:
                    print(f"⚠️ VM detected: {indicator}")
                    return False
            
            # Check memory (VMs often have round numbers)
            import psutil
            total_memory = psutil.virtual_memory().total
            if total_memory % (1024**3) == 0:  # Exact GB
                print("⚠️ Suspicious memory size (common in VMs)")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Environment validation error: {e}")
            return True  # Assume valid if check fails
    
    def activate(self):
        """Activate security layer"""
        print("🛡️ Security layer activated")
        
        # Validate environment
        if not self.validate_environment():
            print("⚠️ Running in suspicious environment")
        
        # Initial proxy rotation
        if self.security_config["stealth"]["ip_rotation"]:
            self.rotate_proxy()
        
        # Log activation
        self.log_security_event("activation", {
            "fingerprint": self.generate_fingerprint(),
            "config": self.security_config
        })
    
    def deactivate(self):
        """Deactivate security layer"""
        print("🛡️ Security layer deactivated")
        
        # Cleanup
        if self.current_proxy:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
        
        # Log deactivation
        self.log_security_event("deactivation", {
            "total_detections": self.detection_count,
            "session_duration": (datetime.now() - self.last_activity).total_seconds()
        })