from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from .logger_middleware import LoggerMiddleware
from .event_queue import EventQueue
from .feedback_handler import FeedbackHandler

# Import endpoint routers
from .endpoints import moderation, feedback, analytics, file_moderation, health

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RL-Powered Content Moderation API", version="2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Add custom logging middleware
app.add_middleware(LoggerMiddleware)

# Initialize core services
event_queue = EventQueue()
feedback_handler = FeedbackHandler()

# Serve frontend
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("frontend/templates/index.html", "r") as f:
        return f.read()

@app.get("/api", response_class=HTMLResponse)
async def get_api_docs():
    """Serve API documentation with custom styling"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RL Content Moderation API</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                padding: 20px;
            }

            .api-container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }

            .api-header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e1e8ed;
            }

            .api-header h1 {
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }

            .api-header p {
                color: #7f8c8d;
                font-size: 1.1rem;
            }

            .api-section {
                margin-bottom: 40px;
            }

            .api-section h2 {
                color: #2c3e50;
                font-size: 1.8rem;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .endpoint {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }

            .endpoint-method {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 15px;
            }

            .method-GET { background: #28a745; color: white; }
            .method-POST { background: #007bff; color: white; }

            .endpoint-path {
                font-family: 'Courier New', monospace;
                font-size: 1.1rem;
                color: #667eea;
                font-weight: bold;
                text-decoration: none;
                transition: color 0.3s ease;
            }

            .endpoint-path:hover {
                color: #764ba2;
                text-decoration: underline;
            }

            .endpoint-description {
                color: #7f8c8d;
                margin-top: 10px;
                font-size: 0.95rem;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }

            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }

            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .stat-label {
                font-size: 0.9rem;
                opacity: 0.9;
            }

            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                margin: 10px 5px;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }

            .btn-secondary {
                background: #6c757d;
            }

            .btn-secondary:hover {
                background: #5a6268;
                box-shadow: 0 8px 25px rgba(108, 117, 125, 0.3);
            }

            .actions {
                text-align: center;
                margin-top: 30px;
            }

            @media (max-width: 768px) {
                .api-container {
                    padding: 20px;
                }

                .api-header h1 {
                    font-size: 2rem;
                }

                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="api-container">
            <div class="api-header">
                <h1><i class="fas fa-shield-alt"></i> RL Content Moderation API</h1>
                <p>RESTful API for AI-powered content moderation with reinforcement learning</p>
            </div>

            <div class="api-section">
                <h2><i class="fas fa-chart-bar"></i> Statistics</h2>
                <div class="stats-grid" id="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="total-moderated">0</div>
                        <div class="stat-label">Total Moderated</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="flagged-count">0</div>
                        <div class="stat-label">Flagged Content</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="avg-confidence">0%</div>
                        <div class="stat-label">Avg Confidence</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="total-feedback">0</div>
                        <div class="stat-label">Total Feedback</div>
                    </div>
                </div>
            </div>

            <div class="api-section">
                <h2><i class="fas fa-code"></i> API Endpoints</h2>

                <div class="endpoint">
                    <span class="endpoint-method method-GET">GET</span>
                    <a href="/api/stats" class="endpoint-path">/api/stats</a>
                    <div class="endpoint-description">Get moderation statistics and analytics</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-GET">GET</span>
                    <a href="/api/moderated-content" class="endpoint-path">/api/moderated-content</a>
                    <div class="endpoint-description">Get paginated list of moderated content history</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-POST">POST</span>
                    <span class="endpoint-path">/api/moderate</span>
                    <div class="endpoint-description">Submit content for moderation</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-POST">POST</span>
                    <span class="endpoint-path">/api/feedback</span>
                    <div class="endpoint-description">Submit feedback on moderation decisions</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-GET">GET</span>
                    <a href="/api/health" class="endpoint-path">/api/health</a>
                    <div class="endpoint-description">Health check endpoint</div>
                </div>
            </div>

            <div class="actions">
                <a href="/" class="btn"><i class="fas fa-tachometer-alt"></i> View Dashboard</a>
                <a href="/docs" class="btn btn-secondary"><i class="fas fa-file-code"></i> API Docs</a>
            </div>
        </div>

        <script>
            // Load stats dynamically
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    document.getElementById('total-moderated').textContent = stats.total_moderations || 0;
                    document.getElementById('flagged-count').textContent = stats.flagged_count || 0;
                    document.getElementById('avg-confidence').textContent = `${(stats.avg_confidence * 100 || 0).toFixed(1)}%`;
                    document.getElementById('total-feedback').textContent = stats.total_feedback || 0;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            // Load stats on page load
            document.addEventListener('DOMContentLoaded', loadStats);
        </script>
    </body>
    </html>
    """
    return html_content

# Include endpoint routers
app.include_router(health.router, prefix="/api")
app.include_router(moderation.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(file_moderation.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RL-Powered Content Moderation API")
    await event_queue.initialize()
    await feedback_handler.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down services")
    await event_queue.close()
    await feedback_handler.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)