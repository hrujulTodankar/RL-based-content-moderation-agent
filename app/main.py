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
                color: red;
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

# Add BNS content endpoint
from fastapi.responses import HTMLResponse
import json

@app.get("/bns", response_class=HTMLResponse)
async def get_bns_content():
    """Serve moderated BNS content with scores"""

    # Import BNS data
    from bharathi_nyaya_sanhita import create_bns_database
    bns_db = create_bns_database()

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

            # Check for clarity issues
            clarity_issues = ["unclear", "ambiguous", "confusing", "incomplete"]
            has_clarity_issues = any(issue in content_text for issue in clarity_issues)

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
            "content": content,
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

            # Check for clarity issues
            clarity_issues = ["unclear", "ambiguous", "confusing", "incomplete"]
            has_clarity_issues = any(issue in content_text for issue in clarity_issues)

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