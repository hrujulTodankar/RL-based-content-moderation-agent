#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  RL Moderation API - Test Suite${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Check if API is running
echo -e "${YELLOW}Checking if API is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ API is running${NC}\n"
else
    echo -e "${RED}✗ API is not running. Please start it first:${NC}"
    echo -e "  uvicorn main:app --host 0.0.0.0 --port 8000\n"
    exit 1
fi

# Test 1: Text Moderation (Clean)
echo -e "${YELLOW}Test 1: Text Moderation (Clean Content)${NC}"
response=$(curl -s -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is a wonderful day!", "content_type": "text"}')

if echo "$response" | grep -q '"flagged":false'; then
    echo -e "${GREEN}✓ Passed${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 2: Text Moderation (Flagged)
echo -e "${YELLOW}Test 2: Text Moderation (Flagged Content)${NC}"
response=$(curl -s -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{"content": "hate spam kill violent abuse", "content_type": "text"}')

if echo "$response" | grep -q '"flagged":true'; then
    echo -e "${GREEN}✓ Passed${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 3: Code Moderation (Dangerous)
echo -e "${YELLOW}Test 3: Code Moderation (Dangerous Code)${NC}"
response=$(curl -s -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{"content": "import os\\nos.system(\"rm -rf /\")\\nexec(malicious)", "content_type": "code"}')

moderation_id=$(echo "$response" | jq -r '.moderation_id')
if echo "$response" | grep -q '"flagged":true'; then
    echo -e "${GREEN}✓ Passed${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 4: Feedback Submission (Thumbs Up)
echo -e "${YELLOW}Test 4: Feedback Submission (Thumbs Up)${NC}"
if [ ! -z "$moderation_id" ]; then
    response=$(curl -s -X POST "http://localhost:8000/feedback" \
      -H "Content-Type: application/json" \
      -d "{\"moderation_id\": \"$moderation_id\", \"feedback_type\": \"thumbs_up\", \"rating\": 5}")
    
    if echo "$response" | grep -q '"status":"processed"'; then
        echo -e "${GREEN}✓ Passed${NC}"
        echo "$response" | jq '.'
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no moderation_id)${NC}"
fi
echo ""

# Test 5: Feedback Submission (Thumbs Down)
echo -e "${YELLOW}Test 5: Feedback Submission (Thumbs Down)${NC}"
if [ ! -z "$moderation_id" ]; then
    response=$(curl -s -X POST "http://localhost:8000/feedback" \
      -H "Content-Type: application/json" \
      -d "{\"moderation_id\": \"$moderation_id\", \"feedback_type\": \"thumbs_down\", \"rating\": 2, \"comment\": \"False positive\"}")
    
    if echo "$response" | grep -q '"status":"processed"'; then
        echo -e "${GREEN}✓ Passed${NC}"
        echo "$response" | jq '.'
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
else
    echo -e "${YELLOW}⊘ Skipped (no moderation_id)${NC}"
fi
echo ""

# Test 6: Statistics Endpoint
echo -e "${YELLOW}Test 6: Statistics Endpoint${NC}"
response=$(curl -s "http://localhost:8000/stats")

if echo "$response" | grep -q 'total_moderations'; then
    echo -e "${GREEN}✓ Passed${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 7: MCP-Aware Moderation
echo -e "${YELLOW}Test 7: MCP-Aware Moderation${NC}"
response=$(curl -s -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test with MCP metadata",
    "content_type": "text",
    "mcp_metadata": {
      "nlp_confidence": 0.9,
      "conversion_quality": 0.85,
      "sentiment_score": 0.7
    }
  }')

if echo "$response" | grep -q 'mcp_weighted_score'; then
    echo -e "${GREEN}✓ Passed${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}✗ Failed${NC}"
fi
echo ""

# Test 8: Invalid Content Type
echo -e "${YELLOW}Test 8: Invalid Content Type (Error Handling)${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8000/moderate" \
  -H "Content-Type: application/json" \
  -d '{"content": "test", "content_type": "invalid"}')

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "400" ]; then
    echo -e "${GREEN}✓ Passed (HTTP 400 returned)${NC}"
else
    echo -e "${RED}✗ Failed (Expected HTTP 400, got $http_code)${NC}"
fi
echo ""

# Summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Test Suite Complete${NC}"
echo -e "${YELLOW}========================================${NC}\n"

echo -e "To run Python unit tests:"
echo -e "  ${GREEN}pytest test_moderation.py -v${NC}\n"

echo -e "To run learning kit demo:"
echo -e "  ${GREEN}python learning_kit.ipynb${NC}\n"