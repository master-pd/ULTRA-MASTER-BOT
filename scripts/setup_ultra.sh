#!/bin/bash
# 🚀 ULTRA MASTER BOT - ONE CLICK SETUP
# Author: RANA (MASTER 🪓)

echo "🤖 MASTER ULTRA BOT SETUP"
echo "=========================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/8]${NC} Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python3 not found! Installing...${NC}"
    sudo apt-get update
    sudo apt-get install python3 python3-pip -y
fi

# Check Node.js
echo -e "${BLUE}[2/8]${NC} Checking Node.js..."
node --version
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Node.js not found! Installing...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install nodejs -y
fi

# Create virtual environment
echo -e "${BLUE}[3/8]${NC} Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}[4/8]${NC} Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo -e "${BLUE}[5/8]${NC} Installing Node.js dependencies..."
npm install

# Create necessary directories
echo -e "${BLUE}[6/8]${NC} Creating directories..."
mkdir -p data/conversations data/diagrams data/images data/backups
mkdir -p templates logs

# Create .env file if not exists
echo -e "${BLUE}[7/8]${NC} Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your credentials!${NC}"
fi

# Set permissions
echo -e "${BLUE}[8/8]${NC} Setting permissions..."
chmod +x run_ultra.py
chmod +x scripts/*.sh
chmod +x scripts/*.py

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the bot: python run_ultra.py"
echo ""
echo -e "${BLUE}🔥 MASTER ULTRA BOT READY TO RUN!${NC}"