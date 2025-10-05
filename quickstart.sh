## 7. quickstart.sh (Complete Version)
```bash
#!/bin/bash

# Quick Start Script for RL-Powered Content Moderation API
# This script sets up and runs the entire system

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║   RL-Powered Content Moderation API - Quick Start        ║
║   Production-Ready with MCP Integration                  ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo -e "${RED}✗ Python 3.11+ required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version${NC}\n"

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}\n"

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Setup environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << 'ENVFILE'
# Database Configuration
DB_TYPE=sqlite
DB_PATH=logs/moderation.db

# MCP Service URLs (using mock services)
OMKAR_RL_URL=http://localhost:8001
ADITYA_NLP_URL=http://localhost:8002
ASHMIT_ANALYTICS_URL=http://localhost:8003

# Application Settings
LOG_LEVEL=INFO
ENVFILE
    echo -e "${GREEN}✓ .env file created${NC}\n"
else
    echo -e "${GREEN}✓ .env file already exists${NC}\n"
fi

# Ask user for deployment mode
echo -e "${BLUE}Choose deployment mode:${NC}"
echo "  1) Local Development (SQLite, single process)"
echo "  2) Docker Compose (PostgreSQL, all services)"
echo "  3) Run Tests Only"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Starting Local Development Server...${NC}\n"
        echo -e "${BLUE}API will be available at: http://localhost:8000${NC}"
        echo -e "${BLUE}API Documentation: http://localhost:8000/docs${NC}"
        echo -e "${BLUE}Health Check: http://localhost:8000/health${NC}\n"
        
        echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"
        sleep 2
        
        # Start the server
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    
    2)
        echo -e "\n${YELLOW}Starting Docker Compose...${NC}\n"
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}✗ Docker Compose not found. Please install Docker Compose first.${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Docker and Docker Compose found${NC}\n"
        
        # Build and start services
        echo -e "${YELLOW}Building Docker images...${NC}"
        docker-compose build
        
        echo -e "${YELLOW}Starting all services...${NC}"
        docker-compose up -d
        
        echo -e "\n${GREEN}✓ All services started${NC}\n"
        
        echo -e "${BLUE}Services:${NC}"
        echo -e "  • Moderation API: http://localhost:8000"
        echo -e "  • PostgreSQL: localhost:5432"
        echo -e "  • Omkar RL: http://localhost:8001"
        echo -e "  • Aditya NLP: http://localhost:8002"
        echo -e "  • Ashmit Analytics: http://localhost:8003"
        echo -e "\n${BLUE}View logs:${NC}"
        echo -e "  docker-compose logs -f moderation-api"
        echo -e "\n${BLUE}Stop services:${NC}"
        echo -e "  docker-compose down"
        ;;
    
    3)
        echo -e "\n${YELLOW}Running Tests...${NC}\n"
        
        # Start API in background
        echo -e "${YELLOW}Starting API for testing...${NC}"
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        API_PID=$!
        
        # Wait for API to start
        echo -e "${YELLOW}Waiting for API to start...${NC}"
        sleep 5
        
        # Run tests
        echo -e "\n${BLUE}Running Python unit tests...${NC}\n"
        pytest test_moderation.py -v --tb=short
        
        echo -e "\n${BLUE}Running integration tests...${NC}\n"
        if [ -f "run_tests.sh" ]; then
            bash run_tests.sh
        else
            echo -e "${YELLOW}run_tests.sh not found, skipping integration tests${NC}"
        fi
        
        # Stop API
        echo -e "\n${YELLOW}Stopping API...${NC}"
        kill $API_PID
        
        echo -e "\n${GREEN}✓ All tests completed${NC}\n"
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Quick Commands:${NC}"
echo -e "  • View logs:      ${YELLOW}tail -f logs/app.log${NC}"
echo -e "  • Run tests:      ${YELLOW}pytest test_moderation.py -v${NC}"
echo -e "  • Run demo:       ${YELLOW}python learning_kit.py${NC}"
echo -e "  • API docs:       ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "  • Health check:   ${YELLOW}curl http://localhost:8000/health${NC}"

echo -e "\n${BLUE}Example API calls:${NC}"
echo -e "${YELLOW}# Moderate text${NC}"
echo -e 'curl -X POST "http://localhost:8000/moderate" \\'
echo -e '  -H "Content-Type: application/json" \\'
echo -e '  -d '"'"'{"content": "test message", "content_type": "text"}'"'"

echo -e "\n${YELLOW}# Submit feedback${NC}"
echo -e 'curl -X POST "http://localhost:8000/feedback" \\'
echo -e '  -H "Content-Type: application/json" \\'
echo -e '  -d '"'"'{"moderation_id": "xxx", "feedback_type": "thumbs_up", "rating": 5}'"'"

echo -e "\n${YELLOW}# Get statistics${NC}"
echo -e 'curl "http://localhost:8000/stats" | jq .'

echo -e "\n${GREEN}Happy Moderating! 🚀${NC}\n"