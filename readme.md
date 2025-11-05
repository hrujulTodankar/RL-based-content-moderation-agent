# RL-Powered Content Moderation System with Indian Legal Content Transparency

## Project Overview
This project implements an advanced content moderation system powered by Reinforcement Learning (RL) that automatically learns and improves from user feedback. The system specializes in moderating Indian legal content with complete transparency features, showing approved and rejected content with detailed reasoning.

The system can moderate various types of content including text, images, audio, video, and code snippets, with special focus on Indian legal documents like Bharatiya Nyaya Sanhita (BNS) and Code of Criminal Procedure (CrPC).

### Key Features
1. **Indian Legal Content Moderation**
   - Bharatiya Nyaya Sanhita (BNS) 2023 content moderation
   - Code of Criminal Procedure (CrPC) 1973 content moderation
   - Dynamic approval/rejection reasons based on legal content analysis
   - Complete transparency with visual distinction between approved/rejected content

2. **Multi-Modal Content Support**
   - Text moderation with NLP context understanding
   - Image content analysis
   - Audio content processing
   - Video content analysis
   - Code snippet evaluation

3. **Adaptive Learning**
   - Real-time learning from user feedback
   - Confidence-based decision making
   - Historical performance tracking
   - Automated improvement over time

4. **Complete Transparency Features**
   - Approved content (green) with specific approval reasons
   - Rejected content (red) with detailed rejection reasons
   - Content-aware analysis for legal terminology, structure, and procedural elements
   - Score-based dynamic reasoning

5. **Integration Capabilities**
   - Model Context Protocol (MCP) integration
   - Event-driven architecture
   - Scalable feedback handling
   - Real-time analytics

## Technical Architecture

### Core Components
1. **Moderation Agent** (`moderation_agent.py`)
   - Implements RL-based decision making
   - Manages state and action spaces
   - Handles reward processing
   - Maintains moderation history

2. **Feedback Handler** (`feedback_handler.py`)
   - Processes user feedback
   - Normalizes feedback scores
   - Maintains feedback database
   - Generates performance metrics

3. **Event Queue** (`event_queue.py`)
   - Manages asynchronous events
   - Handles background tasks
   - Provides event logging
   - Ensures system responsiveness

4. **Integration Services** (`integration_services.py`)
   - Connects with external services
   - Handles NLP processing
   - Manages MCP integration
   - Processes analytics data

5. **Legal Content Repository** (`indian_laws_data.py`)
   - Centralized repository for Indian legal content
   - BNS and CrPC data management
   - Content categorization and metadata
   - Easy extensibility for additional legal content

6. **Web Interface** (`app/main.py`)
   - BNS content moderation display (`/bns`)
   - CrPC content moderation display (`/crpc`)
   - Dynamic approval/rejection reasons
   - Visual distinction with color coding
   - Real-time statistics and analytics

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
- Lines of Code: ~4000+
- Core Components: 10
- API Endpoints: 12+
- Supported Content Types: 5
- Legal Databases: BNS 2023, CrPC 1973
- Transparency Features: Complete approval/rejection reasoning
- Web Routes: 5 (Dashboard, API Docs, BNS, CrPC, API Overview)

## Testing
```bash
# Run the test suite
pytest testing_files/
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
