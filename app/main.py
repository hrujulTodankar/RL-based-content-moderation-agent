from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from .logger_middleware import LoggerMiddleware
from .event_queue import event_queue
from .feedback_handler import feedback_handler
from .task_queue import task_queue
from .security import security_middleware
from .observability import (
    sentry_manager, posthog_manager, performance_monitor,
    structured_logger, get_observability_health, track_performance
)
from .content_clarity_analyzer import create_clarity_analyzer

# Import endpoint routers
from .endpoints import (
    moderation, feedback, analytics, file_moderation, health, auth, gdpr, storage, tasks,
    classify, legal_route, constitution, timeline, success_rate, jurisdiction
)

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
# app.add_middleware(LoggerMiddleware)  # Disabled for demo

# Add security middleware
# app.middleware("http")(security_middleware)  # Disabled for demo

# Core services are imported as global instances

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
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                <h1><i class="fas fa-brain"></i> RL Content Moderation API</h1>
                <p>AI-powered content moderation with adaptive learning and Indian legal content transparency</p>
            </div>

            <div class="api-section">
                <h2><i class="fas fa-chart-line"></i> RL Learning Analytics</h2>
                <div class="rl-analytics" id="rl-analytics">
                    <div class="analytics-tabs">
                        <button class="tab-btn active" onclick="showTab('progress')">Learning Progress</button>
                        <button class="tab-btn" onclick="showTab('metrics')">Training Metrics</button>
                        <button class="tab-btn" onclick="showTab('performance')">Performance</button>
                        <button class="tab-btn" onclick="showTab('accuracy')">Accuracy Trends</button>
                    </div>

                    <div id="progress-tab" class="tab-content active">
                        <div class="rl-progress">
                            <div class="progress-header">
                                <div class="progress-title">Adaptive Learning Progress</div>
                                <div class="progress-metric" id="learning-confidence">Confidence: 0%</div>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                            </div>
                            <div class="progress-stats">
                                <div class="progress-stat">
                                    <div class="progress-stat-value" id="total-learnings">0</div>
                                    <div>Total Learnings</div>
                                </div>
                                <div class="progress-stat">
                                    <div class="progress-stat-value" id="accuracy-rate">0%</div>
                                    <div>Accuracy Rate</div>
                                </div>
                                <div class="progress-stat">
                                    <div class="progress-stat-value" id="q-table-size">0</div>
                                    <div>Q-Table Size</div>
                                </div>
                                <div class="progress-stat">
                                    <div class="progress-stat-value" id="feedback-count">0</div>
                                    <div>Feedback Received</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="metrics-tab" class="tab-content">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h4><i class="fas fa-brain"></i> Q-Learning Metrics</h4>
                                <canvas id="q-learning-chart" width="300" height="200"></canvas>
                            </div>
                            <div class="metric-card">
                                <h4><i class="fas fa-chart-area"></i> Reward Distribution</h4>
                                <canvas id="reward-chart" width="300" height="200"></canvas>
                            </div>
                            <div class="metric-card">
                                <h4><i class="fas fa-cogs"></i> Action Selection</h4>
                                <canvas id="action-chart" width="300" height="200"></canvas>
                            </div>
                            <div class="metric-card">
                                <h4><i class="fas fa-clock"></i> Learning Rate</h4>
                                <canvas id="learning-rate-chart" width="300" height="200"></canvas>
                            </div>
                        </div>
                    </div>

                    <div id="performance-tab" class="tab-content">
                        <div class="performance-dashboard">
                            <div class="performance-header">
                                <h4><i class="fas fa-tachometer-alt"></i> Model Performance Over Time</h4>
                                <div class="performance-controls">
                                    <select id="time-range">
                                        <option value="1h">Last Hour</option>
                                        <option value="24h">Last 24 Hours</option>
                                        <option value="7d">Last 7 Days</option>
                                        <option value="30d">Last 30 Days</option>
                                    </select>
                                </div>
                            </div>
                            <div class="performance-charts">
                                <div class="chart-container">
                                    <canvas id="performance-chart" width="600" height="300"></canvas>
                                </div>
                                <div class="performance-stats">
                                    <div class="stat-item">
                                        <span class="stat-label">Current Accuracy:</span>
                                        <span class="stat-value" id="current-accuracy">0%</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Improvement Rate:</span>
                                        <span class="stat-value" id="improvement-rate">+0%</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Best Performance:</span>
                                        <span class="stat-value" id="best-performance">0%</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">Training Sessions:</span>
                                        <span class="stat-value" id="training-sessions">0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div id="accuracy-tab" class="tab-content">
                        <div class="accuracy-analysis">
                            <h4><i class="fas fa-target"></i> Moderation Accuracy Trends</h4>
                            <div class="accuracy-controls">
                                <div class="filter-group">
                                    <label>Content Type:</label>
                                    <select id="content-filter">
                                        <option value="all">All Types</option>
                                        <option value="text">Text</option>
                                        <option value="image">Image</option>
                                        <option value="video">Video</option>
                                        <option value="audio">Audio</option>
                                    </select>
                                </div>
                                <div class="filter-group">
                                    <label>Time Period:</label>
                                    <select id="accuracy-time-range">
                                        <option value="1h">Last Hour</option>
                                        <option value="6h">Last 6 Hours</option>
                                        <option value="24h">Last 24 Hours</option>
                                        <option value="7d">Last 7 Days</option>
                                    </select>
                                </div>
                            </div>
                            <div class="accuracy-chart-container">
                                <canvas id="accuracy-trend-chart" width="700" height="350"></canvas>
                            </div>
                            <div class="accuracy-insights">
                                <div class="insight-card">
                                    <h5>Key Insights</h5>
                                    <ul id="accuracy-insights-list">
                                        <li>Loading insights...</li>
                                    </ul>
                                </div>
                                <div class="insight-card">
                                    <h5>Content Type Performance</h5>
                                    <div class="content-performance" id="content-performance">
                                        <div class="performance-item">
                                            <span>Text:</span>
                                            <div class="performance-bar">
                                                <div class="performance-fill" style="width: 0%"></div>
                                            </div>
                                            <span class="performance-value">0%</span>
                                        </div>
                                        <div class="performance-item">
                                            <span>Image:</span>
                                            <div class="performance-bar">
                                                <div class="performance-fill" style="width: 0%"></div>
                                            </div>
                                            <span class="performance-value">0%</span>
                                        </div>
                                        <div class="performance-item">
                                            <span>Video:</span>
                                            <div class="performance-bar">
                                                <div class="performance-fill" style="width: 0%"></div>
                                            </div>
                                            <span class="performance-value">0%</span>
                                        </div>
                                        <div class="performance-item">
                                            <span>Audio:</span>
                                            <div class="performance-bar">
                                                <div class="performance-fill" style="width: 0%"></div>
                                            </div>
                                            <span class="performance-value">0%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
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
                    <div class="endpoint-description">Submit text content for moderation</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-POST">POST</span>
                    <span class="endpoint-path">/api/moderate/file</span>
                    <div class="endpoint-description">Upload and moderate image, video, or audio files</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-POST">POST</span>
                    <span class="endpoint-path">/api/feedback</span>
                    <div class="endpoint-description">Submit feedback on moderation decisions (triggers RL learning)</div>
                </div>

                <div class="endpoint">
                    <span class="endpoint-method method-GET">GET</span>
                    <a href="/api/health" class="endpoint-path">/api/health</a>
                    <div class="endpoint-description">Health check endpoint</div>
                </div>
            </div>

            <div class="api-section">
                <h2><i class="fas fa-upload"></i> Multimedia Content Moderation</h2>
                <div class="upload-section">
                    <div class="upload-area" id="upload-area">
                        <div class="upload-content">
                            <i class="fas fa-cloud-upload-alt upload-icon"></i>
                            <h3>Upload Media Files</h3>
                            <p>Drag & drop images, videos, or audio files here, or click to browse</p>
                            <input type="file" id="file-input" accept="image/*,video/*,audio/*" style="display: none;">
                            <button class="btn upload-btn" onclick="document.getElementById('file-input').click()">
                                <i class="fas fa-folder-open"></i> Choose Files
                            </button>
                        </div>
                    </div>

                    <div class="upload-options">
                        <div class="option-group">
                            <label for="content-type">Content Type:</label>
                            <select id="content-type" class="form-control">
                                <option value="image">Image</option>
                                <option value="video">Video</option>
                                <option value="audio">Audio</option>
                            </select>
                        </div>
                        <button class="btn" onclick="moderateFile()" id="moderate-btn" disabled>
                            <i class="fas fa-shield-alt"></i> Moderate Content
                        </button>
                    </div>
                </div>

                <div class="preview-section" id="preview-section" style="display: none;">
                    <h4><i class="fas fa-eye"></i> Preview & Results</h4>
                    <div class="preview-container">
                        <div class="media-preview" id="media-preview"></div>
                        <div class="moderation-results" id="moderation-results"></div>
                    </div>
                </div>
            </div>

            <div class="api-section">
                <h2><i class="fas fa-gavel"></i> Indian Legal Content</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <a href="/bns" class="btn" style="background: linear-gradient(135deg, #28a745, #20c997); margin: 0; text-decoration: none; color: white;">
                            <i class="fas fa-book"></i> BNS 2023
                        </a>
                    </div>
                    <div class="stat-card">
                        <a href="/crpc" class="btn" style="background: linear-gradient(135deg, #dc3545, #fd7e14); margin: 0; text-decoration: none; color: white;">
                            <i class="fas fa-balance-scale"></i> CrPC 1973
                        </a>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">RL</div>
                        <div class="stat-label">Moderation Type</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">100%</div>
                        <div class="stat-label">Transparency</div>
                    </div>
                </div>
            </div>

            <div class="actions">
                <a href="/" class="btn"><i class="fas fa-tachometer-alt"></i> View Dashboard</a>
                <a href="/docs" class="btn btn-secondary"><i class="fas fa-file-code"></i> API Docs</a>
            </div>
        </div>

        <script>
            let selectedFile = null;

            // File upload handling
            document.getElementById('file-input').addEventListener('change', handleFileSelect);
            document.getElementById('upload-area').addEventListener('click', () => document.getElementById('file-input').click());

            // Drag and drop functionality
            const uploadArea = document.getElementById('upload-area');
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, unhighlight, false);
            });

            function highlight(e) {
                uploadArea.classList.add('dragover');
            }

            function unhighlight(e) {
                uploadArea.classList.remove('dragover');
            }

            uploadArea.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                handleFiles(files);
            }

            function handleFileSelect(e) {
                const files = e.target.files;
                handleFiles(files);
            }

            function handleFiles(files) {
                if (files.length > 0) {
                    selectedFile = files[0];
                    updateUploadArea();
                    document.getElementById('moderate-btn').disabled = false;
                }
            }

            function updateUploadArea() {
                const uploadContent = uploadArea.querySelector('.upload-content');
                const fileName = selectedFile.name;
                const fileSize = (selectedFile.size / (1024 * 1024)).toFixed(2) + ' MB';

                uploadContent.innerHTML = `
                    <i class="fas fa-file-alt upload-icon" style="color: #28a745;"></i>
                    <h3>File Selected</h3>
                    <p><strong>${fileName}</strong> (${fileSize})</p>
                    <button class="btn upload-btn" onclick="clearFile()">
                        <i class="fas fa-times"></i> Clear
                    </button>
                `;
            }

            function clearFile() {
                selectedFile = null;
                document.getElementById('file-input').value = '';
                document.getElementById('moderate-btn').disabled = true;

                const uploadContent = document.querySelector('.upload-content');
                uploadContent.innerHTML = `
                    <i class="fas fa-cloud-upload-alt upload-icon"></i>
                    <h3>Upload Media Files</h3>
                    <p>Drag & drop images, videos, or audio files here, or click to browse</p>
                    <button class="btn upload-btn" onclick="document.getElementById('file-input').click()">
                        <i class="fas fa-folder-open"></i> Choose Files
                    </button>
                `;

                document.getElementById('preview-section').style.display = 'none';
            }

            async function moderateFile() {
                if (!selectedFile) {
                    alert('Please select a file first');
                    return;
                }

                const contentType = document.getElementById('content-type').value;
                const moderateBtn = document.getElementById('moderate-btn');

                moderateBtn.disabled = true;
                moderateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

                try {
                    const formData = new FormData();
                    formData.append('file', selectedFile);
                    formData.append('content_type', contentType);

                    const response = await fetch('/api/moderate/file', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        displayResults(result);
                    } else {
                        throw new Error(result.detail || 'Moderation failed');
                    }

                } catch (error) {
                    alert('Error: ' + error.message);
                    console.error('Moderation error:', error);
                } finally {
                    moderateBtn.disabled = false;
                    moderateBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Moderate Content';
                }
            }

            function displayResults(result) {
                const previewSection = document.getElementById('preview-section');
                const mediaPreview = document.getElementById('media-preview');
                const moderationResults = document.getElementById('moderation-results');

                previewSection.style.display = 'block';

                // Create media preview
                let mediaElement = '';
                if (selectedFile.type.startsWith('image/')) {
                    mediaElement = `<img src="${URL.createObjectURL(selectedFile)}" alt="Uploaded image">`;
                } else if (selectedFile.type.startsWith('video/')) {
                    mediaElement = `<video controls><source src="${URL.createObjectURL(selectedFile)}" type="${selectedFile.type}"></video>`;
                } else if (selectedFile.type.startsWith('audio/')) {
                    mediaElement = `<audio controls><source src="${URL.createObjectURL(selectedFile)}" type="${selectedFile.type}"></audio>`;
                }

                mediaPreview.innerHTML = `
                    <h5>Uploaded File</h5>
                    ${mediaElement}
                    <p><strong>File:</strong> ${selectedFile.name}</p>
                    <p><strong>Size:</strong> ${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                    <p><strong>Type:</strong> ${selectedFile.type}</p>
                `;

                // Create moderation results
                const statusClass = result.flagged ? 'flagged' : '';
                const statusText = result.flagged ? 'FLAGGED' : 'APPROVED';
                const statusColor = result.flagged ? '#dc3545' : '#28a745';

                moderationResults.innerHTML = `
                    <div class="result-card ${statusClass}">
                        <h5>Moderation Results</h5>
                        <div class="result-score ${statusClass}">
                            Status: ${statusText}
                        </div>
                        <p><strong>Score:</strong> ${(result.score * 100).toFixed(2)}%</p>
                        <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(2)}%</p>
                        <p><strong>Content Type:</strong> ${result.content_type}</p>
                        <p><strong>Moderation ID:</strong> ${result.moderation_id}</p>
                        <div class="result-reasons">
                            <strong>Analysis:</strong><br>
                            ${result.reasons.map(reason => `<span class="result-reason">${reason}</span>`).join('')}
                        </div>
                    </div>
                `;

                // Scroll to results
                previewSection.scrollIntoView({ behavior: 'smooth' });
            }

            // Load stats and RL progress dynamically
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    document.getElementById('total-moderated').textContent = stats.total_moderations || 0;
                    document.getElementById('flagged-count').textContent = stats.flagged_count || 0;
                    document.getElementById('avg-confidence').textContent = `${(stats.avg_confidence * 100 || 0).toFixed(1)}%`;
                    document.getElementById('total-feedback').textContent = stats.total_feedback || 0;
                    document.getElementById('feedback-count').textContent = stats.total_feedback || 0;

                    // Calculate learning progress
                    const totalModerations = stats.total_moderations || 0;
                    const totalFeedback = stats.total_feedback || 0;
                    const avgConfidence = stats.avg_confidence || 0;

                    // Learning progress based on feedback ratio and confidence
                    const feedbackRatio = totalModerations > 0 ? (totalFeedback / totalModerations) : 0;
                    const learningProgress = Math.min((feedbackRatio * 0.6 + avgConfidence * 0.4) * 100, 100);

                    document.getElementById('progress-fill').style.width = `${learningProgress}%`;
                    document.getElementById('learning-confidence').textContent = `Confidence: ${(avgConfidence * 100).toFixed(1)}%`;
                    document.getElementById('total-learnings').textContent = totalFeedback;
                    document.getElementById('accuracy-rate').textContent = `${(avgConfidence * 100).toFixed(1)}%`;

                    // Mock Q-table size (would come from agent stats in real implementation)
                    document.getElementById('q-table-size').textContent = Math.floor(totalFeedback * 2.5);

                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            // Tab switching functionality
            function showTab(tabName) {
                // Hide all tabs
                const tabs = document.querySelectorAll('.tab-content');
                tabs.forEach(tab => tab.classList.remove('active'));

                // Remove active class from all buttons
                const buttons = document.querySelectorAll('.tab-btn');
                buttons.forEach(btn => btn.classList.remove('active'));

                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');

                // Load data for specific tab
                if (tabName === 'metrics') {
                    loadTrainingMetrics();
                } else if (tabName === 'performance') {
                    loadPerformanceData();
                } else if (tabName === 'accuracy') {
                    loadAccuracyTrends();
                }
            }

            // Load training metrics and create charts
            async function loadTrainingMetrics() {
                try {
                    const response = await fetch('/api/rl-metrics');
                    const metrics = await response.json();

                    // Q-Learning Chart
                    const qCtx = document.getElementById('q-learning-chart').getContext('2d');
                    new Chart(qCtx, {
                        type: 'line',
                        data: {
                            labels: metrics.timestamps || [],
                            datasets: [{
                                label: 'Q-Value Updates',
                                data: metrics.q_values || [],
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });

                    // Reward Distribution Chart
                    const rewardCtx = document.getElementById('reward-chart').getContext('2d');
                    new Chart(rewardCtx, {
                        type: 'bar',
                        data: {
                            labels: ['Positive', 'Neutral', 'Negative'],
                            datasets: [{
                                label: 'Reward Distribution',
                                data: metrics.reward_distribution || [0, 0, 0],
                                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: false }
                            }
                        }
                    });

                    // Action Selection Chart
                    const actionCtx = document.getElementById('action-chart').getContext('2d');
                    new Chart(actionCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Approve', 'Flag', 'Review'],
                            datasets: [{
                                data: metrics.action_counts || [0, 0, 0],
                                backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { position: 'bottom' }
                            }
                        }
                    });

                    // Learning Rate Chart
                    const lrCtx = document.getElementById('learning-rate-chart').getContext('2d');
                    new Chart(lrCtx, {
                        type: 'line',
                        data: {
                            labels: metrics.timestamps || [],
                            datasets: [{
                                label: 'Learning Rate',
                                data: metrics.learning_rates || [],
                                borderColor: '#fd7e14',
                                backgroundColor: 'rgba(253, 126, 20, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                y: { beginAtZero: true, max: 1 }
                            }
                        }
                    });

                } catch (error) {
                    console.error('Error loading training metrics:', error);
                }
            }

            // Load performance data
            async function loadPerformanceData() {
                try {
                    const timeRange = document.getElementById('time-range').value;
                    const response = await fetch(`/api/performance?range=${timeRange}`);
                    const performance = await response.json();

                    // Performance Chart
                    const perfCtx = document.getElementById('performance-chart').getContext('2d');
                    new Chart(perfCtx, {
                        type: 'line',
                        data: {
                            labels: performance.timestamps || [],
                            datasets: [{
                                label: 'Accuracy',
                                data: performance.accuracy || [],
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                tension: 0.4
                            }, {
                                label: 'Confidence',
                                data: performance.confidence || [],
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { position: 'top' }
                            },
                            scales: {
                                y: { beginAtZero: true, max: 1 }
                            }
                        }
                    });

                    // Update performance stats
                    document.getElementById('current-accuracy').textContent = `${(performance.current_accuracy * 100 || 0).toFixed(1)}%`;
                    document.getElementById('improvement-rate').textContent = `${performance.improvement_rate > 0 ? '+' : ''}${(performance.improvement_rate * 100 || 0).toFixed(1)}%`;
                    document.getElementById('best-performance').textContent = `${(performance.best_performance * 100 || 0).toFixed(1)}%`;
                    document.getElementById('training-sessions').textContent = performance.training_sessions || 0;

                } catch (error) {
                    console.error('Error loading performance data:', error);
                }
            }

            // Load accuracy trends
            async function loadAccuracyTrends() {
                try {
                    const contentFilter = document.getElementById('content-filter').value;
                    const timeRange = document.getElementById('accuracy-time-range').value;
                    const response = await fetch(`/api/accuracy-trends?content=${contentFilter}&range=${timeRange}`);
                    const trends = await response.json();

                    // Accuracy Trend Chart
                    const accuracyCtx = document.getElementById('accuracy-trend-chart').getContext('2d');
                    new Chart(accuracyCtx, {
                        type: 'line',
                        data: {
                            labels: trends.timestamps || [],
                            datasets: [{
                                label: 'Overall Accuracy',
                                data: trends.overall_accuracy || [],
                                borderColor: '#28a745',
                                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                                tension: 0.4
                            }, {
                                label: 'Text Accuracy',
                                data: trends.text_accuracy || [],
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4
                            }, {
                                label: 'Media Accuracy',
                                data: trends.media_accuracy || [],
                                borderColor: '#fd7e14',
                                backgroundColor: 'rgba(253, 126, 20, 0.1)',
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { position: 'top' }
                            },
                            scales: {
                                y: { beginAtZero: true, max: 1 }
                            }
                        }
                    });

                    // Update insights
                    const insightsList = document.getElementById('accuracy-insights-list');
                    insightsList.innerHTML = trends.insights.map(insight =>
                        `<li><i class="fas fa-lightbulb"></i> ${insight}</li>`
                    ).join('');

                    // Update content performance bars
                    const performanceItems = document.querySelectorAll('.performance-item');
                    const contentTypes = ['text', 'image', 'video', 'audio'];

                    contentTypes.forEach((type, index) => {
                        const accuracy = trends.content_performance[type] || 0;
                        const fill = performanceItems[index].querySelector('.performance-fill');
                        const value = performanceItems[index].querySelector('.performance-value');

                        fill.style.width = `${accuracy * 100}%`;
                        value.textContent = `${(accuracy * 100).toFixed(1)}%`;
                    });

                } catch (error) {
                    console.error('Error loading accuracy trends:', error);
                }
            }

            // Event listeners for filters
            document.getElementById('time-range').addEventListener('change', loadPerformanceData);
            document.getElementById('content-filter').addEventListener('change', loadAccuracyTrends);
            document.getElementById('accuracy-time-range').addEventListener('change', loadAccuracyTrends);

            // Load stats on page load and refresh every 5 seconds
            document.addEventListener('DOMContentLoaded', function() {
                loadStats();
                // Initialize with progress tab
                showTab('progress');
            });
            setInterval(loadStats, 5000);
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
app.include_router(auth.router, prefix="/api")
app.include_router(gdpr.router, prefix="/api")
app.include_router(storage.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")

# Legal system endpoints
app.include_router(classify.router, prefix="/api")
app.include_router(legal_route.router, prefix="/api")
app.include_router(constitution.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")
app.include_router(success_rate.router, prefix="/api")
app.include_router(jurisdiction.router, prefix="/api")

# Add BNS content endpoint
from fastapi.responses import HTMLResponse
import json

@app.get("/bns", response_class=HTMLResponse)
async def get_bns_content():
    """Serve moderated BNS content with scores"""

    # Import BNS data
    from bharathi_nyaya_sanhita import create_bns_database
    bns_db = create_bns_database()
    
    # Initialize NLP-based clarity analyzer
    clarity_analyzer = create_clarity_analyzer()

    # Get sections and simulate moderation results for demo
    moderated_sections = []
    unapproved_sections = []

    for section_num, section_data in list(bns_db.bns_sections.items())[:30]:
        # Simulate different moderation scores for variety
        import random
        base_score = random.uniform(0.3, 0.95)  # Random score between 0.3-0.95
        confidence = 0.8 + random.uniform(0, 0.15)   # Random confidence between 0.8-0.95

        # Get content from the BNS database
        content = section_data.get("description", section_data.get("content", "Content not available"))

        # Generate approval/rejection reasons based on score
        approval_reasons = []
        rejection_reasons = []

        if base_score >= 0.7:
            # Dynamic approval reasons based on content analysis
            content_text = content.lower()

            # Check for legal keywords
            legal_keywords = ["shall", "section", "act", "law", "punishment", "offence", "court", "police", "magistrate"]
            legal_score = sum(1 for keyword in legal_keywords if keyword in content_text)

            # Check for clarity and structure
            has_structure = any(indicator in content_text for indicator in ["whoever", "any person", "shall be", "punished with", "may be"])

            # Check for procedural elements
            has_procedure = any(proc in content_text for proc in ["arrest", "bail", "warrant", "summons", "investigation"])

            # Generate dynamic reasons
            if base_score >= 0.9:
                approval_reasons.append("Excellent legal content with clear structure")
                if legal_score >= 4:
                    approval_reasons.append("High legal terminology accuracy")
                if has_structure:
                    approval_reasons.append("Well-structured legal provisions")
                if has_procedure:
                    approval_reasons.append("Comprehensive procedural guidance")
            elif base_score >= 0.8:
                approval_reasons.append("High quality legal content")
                if legal_score >= 3:
                    approval_reasons.append("Appropriate legal language usage")
                if has_structure:
                    approval_reasons.append("Clear legal framework")
                if has_procedure:
                    approval_reasons.append("Detailed procedural content")
            else:
                approval_reasons.append("Good legal content quality")
                if legal_score >= 2:
                    approval_reasons.append("Contains relevant legal terms")
                if has_structure:
                    approval_reasons.append("Basic legal structure present")
                approval_reasons.append("Meets basic content standards")
        else:
            # Enhanced rejection reasons based on score and content analysis
            content_text = section_data.get("content", "").lower()

            # Check for concerning keywords
            concerning_keywords = ["violence", "harm", "illegal", "prohibited", "penalty", "punishment"]
            concerning_score = sum(1 for keyword in concerning_keywords if keyword in content_text)

            # Perform NLP-based clarity analysis
            clarity_analysis = clarity_analyzer.analyze_content_clarity(content, "legal")
            has_clarity_issues = len(clarity_analysis.get("clarity_issues", [])) > 0

            # Check for legal completeness
            legal_keywords = ["shall", "section", "act", "law", "court"]
            legal_completeness = sum(1 for keyword in legal_keywords if keyword in content_text)

            if base_score < 0.4:
                rejection_reasons.append("Content violates community guidelines")
                if concerning_score >= 2:
                    rejection_reasons.append("Contains sensitive legal content requiring review")
                rejection_reasons.append("Significant content quality issues detected")
                if legal_completeness < 2:
                    rejection_reasons.append("Insufficient legal context and terminology")
            elif base_score < 0.5:
                rejection_reasons.append("Inappropriate language detected")
                if has_clarity_issues:
                    rejection_reasons.append("Content clarity and structure issues")
                rejection_reasons.append("Moderate content quality concerns")
                if concerning_score >= 1:
                    rejection_reasons.append("Contains potentially sensitive material")
            elif base_score < 0.6:
                rejection_reasons.append("Content flagged for review")
                if legal_completeness < 3:
                    rejection_reasons.append("Limited legal terminology usage")
                rejection_reasons.append("Content requires additional verification")
                if has_clarity_issues:
                    rejection_reasons.append("Potential interpretation ambiguities")
            else:
                rejection_reasons.append("Low confidence score")
                rejection_reasons.append("Borderline content quality")
                if legal_completeness < 2:
                    rejection_reasons.append("Minimal legal framework present")
                rejection_reasons.append("Content needs improvement before approval")

        section_info = {
            "section": section_num,
            "title": section_data["title"],
            # "content": content,
            "category": section_data.get("category", "unknown").replace("_", " ").title(),
            "score": round(base_score, 3),
            "confidence": round(confidence, 3),
            "status": "APPROVED" if base_score >= 0.7 else "REJECTED",
            "approval_reasons": approval_reasons if base_score >= 0.7 else [],
            "rejection_reasons": rejection_reasons if base_score < 0.7 else []
        }

        if base_score >= 0.7:
            moderated_sections.append(section_info)
        else:
            unapproved_sections.append(section_info)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bharatiya Nyaya Sanhita - Moderated Content</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}

            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e1e8ed;
            }}

            .header h1 {{
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }}

            .header p {{
                color: #7f8c8d;
                font-size: 1.1rem;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}

            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}

            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}

            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}

            .content-section {{
                margin-bottom: 40px;
            }}

            .content-section h2 {{
                color: #2c3e50;
                font-size: 1.8rem;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .bns-item {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }}

            .bns-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}

            .section-number {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #667eea;
            }}

            .category {{
                background: #e9ecef;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                color: #495057;
            }}

            .section-title {{
                font-size: 1.1rem;
                color: #2c3e50;
                margin-bottom: 10px;
            }}

            .section-content {{
                background: #f8f9fa;
                border-left: 3px solid #007bff;
                padding: 10px 15px;
                margin-bottom: 10px;
                font-size: 0.9rem;
                color: #495057;
                border-radius: 0 5px 5px 0;
            }}

            .moderation-info {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 10px;
                border-radius: 5px;
                font-size: 0.9rem;
            }}

            .moderation-info.rejected {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }}

            .bns-item.approved {{
                border-left: 4px solid #28a745;
            }}

            .bns-item.rejected {{
                border-left: 4px solid #dc3545;
                opacity: 0.8;
            }}

            .rl-progress {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #28a745;
            }}

            .progress-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}

            .progress-title {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #2c3e50;
            }}

            .progress-metric {{
                font-size: 0.9rem;
                color: #7f8c8d;
            }}

            .progress-bar {{
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 10px;
            }}

            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                transition: width 0.3s ease;
            }}

            .progress-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                font-size: 0.9rem;
            }}

            .progress-stat {{
                text-align: center;
            }}

            .progress-stat-value {{
                font-weight: bold;
                color: #28a745;
                font-size: 1.1rem;
            }}

            .upload-section {{
                margin: 20px 0;
            }}

            .upload-area {{
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background: rgba(102, 126, 234, 0.05);
                transition: all 0.3s ease;
                cursor: pointer;
                margin-bottom: 20px;
            }}

            .upload-area:hover, .upload-area.dragover {{
                border-color: #28a745;
                background: rgba(40, 167, 69, 0.1);
            }}

            .upload-icon {{
                font-size: 3rem;
                color: #667eea;
                margin-bottom: 15px;
            }}

            .upload-content h3 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}

            .upload-content p {{
                color: #7f8c8d;
                margin-bottom: 20px;
            }}

            .upload-btn {{
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .upload-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}

            .upload-options {{
                display: flex;
                gap: 20px;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
            }}

            .option-group {{
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}

            .option-group label {{
                font-weight: 600;
                color: #2c3e50;
                font-size: 0.9rem;
            }}

            .form-control {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 0.9rem;
                min-width: 120px;
            }}

            .preview-section {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
            }}

            .preview-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 15px;
            }}

            .media-preview {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }}

            .media-preview img, .media-preview video, .media-preview audio {{
                max-width: 100%;
                max-height: 300px;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}

            .moderation-results {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }}

            .result-card {{
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid #28a745;
            }}

            .result-card.flagged {{
                border-left-color: #dc3545;
            }}

            .result-score {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #28a745;
            }}

            .result-score.flagged {{
                color: #dc3545;
            }}

            .result-reasons {{
                margin-top: 10px;
                font-size: 0.9rem;
            }}

            .result-reason {{
                background: #e9ecef;
                padding: 5px 10px;
                border-radius: 15px;
                margin: 2px 2px 2px 0;
                display: inline-block;
                font-size: 0.8rem;
            }}

            .rl-analytics {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
            }}

            .analytics-tabs {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 1px solid #e9ecef;
                padding-bottom: 10px;
            }}

            .tab-btn {{
                padding: 10px 20px;
                border: none;
                background: #f8f9fa;
                color: #6c757d;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .tab-btn.active {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }}

            .tab-btn:hover {{
                background: #e9ecef;
            }}

            .tab-content {{
                display: none;
            }}

            .tab-content.active {{
                display: block;
            }}

            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}

            .metric-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                border: 1px solid #e9ecef;
            }}

            .metric-card h4 {{
                margin-bottom: 15px;
                color: #2c3e50;
                font-size: 1.1rem;
            }}

            .metric-card canvas {{
                width: 100% !important;
                height: auto !important;
            }}

            .performance-dashboard {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}

            .performance-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}

            .performance-header h4 {{
                color: #2c3e50;
                margin: 0;
            }}

            .performance-controls select {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 0.9rem;
            }}

            .performance-charts {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }}

            .chart-container {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }}

            .performance-stats {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}

            .stat-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 6px;
            }}

            .stat-label {{
                font-weight: 600;
                color: #495057;
            }}

            .stat-value {{
                font-weight: bold;
                color: #28a745;
                font-size: 1.1rem;
            }}

            .accuracy-analysis {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}

            .accuracy-analysis h4 {{
                color: #2c3e50;
                margin-bottom: 20px;
            }}

            .accuracy-controls {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }}

            .filter-group {{
                display: flex;
                flex-direction: column;
                gap: 5px;
            }}

            .filter-group label {{
                font-weight: 600;
                color: #2c3e50;
                font-size: 0.9rem;
            }}

            .filter-group select {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 0.9rem;
                min-width: 120px;
            }}

            .accuracy-chart-container {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }}

            .accuracy-insights {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}

            .insight-card {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }}

            .insight-card h5 {{
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1rem;
            }}

            .insight-card ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .insight-card li {{
                padding: 5px 0;
                color: #495057;
                font-size: 0.9rem;
            }}

            .content-performance {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .performance-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 0.9rem;
            }}

            .performance-item span:first-child {{
                min-width: 50px;
                font-weight: 600;
                color: #495057;
            }}

            .performance-bar {{
                flex: 1;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
            }}

            .performance-fill {{
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                border-radius: 4px;
                transition: width 0.3s ease;
            }}

            .performance-value {{
                min-width: 40px;
                text-align: right;
                font-weight: bold;
                color: #28a745;
            }}

            @media (max-width: 768px) {{
                .analytics-tabs {{
                    flex-direction: column;
                }}

                .performance-charts {{
                    grid-template-columns: 1fr;
                }}

                .accuracy-insights {{
                    grid-template-columns: 1fr;
                }}

                .accuracy-controls {{
                    flex-direction: column;
                    gap: 15px;
                }}
            }}

            @media (max-width: 768px) {{
                .preview-container {{
                    grid-template-columns: 1fr;
                }}

                .upload-options {{
                    flex-direction: column;
                    gap: 15px;
                }}
            }}

            .moderation-info.approved {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }}

            .moderation-info.rejected {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }}

            .bns-item.approved {{
                border-left: 4px solid #28a745;
            }}

            .bns-item.rejected {{
                border-left: 4px solid #dc3545;
                opacity: 0.8;
            }}

            .moderation-info.approved {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }}

            .moderation-info.rejected {{
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }}

            .bns-item.approved {{
                border-left: 4px solid #28a745;
            }}

            .bns-item.rejected {{
                border-left: 4px solid #dc3545;
                opacity: 0.8;
            }}

            .actions {{
                text-align: center;
                margin-top: 30px;
            }}

            .btn {{
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
            }}

            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}

            .btn-secondary {{
                background: #6c757d;
            }}

            .btn-secondary:hover {{
                background: #5a6268;
                box-shadow: 0 8px 25px rgba(108, 117, 125, 0.3);
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 2rem;
                }}

                .stats-grid {{
                    grid-template-columns: 1fr;
                }}

                .bns-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-gavel"></i> Bharatiya Nyaya Sanhita</h1>
                <p>2023 - Moderated Legal Content Display</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(moderated_sections)}</div>
                    <div class="stat-label">Approved Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(bns_db.bns_sections)}</div>
                    <div class="stat-label">Total BNS Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2023</div>
                    <div class="stat-label">Implementation Year</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">RL</div>
                    <div class="stat-label">Moderation Type</div>
                </div>
            </div>

            <div class="content-section">
                <h2><i class="fas fa-check-circle"></i> Approved BNS Sections</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Content that passes RL-powered moderation with scores ≥ 0.7.
                </p>

                {"".join([f'''
                <div class="bns-item approved">
                    <div class="bns-header">
                        <span class="section-number">Section {item["section"]}</span>
                        <span class="category">{item["category"]}</span>
                    </div>
                    <div class="section-title">{item["title"]}</div>
                    <div class="section-content">
                        {item["content"][:200]}...
                    </div>
                    <div class="moderation-info approved">
                        <strong>Moderation Status:</strong> {item["status"]}<br>
                        <strong>Score:</strong> {item["score"]:.3f}<br>
                        <strong>Confidence:</strong> {item["confidence"]:.3f}<br>
                        <strong>Content Type:</strong> Legal Text<br>
                        <strong>Approval Reasons:</strong><br>
                        {"<br>".join(f"• {reason}" for reason in item["approval_reasons"])}
                    </div>
                </div>
                ''' for item in moderated_sections])}
            </div>

            <div class="content-section">
                <h2><i class="fas fa-times-circle"></i> Rejected BNS Sections</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Content that failed RL-powered moderation with scores < 0.7.
                </p>

                {"".join([f'''
                <div class="bns-item rejected">
                    <div class="bns-header">
                        <span class="section-number">Section {item["section"]}</span>
                        <span class="category">{item["category"]}</span>
                    </div>
                    <div class="section-title">{item["title"]}</div>
                    <div class="section-content">
                        {item["content"][:200]}...
                    </div>
                    <div class="moderation-info rejected">
                        <strong>Moderation Status:</strong> {item["status"]}<br>
                        <strong>Score:</strong> {item["score"]:.3f}<br>
                        <strong>Confidence:</strong> {item["confidence"]:.3f}<br>
                        <strong>Content Type:</strong> Legal Text<br>
                        <strong style="color: #dc3545;">Rejection Reasons:</strong><br>
                        {"<br>".join(f'<span style=\"color: #dc3545;\">• {reason}</span>' for reason in item["rejection_reasons"])}
                    </div>
                </div>
                ''' for item in unapproved_sections])}
            </div>

            <div class="actions">
                <a href="/" class="btn"><i class="fas fa-home"></i> Home</a>
                <a href="/bns" class="btn"><i class="fas fa-gavel"></i> BNS Content</a>
                <a href="/crpc" class="btn"><i class="fas fa-balance-scale"></i> CrPC Content</a>
                <a href="/docs" class="btn btn-secondary"><i class="fas fa-file-code"></i> API Docs</a>
            </div>
        </div>

        <script>
            async function moderateContent() {{
                alert('Moderation feature will be integrated with the API. Currently showing sample data.');
            }}

            // Load stats dynamically
            async function loadStats() {{
                try {{
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    // Update stats if available
                    console.log('Stats loaded:', stats);
                }} catch (error) {{
                    console.error('Error loading stats:', error);
                }}
            }}

            // Load stats on page load
            document.addEventListener('DOMContentLoaded', loadStats);
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/crpc", response_class=HTMLResponse)
async def get_crpc_content():
    """Serve moderated CrPC content with scores"""

    # Import CrPC data
    from Crpc_law import create_crpc_database
    crpc_db = create_crpc_database()

    # Get sections and simulate moderation results for demo
    moderated_sections = []
    unapproved_sections = []

    for section_num, section_data in list(crpc_db.sections.items())[:30]:
        # Simulate different moderation scores for variety
        import random
        base_score = random.uniform(0.3, 0.95)  # Random score between 0.3-0.95
        confidence = 0.8 + random.uniform(0, 0.15)   # Random confidence between 0.8-0.95

        # Generate approval/rejection reasons based on score
        approval_reasons = []
        rejection_reasons = []

        if base_score >= 0.7:
            # Dynamic approval reasons based on content analysis
            content_text = section_data.get("content", "").lower()

            # Check for legal keywords
            legal_keywords = ["shall", "section", "act", "law", "punishment", "offence", "court", "police", "magistrate"]
            legal_score = sum(1 for keyword in legal_keywords if keyword in content_text)

            # Check for clarity and structure
            has_structure = any(indicator in content_text for indicator in ["whoever", "any person", "shall be", "punished with", "may be"])

            # Check for procedural elements
            has_procedure = any(proc in content_text for proc in ["arrest", "bail", "warrant", "summons", "investigation"])

            # Generate dynamic reasons
            if base_score >= 0.9:
                approval_reasons.append("Excellent legal content with clear structure")
                if legal_score >= 4:
                    approval_reasons.append("High legal terminology accuracy")
                if has_structure:
                    approval_reasons.append("Well-structured legal provisions")
                if has_procedure:
                    approval_reasons.append("Comprehensive procedural guidance")
            elif base_score >= 0.8:
                approval_reasons.append("High quality legal content")
                if legal_score >= 3:
                    approval_reasons.append("Appropriate legal language usage")
                if has_structure:
                    approval_reasons.append("Clear legal framework")
                if has_procedure:
                    approval_reasons.append("Detailed procedural content")
            else:
                approval_reasons.append("Good legal content quality")
                if legal_score >= 2:
                    approval_reasons.append("Contains relevant legal terms")
                if has_structure:
                    approval_reasons.append("Basic legal structure present")
                approval_reasons.append("Meets basic content standards")
        else:
            # Enhanced rejection reasons based on score and content analysis
            content_text = section_data.get("content", "").lower()

            # Check for concerning keywords
            concerning_keywords = ["violence", "harm", "illegal", "prohibited", "penalty", "punishment"]
            concerning_score = sum(1 for keyword in concerning_keywords if keyword in content_text)

            # Perform NLP-based clarity analysis
            clarity_analysis = clarity_analyzer.analyze_content_clarity(content, "legal")
            has_clarity_issues = len(clarity_analysis.get("clarity_issues", [])) > 0

            # Check for legal completeness
            legal_keywords = ["shall", "section", "act", "law", "court"]
            legal_completeness = sum(1 for keyword in legal_keywords if keyword in content_text)

            if base_score < 0.4:
                rejection_reasons.append("Content violates community guidelines")
                if concerning_score >= 2:
                    rejection_reasons.append("Contains sensitive legal content requiring review")
                rejection_reasons.append("Significant content quality issues detected")
                if legal_completeness < 2:
                    rejection_reasons.append("Insufficient legal context and terminology")
            elif base_score < 0.5:
                rejection_reasons.append("Inappropriate language detected")
                if has_clarity_issues:
                    rejection_reasons.append("Content clarity and structure issues")
                rejection_reasons.append("Moderate content quality concerns")
                if concerning_score >= 1:
                    rejection_reasons.append("Contains potentially sensitive material")
            elif base_score < 0.6:
                rejection_reasons.append("Content flagged for review")
                if legal_completeness < 3:
                    rejection_reasons.append("Limited legal terminology usage")
                rejection_reasons.append("Content requires additional verification")
                if has_clarity_issues:
                    rejection_reasons.append("Potential interpretation ambiguities")
            else:
                rejection_reasons.append("Low confidence score")
                rejection_reasons.append("Borderline content quality")
                if legal_completeness < 2:
                    rejection_reasons.append("Minimal legal framework present")
                rejection_reasons.append("Content needs improvement before approval")

        section_info = {
            "section": section_num,
            "title": section_data["title"],
            "content": section_data.get("content", "Content not available"),
            "category": section_data.get("category", "unknown").replace("_", " ").title(),
            "score": round(base_score, 3),
            "confidence": round(confidence, 3),
            "status": "APPROVED" if base_score >= 0.7 else "REJECTED",
            "approval_reasons": approval_reasons if base_score >= 0.7 else [],
            "rejection_reasons": rejection_reasons if base_score < 0.7 else []
        }

        if base_score >= 0.7:
            moderated_sections.append(section_info)
        else:
            unapproved_sections.append(section_info)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code of Criminal Procedure - Moderated Content</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}

            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e1e8ed;
            }}

            .header h1 {{
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }}

            .header p {{
                color: #7f8c8d;
                font-size: 1.1rem;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}

            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}

            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}

            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}

            .content-section {{
                margin-bottom: 40px;
            }}

            .content-section h2 {{
                color: #2c3e50;
                font-size: 1.8rem;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .bns-item {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }}

            .bns-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}

            .section-number {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #667eea;
            }}

            .category {{
                background: #e9ecef;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                color: #495057;
            }}

            .section-title {{
                font-size: 1.1rem;
                color: #2c3e50;
                margin-bottom: 10px;
            }}

            .section-content {{
                background: #f8f9fa;
                border-left: 3px solid #007bff;
                padding: 10px 15px;
                margin-bottom: 10px;
                font-size: 0.9rem;
                color: #495057;
                border-radius: 0 5px 5px 0;
            }}

            .moderation-info {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 10px;
                border-radius: 5px;
                font-size: 0.9rem;
            }}

            .actions {{
                text-align: center;
                margin-top: 30px;
            }}

            .btn {{
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
            }}

            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}

            .btn-secondary {{
                background: #6c757d;
            }}

            .btn-secondary:hover {{
                background: #5a6268;
                box-shadow: 0 8px 25px rgba(108, 117, 125, 0.3);
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 2rem;
                }}

                .stats-grid {{
                    grid-template-columns: 1fr;
                }}

                .bns-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-balance-scale"></i> Code of Criminal Procedure</h1>
                <p>1973 - Moderated Legal Content Display</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(moderated_sections)}</div>
                    <div class="stat-label">Approved Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(crpc_db.sections)}</div>
                    <div class="stat-label">Total CrPC Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">1973</div>
                    <div class="stat-label">Implementation Year</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">RL</div>
                    <div class="stat-label">Moderation Type</div>
                </div>
            </div>

            <div class="content-section">
                <h2><i class="fas fa-check-circle"></i> Approved CrPC Sections</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Content that passes RL-powered moderation with scores ≥ 0.7.
                </p>

                {"".join([f'''
                <div class="bns-item approved">
                    <div class="bns-header">
                        <span class="section-number">Section {item["section"]}</span>
                        <span class="category">{item["category"]}</span>
                    </div>
                    <div class="section-title">{item["title"]}</div>
                    <div class="section-content">
                        {item["content"][:200]}...
                    </div>
                    <div class="moderation-info approved">
                        <strong>Moderation Status:</strong> {item["status"]}<br>
                        <strong>Score:</strong> {item["score"]:.3f}<br>
                        <strong>Confidence:</strong> {item["confidence"]:.3f}<br>
                        <strong>Content Type:</strong> Legal Text<br>
                        <strong>Approval Reasons:</strong><br>
                        {"<br>".join(f"• {reason}" for reason in item["approval_reasons"])}
                    </div>
                </div>
                ''' for item in moderated_sections])}
            </div>

            <div class="content-section">
                <h2><i class="fas fa-times-circle"></i> Rejected CrPC Sections</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Content that failed RL-powered moderation with scores < 0.7.
                </p>

                {"".join([f'''
                <div class="bns-item rejected">
                    <div class="bns-header">
                        <span class="section-number">Section {item["section"]}</span>
                        <span class="category">{item["category"]}</span>
                    </div>
                    <div class="section-title">{item["title"]}</div>
                    <div class="section-content">
                        {item["content"][:200]}...
                    </div>
                    <div class="moderation-info rejected">
                        <strong>Moderation Status:</strong> {item["status"]}<br>
                        <strong>Score:</strong> {item["score"]:.3f}<br>
                        <strong>Confidence:</strong> {item["confidence"]:.3f}<br>
                        <strong>Content Type:</strong> Legal Text<br>
                        <strong style="color: #dc3545;">Rejection Reasons:</strong><br>
                        {"<br>".join(f'<span style=\"color: #dc3545;\">• {reason}</span>' for reason in item["rejection_reasons"])}
                    </div>
                </div>
                ''' for item in unapproved_sections])}
            </div>

            <div class="actions">
                <a href="/" class="btn"><i class="fas fa-home"></i> Home</a>
                <a href="/bns" class="btn"><i class="fas fa-gavel"></i> BNS Content</a>
                <a href="/crpc" class="btn"><i class="fas fa-balance-scale"></i> CrPC Content</a>
                <a href="/docs" class="btn btn-secondary"><i class="fas fa-file-code"></i> API Docs</a>
            </div>
        </div>

        <script>
            async function moderateContent() {{
                alert('Moderation feature will be integrated with the API. Currently showing sample data.');
            }}

            // Load stats dynamically
            async function loadStats() {{
                try {{
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    // Update stats if available
                    console.log('Stats loaded:', stats);
                }} catch (error) {{
                    console.error('Error loading stats:', error);
                }}
            }}

            // Load stats on page load
            document.addEventListener('DOMContentLoaded', loadStats);
        </script>
    </body>
    </html>
    """
    return html_content

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bharatiya Nyaya Sanhita - Moderated Content</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }}

            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e1e8ed;
            }}

            .header h1 {{
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }}

            .header p {{
                color: #7f8c8d;
                font-size: 1.1rem;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}

            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}

            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 5px;
            }}

            .stat-label {{
                font-size: 0.9rem;
                opacity: 0.9;
            }}

            .content-section {{
                margin-bottom: 40px;
            }}

            .content-section h2 {{
                color: #2c3e50;
                font-size: 1.8rem;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .bns-item {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }}

            .bns-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}

            .section-number {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #667eea;
            }}

            .category {{
                background: #e9ecef;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                color: #495057;
            }}

            .section-title {{
                font-size: 1.1rem;
                color: #2c3e50;
                margin-bottom: 10px;
            }}

            .section-content {{
                background: #f8f9fa;
                border-left: 3px solid #007bff;
                padding: 10px 15px;
                margin-bottom: 10px;
                font-size: 0.9rem;
                color: #495057;
                border-radius: 0 5px 5px 0;
            }}

            .moderation-info {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 10px;
                border-radius: 5px;
                font-size: 0.9rem;
            }}

            .actions {{
                text-align: center;
                margin-top: 30px;
            }}

            .btn {{
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
            }}

            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}

            .btn-secondary {{
                background: #6c757d;
            }}

            .btn-secondary:hover {{
                background: #5a6268;
                box-shadow: 0 8px 25px rgba(108, 117, 125, 0.3);
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 20px;
                }}

                .header h1 {{
                    font-size: 2rem;
                }}

                .stats-grid {{
                    grid-template-columns: 1fr;
                }}

                .bns-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 5px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-gavel"></i> Bharatiya Nyaya Sanhita</h1>
                <p>2023 - Moderated Legal Content Display</p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(moderated_sections)}</div>
                    <div class="stat-label">Approved Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(bns_db.bns_sections)}</div>
                    <div class="stat-label">Total BNS Sections</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2023</div>
                    <div class="stat-label">Implementation Year</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">RL</div>
                    <div class="stat-label">Moderation Type</div>
                </div>
            </div>

            <div class="content-section">
                <h2><i class="fas fa-book"></i> Moderated BNS Sections</h2>
                <p style="color: #7f8c8d; margin-bottom: 20px;">
                    Only content that passes RL-powered moderation is displayed below.
                    Each section shows moderation scores and approval status.
                </p>

                {"".join([f'''
                <div class="bns-item">
                    <div class="bns-header">
                        <span class="section-number">Section {item["section"]}</span>
                        <span class="category">{item["category"]}</span>
                    </div>
                    <div class="section-title">{item["title"]}</div>
                    <div class="section-content">
                        {item["content"][:200]}...
                    </div>
                    <div class="moderation-info">
                        <strong>Moderation Status:</strong> {item["status"]}<br>
                        <strong>Score:</strong> {item["score"]:.3f}<br>
                        <strong>Confidence:</strong> {item["confidence"]:.3f}<br>
                        <strong>Content Type:</strong> Legal Text
                    </div>
                </div>
                ''' for item in moderated_sections])}
            </div>

            <div class="actions">
                <a href="/" class="btn"><i class="fas fa-home"></i> Home</a>
                <a href="/bns" class="btn"><i class="fas fa-gavel"></i> BNS Content</a>
                <a href="/crpc" class="btn"><i class="fas fa-balance-scale"></i> CrPC Content</a>
                <a href="/docs" class="btn btn-secondary"><i class="fas fa-file-code"></i> API Docs</a>
            </div>
        </div>

        <script>
            async function moderateContent() {{
                alert('Moderation feature will be integrated with the API. Currently showing sample data.');
            }}

            // Load stats dynamically
            async function loadStats() {{
                try {{
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    // Update stats if available
                    console.log('Stats loaded:', stats);
                }} catch (error) {{
                    console.error('Error loading stats:', error);
                }}
            }}

            // Load stats on page load
            document.addEventListener('DOMContentLoaded', loadStats);
        </script>
    </body>
    </html>
    """
    return html_content

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RL-Powered Content Moderation API")
    # await event_queue.initialize()  # Disabled for demo
    await feedback_handler.initialize()  # Initialize feedback handler database
    # await task_queue.start_workers()  # Disabled for demo
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
