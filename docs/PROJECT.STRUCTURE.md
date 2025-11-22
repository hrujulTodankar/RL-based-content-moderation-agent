# Project Structure

Complete file organization for the RL-Powered Content Moderation system.

```
RL-Powered-Content-Moderation-Quality-Scoring-Agent/
│
├── 📄 main.py                          # FastAPI application entry point
├── 📄 moderation_agent.py              # RL-powered moderation agent
├── 📄 feedback_handler.py              # Feedback management and database
├── 📄 mcp_integration.py               # Multi-Channel Pipeline integrator
├── 📄 event_queue.py                   # Event queue for service communication
├── 📄 logger_middleware.py             # Logging middleware
│
├── 📄 test_moderation.py               # Comprehensive test suite
├── 📄 learning_kit.ipynb               # Interactive learning demonstration
│
├── 📄 requirements.txt                 # Python dependencies
├── 📄 Dockerfile                       # Docker container definition
├── 📄 docker-compose.yml               # Multi-service orchestration
├── 📄 .env.example                     # Environment variables template
├── 📄 .env                             # Local environment config (gitignored)
│
├── 📄 README.md                        # Complete documentation
├── 📄 PROJECT_STRUCTURE.md             # This file
│
├── 🔧 quickstart.sh                    # One-command setup script
├── 🔧 run_tests.sh                     # Automated testing script
│
├── 📁 logs/                            # Application logs (gitignored)
│   ├── app.log                         # Main application log
│   ├── requests.jsonl                  # HTTP request logs
│   ├── events.jsonl                    # Event queue logs
│   ├── moderation.db                   # SQLite database (dev)
│   └── moderation_learning_progress.png # Learning kit visualization
│
├── 📁 sample_data/                     # Sample test data (optional)
│   ├── clean_text.txt
│   ├── toxic_text.txt
│   ├── safe_code.py
│   └── dangerous_code.py
│
└── 📁 .github/                         # GitHub configuration (optional)
    └── workflows/
        └── test.yml                    # CI/CD pipeline

```

## File Descriptions

### Core Application Files

#### `main.py`
- **Purpose**: FastAPI application with all API endpoints
- **Key Features**:
  - `/moderate` - Content moderation endpoint
  - `/moderate/file` - File upload moderation
  - `/feedback` - User feedback submission
  - `/stats` - Statistics and analytics
  - `/health` - Health check
- **Dependencies**: FastAPI, uvicorn, pydantic
- **Lines**: ~400

#### `moderation_agent.py`
- **Purpose**: RL-powered moderation engine
- **Key Features**:
  - Q-learning algorithm implementation
  - Content-type specific rules (text, image, audio, video, code)
  - MCP confidence weighting
  - State/action/reward processing
- **Dependencies**: numpy
- **Lines**: ~450

#### `feedback_handler.py`
- **Purpose**: Feedback storage and retrieval
- **Key Features**:
  - Multi-database support (SQLite, PostgreSQL)
  - Feedback normalization to reward values
  - Statistics aggregation
  - Supabase compatibility
- **Dependencies**: aiosqlite, asyncpg
- **Lines**: ~350

#### `mcp_integration.py`
- **Purpose**: Integration with Multi-Channel Pipelines
- **Key Features**:
  - Async HTTP clients for Omkar RL, Aditya NLP, Ashmit Analytics
  - Result aggregation and weighting
  - Fallback mechanisms
  - Caching support
- **Dependencies**: httpx
- **Lines**: ~300

#### `event_queue.py`
- **Purpose**: Event-driven service communication
- **Key Features**:
  - Multiple event queues for different services
  - Subscriber pattern
  - Event logging to file
  - Background workers
- **Dependencies**: asyncio
- **Lines**: ~200

#### `logger_middleware.py`
- **Purpose**: HTTP request/response logging
- **Key Features**:
  - Request tracking
  - Performance metrics
  - Error logging
  - JSONL format output
- **Dependencies**: starlette
- **Lines**: ~120

### Testing Files

#### `test_moderation.py`
- **Purpose**: Comprehensive pytest test suite
- **Test Coverage**:
  - Moderation endpoint tests (8 test cases)
  - Feedback endpoint tests (3 test cases)
  - ModerationAgent unit tests (6 test cases)
  - FeedbackHandler tests (5 test cases)
  - File upload tests (1 test case)
  - Health/stats tests (2 test cases)
- **Total Tests**: 25+
- **Dependencies**: pytest, pytest-asyncio, httpx
- **Lines**: ~450

#### `learning_kit.ipynb`
- **Purpose**: Interactive learning demonstration
- **Sections**:
  1. Sample inputs → moderation
  2. User feedback simulation
  3. RL learning over iterations
  4. Performance visualization
  5. Statistics summary
- **Output**: PNG visualizations, performance metrics
- **Dependencies**: matplotlib, pandas, requests
- **Lines**: ~200

### Configuration Files

#### `requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
aiosqlite==0.19.0
asyncpg==0.29.0
httpx==0.25.1
numpy==1.26.2
pandas==2.1.3
pytest==7.4.3
pytest-asyncio==0.21.1
matplotlib==3.8.2
python-multipart==0.0.6
pydantic==2.5.0
python-json-logger==2.0.7
python-dotenv==1.0.0
```

#### `Dockerfile`
- **Base Image**: python:3.11-slim
- **Multi-stage**: Builder + Production
- **User**: Non-root (appuser)
- **Healthcheck**: Enabled
- **Workers**: 4 (configurable)
- **Size**: ~200MB

#### `docker-compose.yml`
- **Services**:
  - moderation-api (main service)
  - postgres (database)
  - omkar-rl (mock service)
  - aditya-nlp (mock service)
  - ashmit-analytics (mock service)
- **Networks**: Bridge network
- **Volumes**: PostgreSQL data persistence

#### `.env.example`
Template for environment variables with explanations.

### Scripts

#### `quickstart.sh`
- **Purpose**: One-command setup and deployment
- **Options**:
  1. Local development (SQLite)
  2. Docker Compose (full stack)
  3. Run tests only
- **Features**: 
  - Environment setup
  - Dependency installation
  - Service orchestration
  - User-friendly interface

#### `run_tests.sh`
- **Purpose**: Automated integration testing
- **Tests**:
  - 8 integration tests via cURL
  - Error handling validation
  - MCP metadata testing
  - Statistics verification
- **Output**: Color-coded results

## Usage Workflow

### Development Workflow
```bash
# 1. Clone repository
git clone <repo-url>
cd RL-Powered-Content-Moderation-Quality-Scoring-Agent

# 2. Quick setup
chmod +x quickstart.sh
./quickstart.sh
# Choose option 1 for local dev

# 3. Run tests
pytest test_moderation.py -v

# 4. Make changes to code
# Edit main.py, moderation_agent.py, etc.

# 5. Test changes
./run_tests.sh

# 6. Run learning kit
python learning_kit.ipynb
```

### Production Deployment
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with production settings

# 2. Deploy with Docker
chmod +x quickstart.sh
./quickstart.sh
# Choose option 2 for Docker

# 3. Verify deployment
curl http://localhost:8000/health

# 4. Monitor logs
docker-compose logs -f moderation-api

# 5. Scale if needed
docker-compose up -d --scale moderation-api=3
```

## Git Ignore Recommendations

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Logs
logs/
*.log
*.db
*.db-journal

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
htmlcov/
.coverage

# Docker
docker-compose.override.yml
```

## Database Schema

### SQLite/PostgreSQL Tables

**moderations table:**
```sql
CREATE TABLE moderations (
    moderation_id TEXT PRIMARY KEY,
    content_type TEXT NOT NULL,
    flagged BOOLEAN NOT NULL,
    score REAL NOT NULL,
    confidence REAL NOT NULL,
    mcp_weighted_score REAL,
    reasons TEXT/JSONB,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**feedback table:**
```sql
CREATE TABLE feedback (
    feedback_id TEXT PRIMARY KEY,
    moderation_id TEXT NOT NULL,
    user_id TEXT,
    feedback_type TEXT NOT NULL,
    rating INTEGER,
    comment TEXT,
    reward_value REAL NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (moderation_id) REFERENCES moderations(moderation_id)
);
```

## API Response Formats

All endpoints return JSON with consistent structure:

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-01-01T00:00:00"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Logging Format

All logs use JSONL format:
```json
{
  "timestamp": 1234567890.123,
  "level": "INFO",
  "message": "Request processed",
  "request_id": "req_1234567890123",
  "method": "POST",
  "path": "/moderate",
  "status_code": 200,
  "process_time": 0.123
}
```

## Performance Metrics

Expected performance on standard hardware:
- **Latency**: < 100ms for text moderation
- **Throughput**: 1000+ requests/minute
- **Memory**: < 200MB per worker
- **Database**: Supports 100K+ records efficiently

## Extension Points

Areas designed for easy extension:
1. **New Content Types**: Add to `moderation_agent.py`
2. **Additional MCP Services**: Extend `mcp_integration.py`
3. **Custom Rewards**: Modify `feedback_handler.normalize_feedback()`
4. **New Endpoints**: Add to `main.py`
5. **Alternative Databases**: Extend `feedback_handler.py`

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Maintainer**: Hrujul Todankar