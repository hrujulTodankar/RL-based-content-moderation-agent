# Live Demo Guide: RL-Content Moderation System

## Pre-Demo Setup

1. **Environment Setup** (do this before the demo)
```powershell
# Navigate to project directory
cd "C:\Users\Asus\OneDrive\Desktop\RL-Content-Moderation"

# Activate virtual environment
.\.venv\Scripts\activate

# Verify dependencies
pip list | findstr "fastapi uvicorn pyjwt"
```

2. **Open These in Browser Tabs**
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/health (Health Check)
- http://localhost:8000/learning/report (Learning Metrics)

## Live Demo Steps

### Step 1: Start the Server
```powershell
# Start the FastAPI server
python app/main.py
```
Expected output: You should see uvicorn starting and the server listening on http://0.0.0.0:8000

### Step 2: Basic Content Moderation Demo

1. **Text Moderation Example**
```python
# First, generate a demo token
python scripts/generate_demo_token.py

# Open Python REPL in a new terminal
python

# Copy and paste this code:
import requests
import json

# Store the JWT token (copy from generate_demo_token.py output)
AUTH_TOKEN = "Bearer <paste_token_here>"
# Create headers for authenticated requests
headers = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json"
}

# Moderate text content
response = requests.post(
    "http://localhost:8000/moderate",
    headers=headers,  # Include authentication headers
    json={
        "content": "This is a spam message with suspicious links http://spam.com",
        "content_type": "text",
        "metadata": {"source": "demo"}
    }
)
print(json.dumps(response.json(), indent=2))

# Save the moderation_id for feedback
moderation_id = response.json()["moderation_id"]
```

2. **Show Feedback Processing**
```python
# Submit positive feedback
feedback_response = requests.post(
    "http://localhost:8000/feedback",
    json={
        "moderation_id": moderation_id,
        "feedback_type": "thumbs_up",
        "rating": 5,
        "comment": "Correctly identified spam content"
    }
)
print(json.dumps(feedback_response.json(), indent=2))
```

### Step 3: Demonstrate Learning

1. **Multiple Content Types**
```python
# Test different content types
content_samples = [
    {
        "content": "Check out these amazing deals! Click now!",
        "content_type": "text",
        "metadata": {"context": "email"}
    },
    {
        "content": "Here's a legitimate technical discussion about Python programming",
        "content_type": "text",
        "metadata": {"context": "forum"}
    }
]

# Process each sample
for sample in content_samples:
    response = requests.post(
        "http://localhost:8000/moderate",
        json=sample
    )
    result = response.json()
    print(f"\nContent: {sample['content']}")
    print(f"Flagged: {result['flagged']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasons: {result['reasons']}")
```

### Step 4: Show Analytics

1. **Check Learning Progress**
```python
# Get learning metrics
metrics = requests.get("http://localhost:8000/learning/report")
print(json.dumps(metrics.json(), indent=2))
```

2. **View System Health**
```python
# Check system health
health = requests.get("http://localhost:8000/health")
print(json.dumps(health.json(), indent=2))
```

### Step 5: Integration Demo

1. **Test Integration Services**
```python
# Check integration connectivity
connectivity = requests.get(
    "http://localhost:8000/integration/connectivity",
    headers={"Authorization": "Bearer demo-token"}  # If auth is required
)
print(json.dumps(connectivity.json(), indent=2))
```

## Key Points to Highlight During Demo

1. **Real-time Learning**
   - Show how confidence scores change with feedback
   - Point out the adaptive behavior
   - Show the learning metrics visualization

2. **System Architecture**
   - Highlight async processing (quick response times)
   - Show the event-driven design (check logs)
   - Demonstrate error handling

3. **Integration Features**
   - Show MCP integration
   - Demonstrate NLP context processing
   - Point out the analytics pipeline

## Monitoring During Demo

1. **Check Logs in Real-time**
```powershell
# Open a new terminal
Get-Content -Path "logs/app.log" -Wait
```

2. **Monitor Events**
```powershell
# Open another terminal
Get-Content -Path "logs/events.jsonl" -Wait
```

## Troubleshooting Common Demo Issues

1. **If Server Won't Start**
   - Check if port 8000 is already in use
   - Verify virtual environment is activated
   - Check log files for errors

2. **If Moderation Fails**
   - Verify server is running
   - Check network connectivity
   - Review error messages in logs

3. **If Learning Metrics Don't Update**
   - Verify feedback is being processed
   - Check database connectivity
   - Review event queue logs

## Demo Cleanup

```powershell
# Stop the server (Ctrl+C)
# Deactivate virtual environment
deactivate
```

## Tips for a Smooth Demo

1. Practice the flow beforehand
2. Have example content ready to paste
3. Keep terminal windows organized
4. Have backup examples ready
5. Monitor system resources during demo
6. Keep the API documentation handy

Remember to explain:
- How the RL model learns from feedback
- Why certain content is flagged
- How confidence scores are calculated
- The role of different components
- Real-world applications of the system