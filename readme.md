# RL-Powered Content Moderation System with Indian Legal Content Transparency

## Project Overview
This project implements an advanced content moderation system powered by Reinforcement Learning (RL) that automatically learns and improves from user feedback. The system specializes in moderating Indian legal content with complete transparency features, showing approved and rejected content with detailed reasoning.

The system can moderate various types of content including text, images, audio, video, and code snippets, with special focus on Indian legal documents like Bharatiya Nyaya Sanhita (BNS) and Code of Criminal Procedure (CrPC).

### Key Features
1. **Advanced Indian Legal Content Moderation**
    - Bharatiya Nyaya Sanhita (BNS) 2023 content moderation
    - Code of Criminal Procedure (CrPC) 1973 content moderation
    - Dynamic approval/rejection reasons based on legal content analysis
    - Complete transparency with visual distinction between approved/rejected content

2. **Enhanced Multi-Modal Content Support**
    - Text moderation with NLP context understanding
    - Image content analysis with NSFW detection
    - Audio content processing with transcription analysis
    - Advanced video content analysis with frame-by-frame evaluation
    - Code snippet evaluation with security pattern detection

3. **Advanced RL-Powered Adaptive Learning**
    - Enhanced Q-Learning algorithm with persistent state
    - Replay buffer for batch learning from past experiences
    - Pretraining capabilities for seeding Q-values
    - Real-time learning from user feedback with reward normalization
    - Confidence-based decision making with bounds checking
    - Historical performance tracking and metrics
    - Automated improvement over time with state persistence

4. **Complete Transparency Features**
    - Approved content (green) with specific approval reasons
    - Rejected content (red) with detailed rejection reasons
    - Content-aware analysis for legal terminology, structure, and procedural elements
    - Score-based dynamic reasoning with MCP weighting
    - Enhanced state key generation for better learning

5. **Advanced Security & Authentication**
    - JWT authentication with refresh tokens
    - Rate limiting (per endpoint, per user, per IP)
    - Input sanitization and validation
    - Security headers and middleware
    - Authentication rate limiting with lockout protection
    - Comprehensive audit logging

6. **Observability & Monitoring**
    - Sentry error tracking integration
    - PostHog user analytics
    - Performance monitoring and metrics
    - Structured logging with correlation IDs
    - Health checks and system monitoring
    - Real-time performance tracking

7. **GDPR Compliance & Privacy**
    - Complete data export functionality
    - User data deletion with cascade
    - Privacy policy and data summary endpoints
    - Audit trails for all data operations
    - Automated data retention policies

8. **Multi-Storage Backend Support**
    - Supabase Storage integration
    - AWS S3 compatibility
    - MinIO support
    - Local file system fallback
    - Presigned URL generation

9. **Enhanced Analytics & Sentiment Analysis**
    - Advanced sentiment analysis integration
    - Content performance metrics
    - User engagement tracking
    - RL agent performance analytics
    - Comprehensive statistics dashboard

10. **Task Queue & Background Processing**
    - Asynchronous task processing
    - Background workers with retry logic
    - Task status tracking and management
    - Queue statistics and monitoring
    - Scalable background job processing

11. **Integration Capabilities**
    - Model Context Protocol (MCP) integration
    - Event-driven architecture with async queues
    - Scalable feedback handling with database persistence
    - Real-time analytics with WebSocket support
    - Comprehensive API with 15+ endpoints

## Technical Architecture

### Core Components
1. **Advanced Moderation Agent** (`app/moderation_agent.py`)
    - Enhanced Q-Learning RL implementation with persistent state
    - Replay buffer for batch learning from past experiences
    - Pretraining capabilities for seeding Q-values
    - Advanced state key generation from content features
    - Multi-modal content moderation (text, image, audio, video, code)
    - MCP confidence weighting and cross-service integration

2. **Security & Authentication System** (`app/security.py`, `app/auth_middleware.py`)
    - JWT authentication with refresh token support
    - Rate limiting (per endpoint, per user, per IP)
    - Input sanitization and validation middleware
    - Security headers and comprehensive audit logging
    - Authentication rate limiting with lockout protection

3. **Observability & Monitoring** (`app/observability.py`, `app/logger_middleware.py`)
    - Sentry error tracking integration
    - PostHog user analytics and event tracking
    - Performance monitoring and structured logging
    - Health checks and system metrics
    - Correlation ID tracking for request tracing

4. **Feedback Handler** (`app/feedback_handler.py`)
    - Processes user feedback with reward normalization
    - Maintains feedback database with multiple backends
    - Generates comprehensive performance metrics
    - RL agent integration for continuous learning

5. **Task Queue System** (`app/task_queue.py`)
    - Asynchronous task processing with background workers
    - Retry logic and error handling
    - Task status tracking and queue statistics
    - Scalable background job processing

6. **Event Queue** (`app/event_queue.py`)
    - Manages asynchronous events and background tasks
    - Event logging and system responsiveness
    - Integration with task queue for complex workflows

7. **Integration Services** (`app/integration_services.py`)
    - Multi-storage backend support (Supabase, S3, MinIO, local)
    - MCP integration with external AI services
    - Analytics and sentiment analysis processing
    - Webhook support and external service connectivity

8. **GDPR Compliance System** (`app/endpoints/gdpr.py`)
    - Complete data export functionality
    - User data deletion with cascade operations
    - Privacy policy and data summary endpoints
    - Audit trails for all data operations

9. **Legal Content Repository** (`indian_laws_data.py`)
    - Centralized repository for Indian legal content
    - BNS and CrPC data management with advanced moderation
    - Content categorization and metadata
    - Easy extensibility for additional legal content

10. **Web Interface & API** (`app/main.py`, `app/endpoints/`)
    - FastAPI-based REST API with 15+ endpoints
    - BNS and CrPC content moderation displays
    - Dynamic approval/rejection reasons with transparency
    - Real-time statistics and analytics dashboard
    - Comprehensive API documentation and testing interface

## Setup Instructions

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configuration**
   - The system uses environment variables for configuration
   - Copy `.env.example` to `.env` if provided
   - Configure logging in `app/logger_middleware.py`

3. **Running the Application**
   ```bash
   # Navigate to project directory
   cd path/to/RL-Content-Moderation

   # Start the FastAPI server
   python app/main.py
   ```

4. **Accessing the API**
   - API documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Main API: http://localhost:8000
   - BNS Moderated Content: http://localhost:8000/bns
   - CrPC Moderated Content: http://localhost:8000/crpc
   - API Overview: http://localhost:8000/api

## Demonstration Flow

### 1. View Moderated Indian Legal Content
- **BNS Content**: Visit http://localhost:8000/bns to see Bharatiya Nyaya Sanhita sections with approval/rejection status
- **CrPC Content**: Visit http://localhost:8000/crpc to see Code of Criminal Procedure sections with detailed reasons
- **API Overview**: Visit http://localhost:8000/api for interactive API documentation

### 2. Basic Content Moderation
```bash
# Example cURL request for text moderation
curl -X POST "http://localhost:8000/api/moderate" \\
     -H "Content-Type: application/json" \\
     -d '{
           "content": "Sample text to moderate",
           "content_type": "text",
           "metadata": {"source": "demo"}
         }'
```

### 3. Feedback Submission
```bash
# Example feedback submission
curl -X POST "http://localhost:8000/api/feedback" \\
     -H "Content-Type: application/json" \\
     -d '{
           "moderation_id": "<ID_FROM_PREVIOUS_RESPONSE>",
           "feedback_type": "thumbs_up",
           "rating": 5
         }'
```

### 4. Transparency Features
- **Approved Content**: Green styling with specific approval reasons based on legal content analysis
- **Rejected Content**: Red styling with detailed rejection reasons
- **Dynamic Reasons**: Content-aware analysis of legal terminology, structure, and procedural elements
- **Score-based Reasoning**: Different explanations based on moderation confidence scores

## Key Technical Highlights

### 1. Reinforcement Learning Implementation
- Custom Q-learning implementation
- Dynamic state-space management
- Adaptive reward processing
- Real-time learning updates

### 2. Scalable Architecture
- Asynchronous processing
- Event-driven design
- Efficient database management
- Modular component structure

### 3. Integration Capabilities
- Extensible API design
- Robust error handling
- Comprehensive logging
- Real-time monitoring

## Performance Metrics

The system tracks several key metrics:
- Moderation accuracy
- Processing latency
- Learning curve
- User satisfaction scores

## Future Enhancements
1. **Enhanced Legal Content Support**
   - Additional Indian legal codes (IPC, CPC, etc.)
   - State-specific law integration
   - Constitutional law sections
   - Case law integration

2. **Advanced AI/ML Features**
   - Enhanced NLP capabilities for legal text analysis
   - Multi-language support for regional languages
   - Advanced ML model integration
   - Legal precedent analysis

3. **System Improvements**
   - Distributed processing support
   - Real-time collaborative moderation
   - Advanced analytics dashboard
   - Mobile application support

4. **Transparency Enhancements**
   - Detailed audit trails
   - User feedback analytics
   - Performance metrics dashboard
   - Automated compliance reporting

## Project Statistics
- Lines of Code: ~8000+
- Core Components: 15+
- API Endpoints: 20+
- Supported Content Types: 5 (text, image, audio, video, code)
- Legal Databases: BNS 2023, CrPC 1973
- Transparency Features: Complete approval/rejection reasoning with dynamic analysis
- Web Routes: 8+ (Dashboard, API Docs, BNS, CrPC, API Overview, Auth, GDPR, Storage)
- Security Features: JWT auth, rate limiting, input sanitization, audit logging
- Monitoring: Sentry error tracking, PostHog analytics, performance metrics
- Compliance: GDPR compliant with data export/deletion, privacy controls

## Testing
```bash
# Run comprehensive test suite
python run_tests.py

# Run specific test categories
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --security      # Security tests only

# Run with coverage report
python run_tests.py --coverage

# Run individual test files
pytest tests/test_moderation_agent.py -v
pytest tests/test_security.py -v

# Run tests with different markers
pytest -m "security"     # Security-related tests
pytest -m "integration"  # Integration tests
pytest -m "performance"  # Performance tests
```

## Monitoring
- Check logs in `logs/app.log`
- Monitor events in `logs/events.jsonl`
- Review moderation history in `logs/moderation.db`

## Troubleshooting
1. Check logs for detailed error messages
2. Verify environment configuration
3. Ensure all dependencies are installed
4. Confirm database connectivity
