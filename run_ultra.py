#!/usr/bin/env python3
"""
🚀 ULTRA MASTER BOT - MAIN RUNNER
Complete with Web Server & Bot Launcher
"""

import os
import sys
import time
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class MasterBotRunner:
    def __init__(self):
        self.web_port = 8080
        self.bot_process = None
        self.web_server = None
        self.is_running = False
        
    def check_ports(self):
        """Check if ports are available"""
        try:
            # Check web port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', self.web_port))
            sock.close()
            
            if result == 0:
                print(f"{Fore.YELLOW}⚠️ Port {self.web_port} is already in use")
                self.web_port += 1
                print(f"{Fore.YELLOW}⚠️ Trying port {self.web_port} instead")
            
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Port check error: {e}")
            return False
    
    def start_web_server(self):
        """Start HTTP web server"""
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory="web_dashboard", **kwargs)
            
            def log_message(self, format, *args):
                # Customize logging
                print(f"{Fore.CYAN}🌐 Web: {format % args}")
        
        try:
            # Create server
            self.web_server = HTTPServer(('0.0.0.0', self.web_port), Handler)
            
            # Start in separate thread
            server_thread = threading.Thread(target=self.web_server.serve_forever, daemon=True)
            server_thread.start()
            
            print(f"{Fore.GREEN}✅ Web server started on port {self.web_port}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Web server error: {e}")
            return False
    
    def start_bot(self):
        """Start the main bot"""
        try:
            print(f"{Fore.BLUE}🤖 Starting MASTER ULTRA BOT...{Style.RESET_ALL}")
            
            # Import and start bot
            from bot_core.master_ultra import UltraMasterBot
            
            bot = UltraMasterBot()
            
            # Start bot in separate thread
            bot_thread = threading.Thread(target=bot.start, daemon=True)
            bot_thread.start()
            
            self.bot_process = bot_thread
            self.is_running = True
            
            print(f"{Fore.GREEN}✅ Bot started successfully!{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Bot startup error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def open_browser(self):
        """Open web browser"""
        try:
            url = f"http://localhost:{self.web_port}"
            webbrowser.open(url)
            print(f"{Fore.GREEN}🌐 Browser opened: {url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Could not open browser: {e}")
    
    def display_banner(self):
        """Display awesome ASCII banner"""
        banner = f"""
{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
{Fore.RED}╔═╗╦ ╦╔═╗╔═╗╔╦╗╔═╗{Fore.YELLOW}╔╦╗╔═╗╔╗╔╔═╗╦═╗  ╔╦╗╔═╗╔╦╗
{Fore.RED}╠═╣║ ║║  ╠═╣ ║ ║╣ {Fore.YELLOW}║║║╠═╣║║║║╣ ╠╦╝   ║ ╠═╣ ║ 
{Fore.RED}╩ ╩╚═╝╚═╝╩ ╩ ╩ ╚═╝{Fore.YELLOW}╩ ╩╩ ╩╝╚╝╚═╝╩╚═   ╩ ╩ ╩ ╩ 
{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
{Fore.GREEN}🤖 Version: 4.0 ULTRA
{Fore.YELLOW}👑 Author: RANA (MASTER 🪓)
{Fore.MAGENTA}📍 From: Faridpur, Dhaka
{Fore.CYAN}🎯 Dream: Professional Developer
{Fore.WHITE}📧 Email: ranaeditz333@gmail.com
{Fore.BLUE}📱 Support: @black_lovers1_bot
{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
{Fore.YELLOW}🚀 Features:{Style.RESET_ALL}
{Fore.WHITE}• Self-learning AI with Bengali NLP
{Fore.WHITE}• Automatic Diagram Generation
{Fore.WHITE}• AI Image Creation
{Fore.WHITE}• Facebook Messenger Automation
{Fore.WHITE}• Firebase & Cloudinary Integration
{Fore.WHITE}• Military Grade Security
{Fore.WHITE}• Professional Web Dashboard
{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}
"""
        print(banner)
    
    def check_dependencies(self):
        """Check and install dependencies"""
        print(f"{Fore.BLUE}🔍 Checking dependencies...{Style.RESET_ALL}")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print(f"{Fore.RED}❌ Python 3.8+ required!{Style.RESET_ALL}")
            return False
        
        # Check required files
        required_files = [
            "requirements.txt",
            "bot_core/master_ultra.py",
            "web_dashboard/index.html",
            ".env"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{Fore.RED}❌ Missing files: {missing_files}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please run setup script first!{Style.RESET_ALL}")
            return False
        
        # Try to install requirements
        try:
            print(f"{Fore.BLUE}📦 Installing Python packages...{Style.RESET_ALL}")
            os.system(f"{sys.executable} -m pip install -r requirements.txt --quiet")
        except:
            print(f"{Fore.YELLOW}⚠️ Could not auto-install packages{Style.RESET_ALL}")
        
        return True
    
    def run(self):
        """Main runner method"""
        self.display_banner()
        
        # Check dependencies
        if not self.check_dependencies():
            print(f"{Fore.RED}❌ Dependency check failed!{Style.RESET_ALL}")
            sys.exit(1)
        
        # Check ports
        if not self.check_ports():
            print(f"{Fore.RED}❌ Port check failed!{Style.RESET_ALL}")
            sys.exit(1)
        
        # Start web server
        print(f"{Fore.BLUE}🚀 Starting web server...{Style.RESET_ALL}")
        if not self.start_web_server():
            print(f"{Fore.RED}❌ Web server failed!{Style.RESET_ALL}")
            sys.exit(1)
        
        # Start bot
        print(f"{Fore.BLUE}🤖 Starting bot engine...{Style.RESET_ALL}")
        if not self.start_bot():
            print(f"{Fore.YELLOW}⚠️ Bot startup had issues, continuing...{Style.RESET_ALL}")
        
        # Open browser
        print(f"{Fore.BLUE}🌐 Opening dashboard...{Style.RESET_ALL}")
        self.open_browser()
        
        # Display info
        print(f"\n{Fore.GREEN}✅ MASTER ULTRA BOT IS RUNNING!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Dashboard: http://localhost:{self.web_port}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📱 Control Panel: http://localhost:{self.web_port}/control{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📈 Analytics: http://localhost:{self.web_port}/analytics{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Press Ctrl+C to stop the bot{Style.RESET_ALL}")
        
        # Keep running
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Shutting down...{Style.RESET_ALL}")
            self.stop()
    
    def stop(self):
        """Stop everything"""
        print(f"{Fore.YELLOW}🛑 Stopping bot...{Style.RESET_ALL}")
        
        self.is_running = False
        
        # Stop web server
        if self.web_server:
            self.web_server.shutdown()
            print(f"{Fore.GREEN}✅ Web server stopped{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}")

def main():
    """Main function"""
    runner = MasterBotRunner()
    
    try:
        runner.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Exiting...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()