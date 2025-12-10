"""
🏆 ULTRA MASTER BOT ENGINE
Professional Grade with Diagrams & Images
"""

import os
import sys
import json
import time
import random
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional
import requests
from colorama import Fore, Style

# Import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from facebook_ultra import FacebookUltra
    from diagram_generator import DiagramGenerator
    from image_creator import ImageCreator
    from firebase_ultra import FirebaseUltra
    from bengali_nlp_advanced import BengaliNLP
    from memory_ultra import MemoryUltra
    import cloudinary_pro as cloudinary
    import security_ultra as security
except ImportError as e:
    print(f"{Fore.RED}❌ Import Error: {e}")
    print(f"{Fore.YELLOW}Installing missing packages...")
    os.system("pip install -r requirements.txt")

class UltraMasterBot:
    def __init__(self):
        self.bot_name = "MASTER 🪓"
        self.author = "RANA"
        self.version = "4.0 ULTRA"
        self.status = "initializing"
        
        # Initialize modules
        self.fb = FacebookUltra()
        self.diagram = DiagramGenerator()
        self.image = ImageCreator()
        self.db = FirebaseUltra()
        self.nlp = BengaliNLP()
        self.memory = MemoryUltra()
        self.security = security.SecurityLayer()
        
        # Statistics
        self.stats = {
            "messages": 0,
            "diagrams_created": 0,
            "images_generated": 0,
            "profiles_scanned": 0,
            "start_time": datetime.now()
        }
        
        # Response templates
        self.load_templates()
        
        # WebSocket for realtime updates
        self.websocket_clients = []
        
    def load_templates(self):
        """Load response templates"""
        templates_path = "templates/bengali_responses.json"
        default_templates = {
            "greetings": [
                "হ্যালো! আমি MASTER 🪓, আপনার AI সহায়ক।",
                "নমস্কার! কেমন আছেন?",
                "আসসালামু আলাইকুম! আমি MASTER 🪓 বলছি।"
            ],
            "diagram_offer": [
                "আপনার কথাগুলো ডায়াগ্রাম আকারে দেখতে চান?",
                "চাইলে আমি একটি ডায়াগ্রাম তৈরি করতে পারি।",
                "ডায়াগ্রামে ব্যাখ্যা করলে বুঝতে সহজ হবে।"
            ],
            "image_offer": [
                "একটি ইমেজ তৈরি করি?",
                "চিত্র সহ ব্যাখ্যা চান?",
                "ভিজুয়ালাইজেশন তৈরি করি?"
            ]
        }
        
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except:
            self.templates = default_templates
            
        # Save default templates
        os.makedirs("templates", exist_ok=True)
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, ensure_ascii=False, indent=2)
    
    def analyze_message(self, message: str) -> Dict:
        """Analyze message for intent and content"""
        analysis = {
            "intent": "unknown",
            "needs_diagram": False,
            "needs_image": False,
            "language": "bengali",
            "keywords": [],
            "sentiment": "neutral"
        }
        
        # Detect language
        if self.nlp.detect_language(message) == "bengali":
            analysis["language"] = "bengali"
            analysis["keywords"] = self.nlp.extract_keywords_bengali(message)
        else:
            analysis["language"] = "english"
            analysis["keywords"] = self.nlp.extract_keywords_english(message)
        
        # Detect intent
        message_lower = message.lower()
        
        # Diagram related keywords
        diagram_keywords = ["ডায়াগ্রাম", "চার্ট", "গ্রাফ", "ফ্লোচার্ট", "ছবি", "চিত্র", 
                          "diagram", "chart", "graph", "flowchart", "visualize"]
        
        # Image related keywords
        image_keywords = ["ইমেজ", "ছবি", "ফটো", "পিকচার", "অঙ্কন", "ডিজাইন",
                         "image", "photo", "picture", "draw", "design"]
        
        if any(keyword in message_lower for keyword in diagram_keywords):
            analysis["intent"] = "diagram"
            analysis["needs_diagram"] = True
            
        elif any(keyword in message_lower for keyword in image_keywords):
            analysis["intent"] = "image"
            analysis["needs_image"] = True
            
        elif any(word in message_lower for word in ["হ্যালো", "হাই", "hello", "hi"]):
            analysis["intent"] = "greeting"
            
        elif any(word in message_lower for word in ["ধন্যবাদ", "থ্যাংকস", "thank"]):
            analysis["intent"] = "thanks"
            
        elif "?" in message:
            analysis["intent"] = "question"
            
        # Sentiment analysis
        analysis["sentiment"] = self.nlp.analyze_sentiment(message)
        
        return analysis
    
    def create_diagram_response(self, content: str) -> Dict:
        """Create diagram from text content"""
        try:
            # Generate diagram
            diagram_data = self.diagram.create_from_text(content)
            
            # Save to Firebase
            diagram_id = self.db.save_diagram(diagram_data)
            
            # Generate URL
            diagram_url = f"http://localhost:8080/diagrams/{diagram_id}"
            
            # Upload to Cloudinary
            cloudinary_url = cloudinary.upload_diagram(diagram_data)
            
            self.stats["diagrams_created"] += 1
            
            return {
                "success": True,
                "diagram_url": diagram_url,
                "cloudinary_url": cloudinary_url,
                "message": "✅ ডায়াগ্রাম তৈরি সম্পূর্ণ!",
                "diagram_id": diagram_id
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Diagram Error: {e}")
            return {
                "success": False,
                "message": "ডায়াগ্রাম তৈরি করতে সমস্যা হচ্ছে।"
            }
    
    def create_image_response(self, description: str) -> Dict:
        """Create image from description"""
        try:
            # Generate image
            image_data = self.image.generate_from_text(description)
            
            # Save to Firebase
            image_id = self.db.save_image(image_data)
            
            # Generate URL
            image_url = f"http://localhost:8080/images/{image_id}"
            
            # Upload to Cloudinary
            cloudinary_url = cloudinary.upload_image(image_data)
            
            self.stats["images_generated"] += 1
            
            return {
                "success": True,
                "image_url": image_url,
                "cloudinary_url": cloudinary_url,
                "message": "✅ ইমেজ তৈরি সম্পূর্ণ!",
                "image_id": image_id
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Image Error: {e}")
            return {
                "success": False,
                "message": "ইমেজ তৈরি করতে সমস্যা হচ্ছে।"
            }
    
    def generate_intelligent_response(self, message: str, sender_id: str) -> str:
        """Generate intelligent response with diagrams/images"""
        analysis = self.analyze_message(message)
        
        # Check memory for similar conversations
        memory_response = self.memory.recall_conversation(sender_id, message)
        if memory_response:
            return memory_response
        
        # Generate base response
        if analysis["intent"] == "greeting":
            response = random.choice(self.templates["greetings"])
        elif analysis["intent"] == "diagram" or analysis["needs_diagram"]:
            diagram_result = self.create_diagram_response(message)
            if diagram_result["success"]:
                response = f"{diagram_result['message']}\nডায়াগ্রাম লিঙ্ক: {diagram_result['diagram_url']}"
            else:
                response = diagram_result["message"]
        elif analysis["intent"] == "image" or analysis["needs_image"]:
            image_result = self.create_image_response(message)
            if image_result["success"]:
                response = f"{image_result['message']}\nইমেজ লিঙ্ক: {image_result['image_url']}"
            else:
                response = image_result["message"]
        else:
            # Generate generic response
            response = self.nlp.generate_response(message)
        
        # Store in memory
        self.memory.store_conversation(sender_id, message, response)
        
        return response
    
    def process_facebook_messages(self):
        """Process Facebook messages"""
        print(f"{Fore.CYAN}📨 Processing Facebook Messages...{Style.RESET_ALL}")
        
        while True:
            try:
                # Get unread messages
                messages = self.fb.get_unread_messages()
                
                for msg in messages:
                    sender_id = msg["sender_id"]
                    message_text = msg["message"]
                    
                    print(f"{Fore.YELLOW}👤 {sender_id}: {message_text}{Style.RESET_ALL}")
                    
                    # Generate response
                    response = self.generate_intelligent_response(message_text, sender_id)
                    
                    # Send response
                    self.fb.send_message(sender_id, response)
                    
                    # Log statistics
                    self.stats["messages"] += 1
                    
                    print(f"{Fore.GREEN}🤖 MASTER: {response[:50]}...{Style.RESET_ALL}")
                    
                    # Human-like delay
                    time.sleep(random.uniform(1, 3))
                
                # Sleep if no messages
                time.sleep(5)
                
            except Exception as e:
                print(f"{Fore.RED}❌ Message Processing Error: {e}{Style.RESET_ALL}")
                time.sleep(10)
    
    def start_auto_learning(self):
        """Start auto-learning from conversations"""
        print(f"{Fore.BLUE}🧠 Starting Auto-Learning Mode...{Style.RESET_ALL}")
        
        # Join learning groups
        learning_groups = ["বাংলা প্রোগ্রামিং", "AI Bangladesh", "Machine Learning Bangla"]
        
        for group in learning_groups:
            self.fb.join_group_search(group)
            time.sleep(30)
        
        # Start monitoring groups for learning
        while True:
            try:
                # Scan groups for new knowledge
                new_knowledge = self.fb.scan_groups_for_knowledge()
                
                # Process and store knowledge
                for knowledge in new_knowledge:
                    self.memory.store_knowledge(knowledge)
                    self.db.save_knowledge(knowledge)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Learning Error: {e}{Style.RESET_ALL}")
                time.sleep(30)
    
    def show_dashboard(self):
        """Show realtime dashboard"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            runtime = datetime.now() - self.stats["start_time"]
            hours = runtime.total_seconds() / 3600
            
            print(f"""
            {Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
            {Fore.GREEN}🤖 MASTER ULTRA BOT DASHBOARD{Style.RESET_ALL}
            {Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
            {Fore.YELLOW}🆔 Bot Name: {self.bot_name}
            {Fore.YELLOW}👤 Author: {self.author}
            {Fore.YELLOW}📊 Version: {self.version}
            {Fore.YELLOW}⏰ Uptime: {hours:.2f} hours
            {Fore.YELLOW}📨 Messages: {self.stats['messages']}
            {Fore.YELLOW}📊 Diagrams: {self.stats['diagrams_created']}
            {Fore.YELLOW}🖼️ Images: {self.stats['images_generated']}
            {Fore.YELLOW}👥 Profiles: {self.stats['profiles_scanned']}
            {Fore.YELLOW}🔒 Security: {self.security.status}
            {Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
            {Fore.GREEN}🌐 Web Dashboard: http://localhost:8080
            {Fore.BLUE}📱 Control Panel: http://localhost:8080/control
            {Fore.MAGENTA}📊 Analytics: http://localhost:8080/analytics
            {Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
            """)
            
            time.sleep(5)
    
    def start(self):
        """Start the Ultra Master Bot"""
        print(f"{Fore.GREEN}🚀 Starting ULTRA MASTER BOT...{Style.RESET_ALL}")
        
        # Start security layer
        self.security.activate()
        
        # Login to Facebook
        print(f"{Fore.BLUE}🔐 Logging into Facebook...{Style.RESET_ALL}")
        if not self.fb.login():
            print(f"{Fore.RED}❌ Facebook login failed!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}✅ Facebook login successful!{Style.RESET_ALL}")
        
        # Start threads
        threads = []
        
        # Message processing thread
        msg_thread = threading.Thread(target=self.process_facebook_messages, daemon=True)
        threads.append(msg_thread)
        msg_thread.start()
        
        # Auto-learning thread
        learn_thread = threading.Thread(target=self.start_auto_learning, daemon=True)
        threads.append(learn_thread)
        learn_thread.start()
        
        # Dashboard thread
        dash_thread = threading.Thread(target=self.show_dashboard, daemon=True)
        threads.append(dash_thread)
        dash_thread.start()
        
        print(f"{Fore.GREEN}✅ All systems started!{Style.RESET_ALL}")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Shutting down...{Style.RESET_ALL}")
            self.security.deactivate()
            self.fb.logout()
            print(f"{Fore.GREEN}✅ Shutdown complete!{Style.RESET_ALL}")

# Run the bot
if __name__ == "__main__":
    bot = UltraMasterBot()
    bot.start()