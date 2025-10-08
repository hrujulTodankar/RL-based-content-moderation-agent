# RL-Powered Content Moderation System

## Project Overview
This project implements an advanced content moderation system powered by Reinforcement Learning (RL) that automatically learns and improves from user feedback. The system can moderate various types of content including text, images, audio, video, and code snippets.

### Key Features
1. **Multi-Modal Content Support**
   - Text moderation with NLP context understanding
   - Image content analysis
   - Audio content processing
   - Video content analysis
   - Code snippet evaluation

2. **Adaptive Learning**
   - Real-time learning from user feedback
   - Confidence-based decision making
   - Historical performance tracking
   - Automated improvement over time

3. **Integration Capabilities**
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

## Demonstration Flow

### 1. Basic Content Moderation
```bash
# Example cURL request for text moderation
curl -X POST "http://localhost:8000/moderate" \\
     -H "Content-Type: application/json" \\
     -d '{
           "content": "Sample text to moderate",
           "content_type": "text",
           "metadata": {"source": "demo"}
         }'
```

### 2. Feedback Submission
```bash
# Example feedback submission
curl -X POST "http://localhost:8000/feedback" \\
     -H "Content-Type: application/json" \\
     -d '{
           "moderation_id": "<ID_FROM_PREVIOUS_RESPONSE>",
           "feedback_type": "thumbs_up",
           "rating": 5
         }'
```

### 3. Learning Visualization
- Access http://localhost:8000/learning/report to view learning progress
- Check moderation accuracy trends
- View confidence scores over time

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
1. Enhanced NLP capabilities
2. Multi-language support
3. Advanced ML model integration
4. Distributed processing support

## Project Statistics
- Lines of Code: ~2000
- Core Components: 8
- API Endpoints: 10+
- Supported Content Types: 5

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
