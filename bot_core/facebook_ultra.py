"""
🔥 FACEBOOK ULTRA - Advanced Automation
Military Grade Anti-Detection
"""

import os
import time
import random
import pickle
import json
from datetime import datetime
from typing import Dict, List, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import pyautogui
import numpy as np

class FacebookUltra:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.cookies_file = "data/fb_cookies.pkl"
        self.user_agent = UserAgent()
        self.proxy_list = []
        self.current_proxy = None
        self.fingerprint = self.generate_fingerprint()
        
    def generate_fingerprint(self):
        """Generate unique browser fingerprint"""
        return {
            "screen_resolution": f"{random.randint(1920, 3840)}x{random.randint(1080, 2160)}",
            "timezone": random.choice(["+06:00", "+05:30", "+07:00"]),
            "language": "bn-BD,bn;q=0.9,en;q=0.8",
            "platform": random.choice(["Win32", "Linux x86_64", "MacIntel"]),
            "hardware_concurrency": random.choice([4, 8, 12, 16]),
            "device_memory": random.choice([4, 8, 16]),
            "touch_support": random.choice([True, False]),
            "webgl_vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"])
        }
    
    def setup_stealth_driver(self):
        """Setup undetectable Chrome driver"""
        options = uc.ChromeOptions()
        
        # Random user agent
        ua = self.user_agent.random
        options.add_argument(f"user-agent={ua}")
        
        # Window size based on fingerprint
        width, height = map(int, self.fingerprint["screen_resolution"].split('x'))
        options.add_argument(f"--window-size={width},{height}")
        
        # Anti-detection arguments
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Language settings
        options.add_argument(f"--lang={self.fingerprint['language'].split(',')[0]}")
        
        # Experimental options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add custom fingerprint
        options.add_argument(f"--timezone={self.fingerprint['timezone']}")
        
        # Proxy support
        if self.current_proxy:
            options.add_argument(f'--proxy-server={self.current_proxy}')
        
        # Initialize driver
        self.driver = uc.Chrome(
            options=options,
            version_main=random.randint(110, 120),  # Random Chrome version
            headless=False,
            suppress_welcome=True
        )
        
        # Execute CDP commands to hide automation
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['bn-BD', 'bn', 'en']
                });
                window.chrome = { runtime: {} };
            """
        })
        
        # Set additional window properties
        self.driver.execute_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {self.fingerprint['hardware_concurrency']}
            }});
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {self.fingerprint['device_memory']}
            }});
            Object.defineProperty(navigator, 'maxTouchPoints', {{
                get: () => {10 if self.fingerprint['touch_support'] else 0}
            }});
        """)
        
        print(f"✅ Stealth driver initialized with fingerprint")
        print(f"   User Agent: {ua}")
        print(f"   Resolution: {self.fingerprint['screen_resolution']}")
    
    def human_like_typing(self, element, text, speed="normal"):
        """Type like a human with variable speed"""
        speeds = {
            "slow": (0.15, 0.3),
            "normal": (0.08, 0.15),
            "fast": (0.03, 0.08)
        }
        
        min_speed, max_speed = speeds.get(speed, (0.08, 0.15))
        
        for char in text:
            element.send_keys(char)
            
            # Random delay with occasional pauses
            if random.random() < 0.05:  # 5% chance of longer pause
                time.sleep(random.uniform(0.3, 0.8))
            else:
                time.sleep(random.uniform(min_speed, max_speed))
    
    def human_like_mouse(self):
        """Simulate human mouse movements"""
        actions = ActionChains(self.driver)
        
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Generate smooth bezier curve points
        points = self.generate_bezier_points(
            (current_x, current_y),
            (current_x + random.randint(100, 500), current_y + random.randint(-100, 100)),
            num_points=20
        )
        
        # Move through points
        for x, y in points:
            try:
                actions.move_by_offset(x - current_x, y - current_y)
                current_x, current_y = x, y
            except:
                pass
        
        # Random clicks
        if random.random() < 0.3:
            actions.click()
        
        # Scroll randomly
        if random.random() < 0.4:
            scroll_amount = random.randint(-300, 300)
            actions.scroll_by_amount(0, scroll_amount)
        
        actions.perform()
    
    def generate_bezier_points(self, start, end, num_points=20):
        """Generate smooth bezier curve points"""
        # Control point for curve
        control = (
            (start[0] + end[0]) / 2 + random.randint(-100, 100),
            (start[1] + end[1]) / 2 + random.randint(-100, 100)
        )
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Quadratic Bezier formula
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control[0] + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control[1] + t**2 * end[1]
            
            # Add some randomness
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            
            points.append((int(x), int(y)))
        
        return points
    
    def random_activity_simulation(self):
        """Simulate random human activity"""
        activities = [
            self.simulate_reading,
            self.simulate_scrolling,
            self.simulate_tab_switching,
            self.simulate_idle_time
        ]
        
        # Perform 2-4 random activities
        for _ in range(random.randint(2, 4)):
            activity = random.choice(activities)
            activity()
            time.sleep(random.uniform(1, 3))
    
    def simulate_reading(self):
        """Simulate reading content"""
        time.sleep(random.uniform(3, 8))
        
        # Occasional scroll while reading
        if random.random() < 0.7:
            self.driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
            time.sleep(random.uniform(1, 3))
    
    def simulate_scrolling(self):
        """Simulate natural scrolling"""
        scrolls = random.randint(2, 5)
        
        for _ in range(scrolls):
            direction = random.choice([-1, 1])
            amount = random.randint(200, 600) * direction
            
            # Smooth scroll
            self.driver.execute_script(f"""
                window.scrollBy({{
                    top: {amount},
                    behavior: 'smooth'
                }});
            """)
            
            time.sleep(random.uniform(0.5, 2))
    
    def simulate_tab_switching(self):
        """Simulate tab switching"""
        if len(self.driver.window_handles) > 1:
            # Switch to random tab
            tabs = self.driver.window_handles
            self.driver.switch_to.window(random.choice(tabs))
            time.sleep(random.uniform(2, 5))
            
            # Switch back
            self.driver.switch_to.window(tabs[0])
    
    def simulate_idle_time(self):
        """Simulate idle/thinking time"""
        idle_time = random.uniform(2, 10)
        time.sleep(idle_time)
    
    def rotate_proxy(self):
        """Rotate to next proxy"""
        if not self.proxy_list:
            return
        
        self.current_proxy = random.choice(self.proxy_list)
        print(f"🔄 Rotated proxy: {self.current_proxy}")
    
    def login(self):
        """Login to Facebook with stealth"""
        try:
            self.setup_stealth_driver()
            
            print("🌐 Navigating to Facebook...")
            self.driver.get("https://www.facebook.com")
            time.sleep(random.uniform(3, 5))
            
            # Check for saved cookies first
            if os.path.exists(self.cookies_file):
                print("🔑 Loading saved cookies...")
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                # Delete old cookies
                self.driver.delete_all_cookies()
                
                # Add saved cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                
                self.driver.refresh()
                time.sleep(random.uniform(3, 5))
                
                # Check if logged in
                if any(x in self.driver.current_url for x in ["home", "feed", "watch"]):
                    self.is_logged_in = True
                    print("✅ Auto-login successful via cookies!")
                    return True
            
            # Manual login required
            print("🔐 Performing manual login...")
            
            # Simulate human activity before login
            self.human_like_mouse()
            time.sleep(random.uniform(1, 2))
            
            # Find email field
            try:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                
                # Clear and type email
                email_input.clear()
                self.human_like_typing(email_input, os.getenv("FB_EMAIL"), speed="normal")
                time.sleep(random.uniform(1, 2))
                
                # Find password field
                pass_input = self.driver.find_element(By.ID, "pass")
                
                # Type password
                self.human_like_typing(pass_input, os.getenv("FB_PASSWORD"), speed="normal")
                time.sleep(random.uniform(1, 3))
                
                # Find login button
                login_button = self.driver.find_element(By.NAME, "login")
                
                # Human-like click delay
                time.sleep(random.uniform(0.5, 1.5))
                
                # Click login
                login_button.click()
                time.sleep(random.uniform(5, 8))
                
                # Check for login success
                if any(x in self.driver.current_url for x in ["home", "feed", "watch"]):
                    self.is_logged_in = True
                    
                    # Save cookies for next time
                    with open(self.cookies_file, 'wb') as f:
                        pickle.dump(self.driver.get_cookies(), f)
                    
                    print("✅ Manual login successful!")
                    
                    # Simulate post-login activity
                    self.random_activity_simulation()
                    
                    return True
                else:
                    # Check for 2FA or other challenges
                    if "checkpoint" in self.driver.current_url:
                        print("⚠️ Facebook checkpoint detected!")
                        print("  可能需要验证码或双重认证")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ Login form error: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Login process error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_unread_messages(self):
        """Get unread messages from Messenger"""
        if not self.is_logged_in:
            return []
        
        messages = []
        
        try:
            # Navigate to Messenger
            self.driver.get("https://www.facebook.com/messages")
            time.sleep(random.uniform(3, 5))
            
            # Simulate human activity
            self.random_activity_simulation()
            
            # Try to find unread messages
            # Note: Facebook frequently changes their DOM structure
            # This is a simplified version - needs regular updates
            
            # Method 1: Look for unread indicators
            try:
                unread_elements = self.driver.find_elements(
                    By.XPATH, "//div[contains(@aria-label, 'Unread') or contains(@class, 'unread')]"
                )
                
                for element in unread_elements[:5]:  # Limit to 5
                    try:
                        # Extract message info
                        message_text = element.text
                        if message_text and len(message_text) > 5:
                            # Try to find sender
                            sender = "Unknown"
                            parent = element.find_element(By.XPATH, "./ancestor::div[contains(@role, 'row')]")
                            
                            # Extract sender from parent
                            sender_elements = parent.find_elements(By.XPATH, ".//span[contains(@class, 'x1lliihq')]")
                            if sender_elements:
                                sender = sender_elements[0].text
                            
                            messages.append({
                                "sender": sender,
                                "message": message_text[:200],  # Limit length
                                "timestamp": datetime.now().isoformat()
                            })
                    except:
                        continue
                        
            except:
                pass
            
            # Method 2: Check recent conversations
            try:
                conversations = self.driver.find_elements(
                    By.XPATH, "//div[contains(@role, 'row') and contains(@tabindex, '-1')]"
                )[:10]
                
                for conv in conversations:
                    try:
                        conv.click()
                        time.sleep(2)
                        
                        # Get messages in conversation
                        message_elements = self.driver.find_elements(
                            By.XPATH, "//div[contains(@class, 'x78zum5') and contains(@class, 'x1n2onr6')]"
                        )
                        
                        if message_elements:
                            last_message = message_elements[-1].text
                            if last_message:
                                messages.append({
                                    "sender": "Conversation",
                                    "message": last_message[:200],
                                    "timestamp": datetime.now().isoformat()
                                })
                    except:
                        continue
                        
            except:
                pass
            
            print(f"📨 Found {len(messages)} new messages")
            return messages
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def send_message(self, user_id: str, message: str):
        """Send message to user"""
        if not self.is_logged_in:
            return False
        
        try:
            # Navigate to user's message page
            self.driver.get(f"https://www.facebook.com/messages/t/{user_id}")
            time.sleep(random.uniform(3, 5))
            
            # Simulate human activity
            self.random_activity_simulation()
            
            # Find message input
            try:
                # Try multiple selectors (Facebook changes frequently)
                selectors = [
                    "div[contenteditable='true']",
                    "div[aria-label='Message']",
                    "div[data-editor='true']",
                    "div[spellcheck='true']"
                ]
                
                message_box = None
                for selector in selectors:
                    try:
                        message_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if message_box:
                            break
                    except:
                        continue
                
                if not message_box:
                    raise Exception("Message box not found")
                
                # Type message
                message_box.click()
                time.sleep(random.uniform(0.5, 1))
                
                self.human_like_typing(message_box, message, speed="normal")
                time.sleep(random.uniform(1, 2))
                
                # Send message (Enter key)
                message_box.send_keys(Keys.ENTER)
                time.sleep(random.uniform(1, 3))
                
                # Simulate post-send activity
                self.random_activity_simulation()
                
                print(f"✅ Message sent to {user_id}")
                return True
                
            except Exception as e:
                print(f"❌ Error finding message box: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def join_group_search(self, keyword: str):
        """Search and join groups"""
        if not self.is_logged_in:
            return False
        
        try:
            # Search for groups
            self.driver.get(f"https://www.facebook.com/groups/search/groups/?q={keyword}")
            time.sleep(random.uniform(4, 6))
            
            # Scroll to load more results
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Find join buttons
            join_buttons = self.driver.find_elements(
                By.XPATH, "//span[text()='Join' or text()='Join Group' or text()='যোগ দেন']"
            )[:3]  # Limit to 3 groups
            
            joined_count = 0
            
            for button in join_buttons:
                try:
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                    time.sleep(random.uniform(1, 2))
                    
                    # Click join
                    button.click()
                    time.sleep(random.uniform(3, 5))
                    
                    joined_count += 1
                    print(f"✅ Joined group #{joined_count}")
                    
                    # Random delay between joins
                    time.sleep(random.uniform(10, 30))
                    
                except Exception as e:
                    print(f"⚠️ Error joining group: {e}")
                    continue
            
            print(f"✅ Joined {joined_count} groups for keyword: {keyword}")
            return joined_count > 0
            
        except Exception as e:
            print(f"❌ Error joining groups: {e}")
            return False
    
    def scan_groups_for_knowledge(self):
        """Scan joined groups for learning material"""
        if not self.is_logged_in:
            return []
        
        knowledge = []
        
        try:
            # Go to groups page
            self.driver.get("https://www.facebook.com/groups/")
            time.sleep(random.uniform(4, 6))
            
            # Get group links
            group_elements = self.driver.find_elements(
                By.XPATH, "//a[contains(@href, '/groups/') and contains(@role, 'link')]"
            )[:10]  # Limit to 10 groups
            
            for i, group in enumerate(group_elements[:5]):  # Visit first 5
                try:
                    group_url = group.get_attribute("href")
                    if "/groups/" in group_url and "permalink" not in group_url:
                        # Visit group
                        self.driver.get(group_url)
                        time.sleep(random.uniform(5, 8))
                        
                        # Scroll to load posts
                        for _ in range(2):
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
                            time.sleep(random.uniform(3, 5))
                        
                        # Extract posts
                        posts = self.driver.find_elements(
                            By.XPATH, "//div[contains(@data-ad-preview, 'message') or contains(@role, 'article')]"
                        )[:10]
                        
                        for post in posts:
                            try:
                                post_text = post.text.strip()
                                if post_text and len(post_text) > 20:
                                    knowledge.append({
                                        "source": f"Group {i+1}",
                                        "content": post_text[:500],
                                        "type": "post",
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except:
                                continue
                        
                        print(f"📖 Scanned group {i+1}: Found {len(posts)} posts")
                        
                        # Random delay between groups
                        time.sleep(random.uniform(10, 20))
                        
                except Exception as e:
                    print(f"⚠️ Error scanning group: {e}")
                    continue
            
            print(f"🧠 Collected {len(knowledge)} knowledge items")
            return knowledge
            
        except Exception as e:
            print(f"❌ Error scanning groups: {e}")
            return []
    
    def logout(self):
        """Logout and cleanup"""
        try:
            if self.driver:
                # Save cookies before quitting
                if self.is_logged_in:
                    with open(self.cookies_file, 'wb') as f:
                        pickle.dump(self.driver.get_cookies(), f)
                
                self.driver.quit()
            
            self.is_logged_in = False
            print("✅ Logged out and cleaned up")
            
        except Exception as e:
            print(f"❌ Logout error: {e}")