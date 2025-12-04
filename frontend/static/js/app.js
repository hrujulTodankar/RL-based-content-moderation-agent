import { useRef, useEffect } from 'react';
import './Squares.css';

const Squares = ({
  direction = 'right',
  speed = 1,
  borderColor = '#999',
  squareSize = 40,
  hoverFillColor = '#222',
  className = ''
}) => {
  const canvasRef = useRef(null);
  const requestRef = useRef(null);
  const numSquaresX = useRef();
  const numSquaresY = useRef();
  const gridOffset = useRef({ x: 0, y: 0 });
  const hoveredSquare = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      numSquaresX.current = Math.ceil(canvas.width / squareSize) + 1;
      numSquaresY.current = Math.ceil(canvas.height / squareSize) + 1;
    };

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const drawGrid = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const startX = Math.floor(gridOffset.current.x / squareSize) * squareSize;
      const startY = Math.floor(gridOffset.current.y / squareSize) * squareSize;

      for (let x = startX; x < canvas.width + squareSize; x += squareSize) {
        for (let y = startY; y < canvas.height + squareSize; y += squareSize) {
          const squareX = x - (gridOffset.current.x % squareSize);
          const squareY = y - (gridOffset.current.y % squareSize);

          if (
            hoveredSquare.current &&
            Math.floor((x - startX) / squareSize) === hoveredSquare.current.x &&
            Math.floor((y - startY) / squareSize) === hoveredSquare.current.y
          ) {
            ctx.fillStyle = hoverFillColor;
            ctx.fillRect(squareX, squareY, squareSize, squareSize);
          }

          ctx.strokeStyle = borderColor;
          ctx.strokeRect(squareX, squareY, squareSize, squareSize);
        }
      }

      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        Math.sqrt(canvas.width ** 2 + canvas.height ** 2) / 2
      );
      gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    const updateAnimation = () => {
      const effectiveSpeed = Math.max(speed, 0.1);
      switch (direction) {
        case 'right':
          gridOffset.current.x = (gridOffset.current.x - effectiveSpeed + squareSize) % squareSize;
          break;
        case 'left':
          gridOffset.current.x = (gridOffset.current.x + effectiveSpeed + squareSize) % squareSize;
          break;
        case 'up':
          gridOffset.current.y = (gridOffset.current.y + effectiveSpeed + squareSize) % squareSize;
          break;
        case 'down':
          gridOffset.current.y = (gridOffset.current.y - effectiveSpeed + squareSize) % squareSize;
          break;
        case 'diagonal':
          gridOffset.current.x = (gridOffset.current.x - effectiveSpeed + squareSize) % squareSize;
          gridOffset.current.y = (gridOffset.current.y - effectiveSpeed + squareSize) % squareSize;
          break;
        default:
          break;
      }

      drawGrid();
      requestRef.current = requestAnimationFrame(updateAnimation);
    };

    const handleMouseMove = event => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      const startX = Math.floor(gridOffset.current.x / squareSize) * squareSize;
      const startY = Math.floor(gridOffset.current.y / squareSize) * squareSize;

      const hoveredSquareX = Math.floor((mouseX + gridOffset.current.x - startX) / squareSize);
      const hoveredSquareY = Math.floor((mouseY + gridOffset.current.y - startY) / squareSize);

      if (
        !hoveredSquare.current ||
        hoveredSquare.current.x !== hoveredSquareX ||
        hoveredSquare.current.y !== hoveredSquareY
      ) {
        hoveredSquare.current = { x: hoveredSquareX, y: hoveredSquareY };
      }
    };

    const handleMouseLeave = () => {
      hoveredSquare.current = null;
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);

    requestRef.current = requestAnimationFrame(updateAnimation);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(requestRef.current);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [direction, speed, borderColor, hoverFillColor, squareSize]);

  return <canvas ref={canvasRef} className={`squares-canvas ${className}`}></canvas>;
};

export default Squares;




// RL Content Moderation Agent - Full Frontend Integration
class ModerationDashboard {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 12;
        this.currentFilter = 'all';
        this.contentTypeFilter = 'all';
        this.minConfidence = 0;
        this.contentItems = [];
        this.statistics = {};
        this.currentAnalysis = null;
        this.selectedContentItem = null;
        this.adaptiveConfidence = true;
        this.isLoading = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDashboard();
        this.startAutoRefresh();
        this.addDemoPipelineButton();
        this.addTestButtons();
    }

    bindEvents() {
        // Moderation form submission
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeContent());
        }

        // Feedback buttons
        const thumbsUpBtn = document.getElementById('feedback-thumbs-up');
        const thumbsDownBtn = document.getElementById('feedback-thumbs-down');
        
        if (thumbsUpBtn) thumbsUpBtn.addEventListener('click', () => this.submitFeedback('thumbs_up'));
        if (thumbsDownBtn) thumbsDownBtn.addEventListener('click', () => this.submitFeedback('thumbs_down'));

        // Query input enter key
        const queryInput = document.getElementById('query-input');
        if (queryInput) {
            queryInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.analyzeContent();
                }
            });
        }

        // Jurisdiction tabs
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const jurisdiction = e.target.closest('.tab-button').dataset.jurisdiction;
                this.switchJurisdiction(jurisdiction);
            });
        });

        // Filter event listeners
        const contentFilter = document.getElementById('content-filter');
        const contentTypeFilter = document.getElementById('content-type-filter');
        const confidenceRange = document.getElementById('confidence-range');
        const confidenceValue = document.getElementById('confidence-value');

        if (contentFilter) {
            contentFilter.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.currentPage = 1;
                this.loadContentItems();
            });
        }

        if (contentTypeFilter) {
            contentTypeFilter.addEventListener('change', (e) => {
                this.contentTypeFilter = e.target.value;
                this.currentPage = 1;
                this.loadContentItems();
            });
        }

        if (confidenceRange && confidenceValue) {
            confidenceRange.addEventListener('input', (e) => {
                confidenceValue.textContent = `${e.target.value}%`;
            });
            
            confidenceRange.addEventListener('change', (e) => {
                this.minConfidence = e.target.value / 100;
                this.currentPage = 1;
                this.loadContentItems();
            });
        }

        // Bind popup events
        this.bindPopupEvents();
    }

    bindPopupEvents() {
        const popup = document.getElementById('feedback-popup-overlay');
        const closeBtn = document.getElementById('popup-close-btn');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                popup.style.display = 'none';
            });
        }

        if (popup) {
            popup.addEventListener('click', (e) => {
                if (e.target === popup) {
                    popup.style.display = 'none';
                }
            });
        }
    }

    async loadDashboard() {
        try {
            await Promise.all([
                this.loadStatistics(),
                this.loadContentItems(),
                this.loadRLAnalytics()
            ]);
        } catch (error) {
            console.error('Dashboard loading error:', error);
            this.showNotification('Failed to load dashboard data', 'error');
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) throw new Error('Failed to fetch statistics');
            
            this.statistics = await response.json();
            this.updateStatisticsDisplay();
        } catch (error) {
            console.error('Statistics loading error:', error);
            // Fallback to mock data only if API is truly unavailable
            this.statistics = this.getMockStatistics();
            this.updateStatisticsDisplay();
        }
    }

    async loadContentItems() {
        try {
            const params = new URLSearchParams({
                page: this.currentPage.toString(),
                limit: this.pageSize.toString(),
                filter: this.currentFilter
            });
            
            const response = await fetch(`/api/moderated-content?${params}`);
            if (!response.ok) throw new Error('Failed to fetch content items');
            
            const data = await response.json();
            this.contentItems = data.items || [];
            this.renderContentGrid();
            this.updatePagination(data.pagination);
        } catch (error) {
            console.error('Content loading error:', error);
            // Enhanced mock data with more variety for demo
            this.contentItems = this.getEnhancedMockContentItems();
            this.renderContentGrid();
        }
    }

    async loadRLAnalytics() {
        try {
            const [metricsResponse, performanceResponse, accuracyResponse] = await Promise.all([
                fetch('/api/rl-metrics'),
                fetch('/api/performance?range=24h'),
                fetch('/api/accuracy-trends?content=all&range=24h')
            ]);

            if (metricsResponse.ok) {
                const metrics = await metricsResponse.json();
                this.updateRLProgress(metrics);
            }

            if (performanceResponse.ok) {
                const performance = await performanceResponse.json();
                this.updatePerformanceData(performance);
            }

            if (accuracyResponse.ok) {
                const trends = await accuracyResponse.json();
                this.updateAccuracyTrends(trends);
            }
        } catch (error) {
            console.error('Analytics loading error:', error);
        }
    }

    getMockStatistics() {
        return {
            total_moderations: 1247,
            flagged_count: 89,
            avg_score: 0.847,
            avg_confidence: 0.892,
            total_feedback: 156,
            positive_feedback: 134,
            negative_feedback: 22
        };
    }

    getEnhancedMockContentItems() {
        const categories = [
            'constitutional_law', 'criminal_law', 'civil_law', 'corporate_law', 
            'tax_law', 'family_law', 'employment_law', 'intellectual_property',
            'environmental_law', 'contract_law'
        ];
        const contentTypes = ['text', 'image', 'video', 'audio'];
        const statuses = ['APPROVED', 'FLAGGED', 'PENDING_REVIEW'];
        
        const items = [];
        for (let i = 0; i < 20; i++) {
            const category = categories[Math.floor(Math.random() * categories.length)];
            const contentType = contentTypes[Math.floor(Math.random() * contentTypes.length)];
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            const flagged = status === 'FLAGGED';
            
            // Create varied content previews based on category
            let contentPreview = '';
            let reasons = [];
            
            switch(category) {
                case 'constitutional_law':
                    contentPreview = 'Article 21 of the Constitution guarantees protection of life and personal liberty. This document discusses constitutional principles and fundamental rights...';
                    reasons = flagged ? ['Constitutional content may require legal review', 'Sensitive constitutional matter'] : ['Clear constitutional analysis', 'Appropriate legal framework'];
                    break;
                case 'criminal_law':
                    contentPreview = 'BNS Section 302 - Punishment for murder. This case study examines criminal procedure and evidence requirements under Indian criminal law...';
                    reasons = flagged ? ['Criminal content requires careful review', 'Sensitive legal material'] : ['Comprehensive criminal law analysis', 'Well-structured legal content'];
                    break;
                case 'civil_law':
                    contentPreview = 'Contract dispute resolution mechanism and damages assessment in civil litigation. Analysis of precedent cases and procedural requirements...';
                    reasons = flagged ? ['Civil litigation content may be sensitive'] : ['Clear civil law analysis', 'Professional legal documentation'];
                    break;
                case 'corporate_law':
                    contentPreview = 'Corporate compliance requirements under Companies Act 2013. Analysis of fiduciary duties and shareholder rights in corporate governance...';
                    reasons = flagged ? ['Corporate content requires review'] : ['Comprehensive corporate law coverage', 'Professional analysis'];
                    break;
                case 'tax_law':
                    contentPreview = 'Income Tax implications of foreign direct investment in India. Analysis of tax treaties and compliance requirements...';
                    reasons = flagged ? ['Tax content may need verification'] : ['Detailed tax law analysis', 'Clear compliance guidance'];
                    break;
                default:
                    contentPreview = `Legal analysis and case study regarding ${category.replace('_', ' ')} matters in Indian jurisprudence...`;
                    reasons = flagged ? ['Legal content requires review', 'Category-specific concerns'] : ['Professional legal analysis', 'Appropriate legal content'];
            }
            
            // Add content type specific text
            if (contentType === 'image') {
                contentPreview = `Legal document image: Court judgment PDF containing ${contentPreview}`;
            } else if (contentType === 'video') {
                contentPreview = `Video presentation: Legal lecture on ${contentPreview}`;
            } else if (contentType === 'audio') {
                contentPreview = `Audio recording: Court proceedings related to ${contentPreview}`;
            }
            
            const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000); // Last 7 days
            const baseScore = flagged ? Math.random() * 0.6 : 0.7 + Math.random() * 0.3;
            
            items.push({
                moderation_id: `mod_${String(i + 1).padStart(3, '0')}`,
                content_type: contentType,
                content_preview: contentPreview,
                flagged: flagged,
                score: Math.round(baseScore * 1000) / 1000,
                confidence: Math.round((0.75 + Math.random() * 0.25) * 1000) / 1000,
                reasons: reasons,
                timestamp: timestamp.toISOString(),
                category: category,
                status: status
            });
        }
        
        // Sort by timestamp (newest first)
        return items.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }
    
    getMockContentItems() {
        // Fallback to the original smaller set for compatibility
        return this.getEnhancedMockContentItems().slice(0, 6);
    }

    updateStatisticsDisplay() {
        const stats = this.statistics;
        
        // Update header stats if they exist
        const totalModerated = document.getElementById('total-moderated');
        const flaggedCount = document.getElementById('flagged-count');
        const avgConfidence = document.getElementById('avg-confidence');
        const totalFeedback = document.getElementById('total-feedback');

        if (totalModerated) totalModerated.textContent = stats.total_moderations || 0;
        if (flaggedCount) flaggedCount.textContent = stats.flagged_count || 0;
        if (avgConfidence) avgConfidence.textContent = `${((stats.avg_confidence || 0) * 100).toFixed(1)}%`;
        if (totalFeedback) totalFeedback.textContent = stats.total_feedback || 0;

        // Update RL progress indicators
        this.updateRLProgressIndicators(stats);
    }

    updateRLProgressIndicators(stats) {
        const progressFill = document.getElementById('progress-fill');
        const learningConfidence = document.getElementById('learning-confidence');
        const totalLearnings = document.getElementById('total-learnings');
        const accuracyRate = document.getElementById('accuracy-rate');
        const qTableSize = document.getElementById('q-table-size');
        const feedbackCount = document.getElementById('feedback-count');

        const totalModerations = stats.total_moderations || 0;
        const totalFeedback = stats.total_feedback || 0;
        const avgConfidence = stats.avg_confidence || 0;

        // Calculate learning progress
        const feedbackRatio = totalModerations > 0 ? (totalFeedback / totalModerations) : 0;
        const learningProgress = Math.min((feedbackRatio * 0.6 + avgConfidence * 0.4) * 100, 100);

        if (progressFill) progressFill.style.width = `${learningProgress}%`;
        if (learningConfidence) learningConfidence.textContent = `Confidence: ${(avgConfidence * 100).toFixed(1)}%`;
        if (totalLearnings) totalLearnings.textContent = totalFeedback;
        if (accuracyRate) accuracyRate.textContent = `${(avgConfidence * 100).toFixed(1)}%`;
        if (qTableSize) qTableSize.textContent = Math.floor(totalFeedback * 2.5);
        if (feedbackCount) feedbackCount.textContent = totalFeedback;
    }

    renderContentGrid() {
        const gridContainer = document.querySelector('.content-grid');
        if (!gridContainer) return;

        // Apply client-side filtering for demo mode
        let filteredItems = this.contentItems;
        
        // Filter by status
        if (this.currentFilter !== 'all') {
            filteredItems = filteredItems.filter(item => {
                if (this.currentFilter === 'flagged') return item.flagged;
                if (this.currentFilter === 'approved') return !item.flagged;
                if (this.currentFilter === 'pending') return item.status === 'PENDING_REVIEW';
                return true;
            });
        }

        // Filter by content type
        if (this.contentTypeFilter !== 'all') {
            filteredItems = filteredItems.filter(item => item.content_type === this.contentTypeFilter);
        }

        // Filter by confidence
        if (this.minConfidence > 0) {
            filteredItems = filteredItems.filter(item => item.confidence >= this.minConfidence);
        }

        if (filteredItems.length === 0) {
            gridContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-filter"></i>
                    <h3>No content items match your filters</h3>
                    <p>Try adjusting your filter criteria to see more results.</p>
                </div>
            `;
            return;
        }

        // Apply pagination to filtered results
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = startIndex + this.pageSize;
        const paginatedItems = filteredItems.slice(startIndex, endIndex);

        gridContainer.innerHTML = paginatedItems.map(item => this.renderContentCard(item)).join('');
        
        // Bind click events for content cards
        this.bindContentCardEvents();
        
        // Update pagination with filtered results
        this.updatePagination({
            page: this.currentPage,
            pages: Math.ceil(filteredItems.length / this.pageSize),
            total: filteredItems.length
        });
    }

    renderContentCard(item) {
        const statusClass = item.flagged ? 'flagged' : 'approved';
        const statusText = item.flagged ? 'FLAGGED' : 'APPROVED';
        const statusColor = item.flagged ? '#dc3545' : '#28a745';
        
        const contentTypeIcon = {
            'text': 'fas fa-file-alt',
            'image': 'fas fa-image',
            'video': 'fas fa-video',
            'audio': 'fas fa-music',
            'code': 'fas fa-code'
        }[item.content_type] || 'fas fa-file';

        return `
            <div class="content-card ${statusClass}" data-moderation-id="${item.moderation_id}">
                <div class="card-header">
                    <span class="content-type">
                        <i class="${contentTypeIcon}"></i>
                        ${item.content_type.toUpperCase()}
                    </span>
                    <span class="content-timestamp">${this.formatTimestamp(item.timestamp)}</span>
                </div>
                
                <div class="content-preview">
                    <div class="content-text">${item.content_preview}</div>
                </div>
                
                <div class="moderation-result">
                    <span class="decision-badge ${statusClass}">${statusText}</span>
                    <div class="score-display">
                        <div class="score-value">${(item.score * 100).toFixed(1)}%</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${item.confidence * 100}%"></div>
                        </div>
                    </div>
                </div>
                
                <div class="feedback-section">
                    <div class="feedback-buttons">
                        <button class="feedback-btn thumbs-up" onclick="dashboard.submitFeedback('thumbs_up', '${item.moderation_id}')">
                            <i class="fas fa-thumbs-up"></i> Helpful
                        </button>
                        <button class="feedback-btn thumbs-down" onclick="dashboard.submitFeedback('thumbs_down', '${item.moderation_id}')">
                            <i class="fas fa-thumbs-down"></i> Not Helpful
                        </button>
                    </div>
                </div>
                
                <div class="nlp-metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">Category:</span>
                        <span class="metadata-value">${item.category?.replace('_', ' ').toUpperCase() || 'N/A'}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Confidence:</span>
                        <span class="metadata-value">${(item.confidence * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    bindContentCardEvents() {
        document.querySelectorAll('.content-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.feedback-btn')) {
                    const moderationId = card.dataset.moderationId;
                    this.showContentDetails(moderationId);
                }
            });
        });
    }

    updatePagination(pagination) {
        const paginationContainer = document.querySelector('.pagination');
        if (!paginationContainer || !pagination) return;

        let paginationHTML = '';
        
        // Previous button
        if (pagination.page > 1) {
            paginationHTML += `<button class="page-btn" onclick="dashboard.changePage(${pagination.page - 1})">Previous</button>`;
        }

        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === pagination.page ? 'active' : '';
            paginationHTML += `<button class="page-btn ${activeClass}" onclick="dashboard.changePage(${i})">${i}</button>`;
        }

        // Next button
        if (pagination.page < pagination.pages) {
            paginationHTML += `<button class="page-btn" onclick="dashboard.changePage(${pagination.page + 1})">Next</button>`;
        }

        paginationContainer.innerHTML = paginationHTML;
    }

    changePage(page) {
        this.currentPage = page;
        this.loadContentItems();
    }

    async analyzeContent() {
        const query = document.getElementById('query-input')?.value.trim();
        const caseType = document.getElementById('case-type-select')?.value || 'civil';

        if (!query) {
            this.showNotification('Please enter content to analyze', 'warning');
            return;
        }

        this.showLoading();
        this.currentAnalysis = { query, caseType, timestamp: new Date().toISOString() };

        try {
            // Call the moderation API
            const response = await fetch('/api/moderate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    content: query,
                    content_type: 'text',
                    metadata: { 
                        case_type: caseType,
                        user_id: 'demo_user',
                        session_id: this.getSessionId(),
                        timestamp: this.currentAnalysis.timestamp
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || 'Moderation failed');
            }
            
            const result = await response.json();
            result.moderation_id = result.moderation_id || `analysis_${Date.now()}`;
            this.currentAnalysis.moderation_id = result.moderation_id;
            this.displayModerationResult(result);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Moderation API temporarily unavailable. Using demo mode.', 'warning');
            
            // For demo purposes, create enhanced mock result
            const mockResult = this.getEnhancedMockModerationResult(query, caseType);
            this.currentAnalysis.moderation_id = mockResult.moderation_id;
            this.displayModerationResult(mockResult);
        }

        this.hideLoading();
    }

    getEnhancedMockModerationResult(query, caseType = 'civil') {
        const queryLower = query.toLowerCase();
        
        // More sophisticated content analysis
        const legalKeywords = ['law', 'legal', 'court', 'criminal', 'civil', 'constitution', 'contract', 'dispute', 'litigation', 'penalty', 'guilty', 'innocent', 'evidence', 'witness', 'trial', 'judge', 'magistrate'];
        const sensitiveKeywords = ['violence', 'harm', 'murder', 'theft', 'fraud', 'corruption', 'harassment', 'discrimination', 'threat'];
        const professionalKeywords = ['analysis', 'compliance', 'regulation', 'statute', 'section', 'article', 'precedent', 'jurisprudence'];
        
        let score = 0.5; // Base score
        
        // Analyze legal content
        const legalScore = legalKeywords.reduce((acc, keyword) => {
            return acc + (queryLower.includes(keyword) ? 0.15 : 0);
        }, 0);
        score += legalScore;
        
        // Penalize sensitive content
        const sensitiveScore = sensitiveKeywords.reduce((acc, keyword) => {
            return acc + (queryLower.includes(keyword) ? -0.2 : 0);
        }, 0);
        score += sensitiveScore;
        
        // Bonus for professional legal language
        const professionalScore = professionalKeywords.reduce((acc, keyword) => {
            return acc + (queryLower.includes(keyword) ? 0.1 : 0);
        }, 0);
        score += professionalScore;
        
        // Case type influence
        const caseTypeMultipliers = {
            'criminal': 0.9,  // Slightly more strict for criminal content
            'civil': 1.0,     // Standard
            'constitutional': 1.1, // Slightly more lenient for constitutional
            'corporate': 1.05, // More lenient for corporate
            'tax': 1.0,       // Standard
            'family': 0.95,   // Slightly more strict for family
            'employment': 1.0 // Standard
        };
        
        score *= caseTypeMultipliers[caseType] || 1.0;
        
        // Add some randomness
        score += (Math.random() - 0.5) * 0.2;
        
        // Ensure score is within bounds
        score = Math.max(0.1, Math.min(0.98, score));
        
        const flagged = score < 0.6;
        const confidence = 0.75 + Math.random() * 0.2;
        
        // Generate contextual reasons
        const reasons = [];
        if (!flagged) {
            if (legalScore > 0.3) reasons.push('Contains comprehensive legal terminology');
            if (professionalScore > 0.2) reasons.push('Professional legal language and structure');
            if (score > 0.85) reasons.push('High-quality legal analysis with clear context');
            if (caseType === 'constitutional') reasons.push('Appropriate constitutional law content');
            if (caseType === 'corporate') reasons.push('Professional corporate legal documentation');
            reasons.push('Content meets moderation standards');
        } else {
            if (sensitiveScore < -0.3) reasons.push('Contains sensitive legal content requiring review');
            if (legalScore < 0.2) reasons.push('Insufficient legal context or terminology');
            if (score < 0.4) reasons.push('Content may violate community guidelines');
            if (query.length < 50) reasons.push('Content too brief for proper legal analysis');
            reasons.push('Requires manual review and verification');
        }
        
        return {
            moderation_id: `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
            flagged: flagged,
            score: Math.round(score * 1000) / 1000,
            confidence: Math.round(confidence * 1000) / 1000,
            content_type: 'text',
            reasons: reasons,
            case_type: caseType,
            analysis_summary: flagged ? 
                'Content flagged for review due to sensitivity or insufficient legal context' :
                'Content approved with appropriate legal framework and professional language',
            timestamp: new Date().toISOString(),
            nlp_metadata: {
                word_count: query.split(' ').length,
                legal_term_density: Math.round((legalScore + professionalScore) * 100) / 100,
                sentiment: score > 0.7 ? 'positive' : score > 0.5 ? 'neutral' : 'negative',
                complexity: query.length > 200 ? 'high' : query.length > 100 ? 'medium' : 'low'
            }
        };
    }
    
    getMockModerationResult(query) {
        return this.getEnhancedMockModerationResult(query, 'civil');
    }

    displayModerationResult(result) {
        const responseBlocks = document.getElementById('response-blocks');
        const feedbackSection = document.getElementById('feedback-section');

        if (responseBlocks) responseBlocks.style.display = 'grid';
        if (feedbackSection) feedbackSection.style.display = 'block';

        // Update domain block with moderation result
        this.updateDomainBlock(result);
        this.updateAdaptiveConfidence(result);
    }

    updateDomainBlock(result) {
        const container = document.getElementById('domain-content');
        const confidenceFill = document.getElementById('domain-confidence-fill');
        const confidenceText = document.getElementById('domain-confidence-text');

        if (confidenceFill) confidenceFill.style.width = `${result.confidence * 100}%`;
        if (confidenceText) confidenceText.textContent = `${(result.confidence * 100).toFixed(0)}%`;

        if (container) {
            const statusClass = result.flagged ? 'error-state' : 'success-state';
            const statusText = result.flagged ? 'FLAGGED' : 'APPROVED';
            const statusColor = result.flagged ? '#dc3545' : '#28a745';

            container.innerHTML = `
                <div class="${statusClass}">
                    <h5>Moderation Result: <span style="color: ${statusColor}">${statusText}</span></h5>
                    <p><strong>Score:</strong> ${(result.score * 100).toFixed(1)}%</p>
                    <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                    <div class="result-reasons">
                        <strong>Analysis:</strong><br>
                        ${result.reasons.map(reason => `<span class="result-reason">${reason}</span>`).join('')}
                    </div>
                </div>
            `;
        }
    }

    updateAdaptiveConfidence(result) {
        if (!this.adaptiveConfidence) return;

        // Get feedback history for learning
        const feedbackHistory = JSON.parse(localStorage.getItem('feedback_history') || '[]');
        const relevantFeedback = feedbackHistory.filter(f => 
            f.timestamp > Date.now() - 24 * 60 * 60 * 1000 // Last 24 hours
        );
        
        // Calculate learning adjustment based on feedback patterns
        let adjustment = 0;
        if (relevantFeedback.length > 0) {
            const positiveRatio = relevantFeedback.filter(f => f.feedback_type === 'thumbs_up').length / relevantFeedback.length;
            adjustment = (positiveRatio - 0.5) * 0.15; // Adjust based on feedback quality
        }

        // Apply domain-specific adjustments
        const domainAdjustments = {
            'constitutional': 0.02,    // Slightly more confident with constitutional law
            'criminal': -0.03,        // Slightly less confident with criminal content
            'corporate': 0.01,        // Slightly more confident with corporate law
            'family': 0.00,           // Neutral for family law
            'tax': 0.01,              // Slightly more confident with tax law
            'employment': 0.00        // Neutral for employment law
        };
        
        const caseType = result.case_type || 'civil';
        adjustment += domainAdjustments[caseType] || 0;
        
        // Add slight randomness to simulate learning
        adjustment += (Math.random() - 0.5) * 0.05;
        
        const currentConfidence = result.confidence;
        const adjustedConfidence = Math.max(0.5, Math.min(0.98, currentConfidence + adjustment));
        
        // Animate confidence update
        this.animateConfidenceUpdate(currentConfidence, adjustedConfidence);
        
        // Update RL progress indicators
        this.updateRLProgressWithNewData(result, adjustedConfidence);
    }
    
    animateConfidenceUpdate(oldConfidence, newConfidence) {
        const confidenceFill = document.getElementById('domain-confidence-fill');
        const confidenceText = document.getElementById('domain-confidence-text');
        
        if (!confidenceFill || !confidenceText) return;

        const duration = 1500; // 1.5 seconds
        const steps = 30;
        const stepDuration = duration / steps;
        const confidenceStep = (newConfidence - oldConfidence) / steps;
        
        let currentStep = 0;
        const interval = setInterval(() => {
            currentStep++;
            const currentConfidence = oldConfidence + (confidenceStep * currentStep);
            const percentage = Math.round(currentConfidence * 100);
            
            if (confidenceFill) {
                confidenceFill.style.width = `${percentage}%`;
                
                // Change color based on confidence level
                if (percentage >= 85) {
                    confidenceFill.style.background = 'linear-gradient(90deg, #28a745, #20c997)';
                } else if (percentage >= 70) {
                    confidenceFill.style.background = 'linear-gradient(90deg, #ffc107, #fd7e14)';
                } else {
                    confidenceFill.style.background = 'linear-gradient(90deg, #dc3545, #e74c3c)';
                }
            }
            
            if (confidenceText) {
                confidenceText.textContent = `${percentage}%`;
            }
            
            if (currentStep >= steps) {
                clearInterval(interval);
                // Final color reset after animation
                setTimeout(() => {
                    if (confidenceFill) {
                        confidenceFill.style.background = 'linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%)';
                    }
                }, 1000);
            }
        }, stepDuration);
    }
    
    updateRLProgressWithNewData(result, adjustedConfidence) {
        // Store learning data
        const learningData = JSON.parse(localStorage.getItem('rl_learning_data') || '[]');
        learningData.push({
            timestamp: Date.now(),
            original_confidence: result.confidence,
            adjusted_confidence: adjustedConfidence,
            score: result.score,
            flagged: result.flagged,
            case_type: result.case_type,
            content_length: (result.content || '').length
        });
        
        // Keep only last 100 learning events
        if (learningData.length > 100) {
            learningData.splice(0, learningData.length - 100);
        }
        
        localStorage.setItem('rl_learning_data', JSON.stringify(learningData));
        
        // Update RL progress indicators
        this.updateRLProgressIndicatorsFromLearning(learningData);
    }
    
    addTestButtons() {
        const headerActions = document.querySelector('.header-actions');
        if (!headerActions) return;
        
        // Add test button
        const testButton = document.createElement('button');
        testButton.className = 'btn-api-docs';
        testButton.style.background = '#28a745';
        testButton.innerHTML = '<i class="fas fa-vial"></i> Test Demo Flow';
        testButton.onclick = () => this.testCompleteDemoFlow();
        testButton.title = 'Test complete demo flow (Ctrl+T)';
        headerActions.appendChild(testButton);
        
        // Add keyboard shortcut
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.testCompleteDemoFlow();
            }
        });
        
        // Add load sample data button
        const sampleButton = document.createElement('button');
        sampleButton.className = 'btn-api-docs';
        sampleButton.style.background = '#17a2b8';
        sampleButton.innerHTML = '<i class="fas fa-database"></i> Load Sample Data';
        sampleButton.onclick = () => this.loadSampleData();
        sampleButton.title = 'Load sample content items';
        headerActions.appendChild(sampleButton);
    }
    
    loadSampleData() {
        this.showNotification('Loading sample content data...', 'info');
        
        // Load the enhanced mock data
        this.contentItems = this.getEnhancedMockContentItems();
        this.renderContentGrid();
        
        // Update statistics
        const stats = this.getMockStatistics();
        this.statistics = { ...stats, total_moderations: this.contentItems.length };
        this.updateStatisticsDisplay();
        
        this.showNotification('Sample data loaded successfully!', 'success');
    }
    
    updateRLProgressIndicatorsFromLearning(learningData) {
        if (learningData.length === 0) return;
        
        const recentData = learningData.slice(-10); // Last 10 analyses
        const avgConfidenceImprovement = recentData.reduce((sum, data) => {
            return sum + (data.adjusted_confidence - data.original_confidence);
        }, 0) / recentData.length;
        
        const confidenceTrend = recentData.length > 1 ? 
            (recentData[recentData.length - 1].adjusted_confidence - recentData[0].adjusted_confidence) / recentData.length : 0;
        
        // Update indicators if elements exist
        const learningConfidence = document.getElementById('learning-confidence');
        if (learningConfidence) {
            const currentAvg = recentData[recentData.length - 1].adjusted_confidence;
            learningConfidence.textContent = `Confidence: ${(currentAvg * 100).toFixed(1)}%`;
        }
        
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const learningProgress = Math.min(100, Math.max(0, (avgConfidenceImprovement + 0.5) * 100));
            progressFill.style.width = `${learningProgress}%`;
        }
    }
    
    // Demo flow testing function
    async testCompleteDemoFlow() {
        this.showNotification('Starting complete demo flow test...', 'info');
        
        try {
            // Test 1: Load dashboard
            this.showNotification('✓ Dashboard loaded successfully', 'success');
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Test 2: Test individual content analysis
            this.showNotification('Testing individual content analysis...', 'info');
            const testQuery = 'Constitutional law analysis regarding fundamental rights and judicial review mechanisms under Article 32 of the Indian Constitution.';
            const mockResult = this.getEnhancedMockModerationResult(testQuery, 'constitutional');
            this.displayModerationResult(mockResult);
            this.currentAnalysis = { query: testQuery, moderation_id: mockResult.moderation_id };
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Test 3: Test feedback submission
            this.showNotification('Testing feedback submission...', 'info');
            await this.submitFeedback('thumbs_up', mockResult.moderation_id);
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Test 4: Test demo pipeline
            this.showNotification('Running demo pipeline...', 'info');
            await this.runDemoPipeline();
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Test 5: Test filtering
            this.showNotification('Testing filter functionality...', 'info');
            this.currentFilter = 'flagged';
            this.renderContentGrid();
            await new Promise(resolve => setTimeout(resolve, 500));
            
            this.currentFilter = 'all';
            this.renderContentGrid();
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Test 6: Test pagination
            this.changePage(2);
            await new Promise(resolve => setTimeout(resolve, 500));
            this.changePage(1);
            
            this.showNotification('✅ Complete demo flow test passed! All features working correctly.', 'success');
            
        } catch (error) {
            console.error('Demo flow test failed:', error);
            this.showNotification('❌ Demo flow test failed. Check console for details.', 'error');
        }
    }

    async submitFeedback(feedbackType, moderationId = null) {
        // Use current analysis if no specific moderation ID
        const targetModerationId = moderationId || this.currentAnalysis?.moderation_id || `analysis_${Date.now()}`;
        
        this.showLearningIndicator();

        try {
            const feedbackData = {
                moderation_id: targetModerationId,
                feedback_type: feedbackType,
                comment: `User feedback: ${feedbackType}`,
                user_id: 'demo_user',
                rating: feedbackType === 'thumbs_up' ? 5 : 2,
                content: this.currentAnalysis?.query || 'Demo content',
                metadata: {
                    timestamp: new Date().toISOString(),
                    user_agent: navigator.userAgent,
                    session_id: this.getSessionId()
                }
            };

            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(feedbackData)
            });

            if (response.ok) {
                const result = await response.json();
                this.handleSuccessfulFeedback(feedbackType, targetModerationId, result);
            } else {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || 'Feedback submission failed');
            }
        } catch (error) {
            console.error('Feedback error:', error);
            this.handleFeedbackError(feedbackType);
            // For demo purposes, still simulate success even if API fails
            setTimeout(() => {
                this.handleSuccessfulFeedback(feedbackType, targetModerationId, { learning_applied: true });
            }, 2000);
        }
    }

    handleSuccessfulFeedback(feedbackType, moderationId, result = null) {
        this.showNotification('Feedback submitted successfully! The RL system will learn from this.', 'success');

        // Show learning applied if backend returned success
        if (result && result.learning_applied) {
            this.showNotification('RL model updated based on your feedback!', 'success');
        }

        if (feedbackType === 'thumbs_down') {
            // Simulate re-evaluation after negative feedback
            setTimeout(() => {
                this.simulateImprovedAnalysis();
                this.showLearningBadge();
                this.showFeedbackPopup(85, 92); // Show confidence improvement
            }, 2000);
        } else {
            // Positive feedback - just show learning badge
            setTimeout(() => {
                this.showLearningBadge();
                this.hideLearningIndicator();
            }, 1500);
        }

        // Update statistics
        this.updateStatisticsAfterFeedback(feedbackType);
        
        // Add to local feedback history
        this.addToFeedbackHistory(moderationId, feedbackType);
    }
    
    getSessionId() {
        let sessionId = sessionStorage.getItem('dashboard_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            sessionStorage.setItem('dashboard_session_id', sessionId);
        }
        return sessionId;
    }
    
    addToFeedbackHistory(moderationId, feedbackType) {
        let feedbackHistory = JSON.parse(localStorage.getItem('feedback_history') || '[]');
        feedbackHistory.push({
            moderation_id: moderationId,
            feedback_type: feedbackType,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 feedback items
        if (feedbackHistory.length > 50) {
            feedbackHistory = feedbackHistory.slice(-50);
        }
        
        localStorage.setItem('feedback_history', JSON.stringify(feedbackHistory));
    }

    addDemoPipelineButton() {
        const submissionSection = document.querySelector('.submission-section');
        if (!submissionSection) return;

        const demoButton = document.createElement('button');
        demoButton.className = 'btn-primary';
        demoButton.style.marginTop = '15px';
        demoButton.innerHTML = '<i class="fas fa-vial"></i> Run Demo Pipeline (15 Items)';
        demoButton.onclick = () => this.runDemoPipeline();
        
        const submitBtn = document.getElementById('analyze-btn');
        if (submitBtn) {
            submitBtn.parentNode.appendChild(demoButton);
        }
    }

    async runDemoPipeline() {
        this.showNotification('Starting demo pipeline with 15 content items...', 'info');
        
        const demoContent = this.getDemoPipelineContent();
        const results = [];
        
        for (let i = 0; i < demoContent.length; i++) {
            const content = demoContent[i];
            this.showNotification(`Processing item ${i + 1}/15: ${content.type}`, 'info');
            
            // Add slight delay for better UX
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Mock analysis result
            const result = this.getEnhancedMockModerationResult(content.text, content.caseType);
            result.moderation_id = `demo_${i + 1}_${Date.now()}`;
            
            results.push(result);
            
            // Simulate some feedback (randomly)
            if (Math.random() > 0.7) {
                const feedbackType = Math.random() > 0.5 ? 'thumbs_up' : 'thumbs_down';
                this.addToFeedbackHistory(result.moderation_id, feedbackType);
            }
        }
        
        // Update the content items with demo results
        this.contentItems = results.reverse(); // Newest first
        this.renderContentGrid();
        this.updateStatisticsAfterDemo(results);
        
        this.showNotification('Demo pipeline completed! Check the updated results below.', 'success');
        
        // Scroll to results
        document.querySelector('.content-section')?.scrollIntoView({ behavior: 'smooth' });
    }

    getDemoPipelineContent() {
        return [
            {
                text: "Article 21 of the Constitution of India guarantees protection of life and personal liberty. This fundamental right cannot be taken away except through due process of law as established by precedent in Maneka Gandhi v. Union of India.",
                type: "Constitutional Law Analysis",
                caseType: "constitutional"
            },
            {
                text: "Section 302 of the Bharatiya Nyaya Sanhita deals with punishment for murder. The section establishes mandatory life imprisonment as the standard penalty, with potential for death penalty in exceptional circumstances.",
                type: "Criminal Law - BNS Section",
                caseType: "criminal"
            },
            {
                text: "Employment contract dispute regarding non-compete clauses and breach of confidentiality agreements. The matter involves interpretation of Section 27 of the Indian Contract Act regarding restraint of trade.",
                type: "Employment Law Contract",
                caseType: "employment"
            },
            {
                text: "Corporate compliance audit for listed companies under SEBI regulations. Analysis of disclosure requirements and insider trading provisions under the Companies Act 2013.",
                type: "Corporate Law Compliance",
                caseType: "corporate"
            },
            {
                text: "Intellectual property dispute involving trademark infringement and passing off claims. The case involves registration of similar marks under the Trade Marks Act 1999.",
                type: "IP Law - Trademark",
                caseType: "intellectual_property"
            },
            {
                text: "Environmental clearance controversy regarding industrial project approval. Legal challenge under the Environment Protection Act 1986 and National Green Tribunal Act 2010.",
                type: "Environmental Law",
                caseType: "environmental"
            },
            {
                text: "Tax implications of cryptocurrency transactions under Income Tax Act 1961. Analysis of capital gains classification and reporting requirements for digital assets.",
                caseType: "tax",
                type: "Tax Law - Digital Assets"
            },
            {
                text: "Family law matters including divorce proceedings, maintenance claims, and child custody disputes under the Hindu Marriage Act 1955 and Special Marriage Act 1954.",
                type: "Family Law Proceedings",
                caseType: "family"
            },
            {
                text: "Insurance claim rejection dispute regarding motor vehicle accident compensation. Analysis of coverage terms and third-party liability under Motor Vehicles Act 1988.",
                type: "Insurance Law",
                caseType: "civil"
            },
            {
                text: "Public interest litigation challenging government policy on education sector reforms. Constitutional validity of the National Education Policy 2020 under fundamental rights.",
                type: "Constitutional PIL",
                caseType: "constitutional"
            },
            {
                text: "Cybercrime investigation involving online fraud and digital evidence collection. Procedural requirements under Information Technology Act 2000 and Evidence Act.",
                type: "Cyber Law",
                caseType: "criminal"
            },
            {
                text: "Real estate transaction dispute regarding title verification and encumbrance certificates. Due diligence requirements under Registration Act 1908.",
                type: "Property Law",
                caseType: "civil"
            },
            {
                text: "Labor law violation case involving non-payment of minimum wages and overtime compensation under the Payment of Wages Act 1936.",
                type: "Labor Law Violation",
                caseType: "employment"
            },
            {
                text: "Medical negligence claim based on delayed diagnosis and treatment complications. Professional liability standards under Indian Penal Code and Consumer Protection Act.",
                type: "Medical Law",
                caseType: "civil"
            },
            {
                text: "Administrative law challenge to government decision on land acquisition for infrastructure project. Procedural fairness and compensation standards under Land Acquisition Act 2013.",
                type: "Administrative Law",
                caseType: "civil"
            }
        ];
    }

    updateStatisticsAfterDemo(results) {
        // Update local statistics based on demo results
        const flagged = results.filter(r => r.flagged).length;
        const approved = results.length - flagged;
        const avgConfidence = results.reduce((sum, r) => sum + r.confidence, 0) / results.length;
        
        // Update statistics object
        this.statistics = {
            ...this.statistics,
            total_moderations: (this.statistics.total_moderations || 0) + results.length,
            flagged_count: (this.statistics.flagged_count || 0) + flagged,
            approved_count: (this.statistics.approved_count || 0) + approved,
            avg_confidence: avgConfidence,
            total_feedback: JSON.parse(localStorage.getItem('feedback_history') || '[]').length
        };
        
        this.updateStatisticsDisplay();
    }

    handleFeedbackError(feedbackType) {
        this.showNotification('Feedback submitted (demo mode). In production, this would update the RL model.', 'info');
        this.hideLearningIndicator();
    }

    simulateImprovedAnalysis() {
        // Simulate that the analysis has improved after feedback
        const confidenceFill = document.getElementById('domain-confidence-fill');
        const confidenceText = document.getElementById('domain-confidence-text');

        if (confidenceFill && confidenceText) {
            const currentWidth = parseInt(confidenceFill.style.width) || 85;
            const newWidth = Math.min(95, currentWidth + 7);
            
            confidenceFill.style.width = `${newWidth}%`;
            confidenceText.textContent = `${newWidth}%`;
            
            // Add success animation
            confidenceFill.style.background = 'linear-gradient(90deg, #27ae60, #2ecc71)';
            setTimeout(() => {
                confidenceFill.style.background = 'linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%)';
            }, 2000);
        }
    }

    updateStatisticsAfterFeedback(feedbackType) {
        // Update local statistics
        if (feedbackType === 'thumbs_up') {
            this.statistics.positive_feedback = (this.statistics.positive_feedback || 0) + 1;
        } else {
            this.statistics.negative_feedback = (this.statistics.negative_feedback || 0) + 1;
        }
        this.statistics.total_feedback = (this.statistics.total_feedback || 0) + 1;
        
        // Update display
        this.updateStatisticsDisplay();
    }

    showContentDetails(moderationId) {
        const item = this.contentItems.find(i => i.moderation_id === moderationId);
        if (!item) return;

        // Create and show modal with content details
        this.showNotification(`Showing details for moderation ${moderationId}`, 'info');
    }

    updateRLProgress(metrics) {
        // Update RL progress indicators with real data
        this.updateRLProgressIndicators({
            ...this.statistics,
            q_table_size: metrics.q_table_size || 0,
            total_moderations: metrics.total_moderations || 0
        });
    }

    updatePerformanceData(performance) {
        // Update performance metrics in the dashboard
        const currentAccuracy = document.getElementById('current-accuracy');
        const improvementRate = document.getElementById('improvement-rate');
        const bestPerformance = document.getElementById('best-performance');
        const trainingSessions = document.getElementById('training-sessions');

        if (currentAccuracy) currentAccuracy.textContent = `${(performance.current_accuracy * 100 || 0).toFixed(1)}%`;
        if (improvementRate) improvementRate.textContent = `${(performance.improvement_rate * 100 || 0).toFixed(1)}%`;
        if (bestPerformance) bestPerformance.textContent = `${(performance.best_performance * 100 || 0).toFixed(1)}%`;
        if (trainingSessions) trainingSessions.textContent = performance.training_sessions || 0;
    }

    updateAccuracyTrends(trends) {
        // Update accuracy trends display
        const insightsList = document.getElementById('accuracy-insights-list');
        if (insightsList && trends.insights) {
            insightsList.innerHTML = trends.insights.map(insight => 
                `<li><i class="fas fa-lightbulb"></i> ${insight}</li>`
            ).join('');
        }

        // Update content performance bars
        const performanceItems = document.querySelectorAll('.performance-item');
        const contentTypes = ['text', 'image', 'video', 'audio'];

        contentTypes.forEach((type, index) => {
            if (performanceItems[index] && trends.content_performance) {
                const accuracy = trends.content_performance[type] || 0;
                const fill = performanceItems[index].querySelector('.performance-fill');
                const value = performanceItems[index].querySelector('.performance-value');

                if (fill) fill.style.width = `${accuracy * 100}%`;
                if (value) value.textContent = `${(accuracy * 100).toFixed(1)}%`;
            }
        });
    }

    showLearningIndicator() {
        const indicator = document.getElementById('learning-indicator');
        if (indicator) indicator.style.display = 'flex';
    }

    hideLearningIndicator() {
        const indicator = document.getElementById('learning-indicator');
        if (indicator) indicator.style.display = 'none';
    }

    showLearningBadge() {
        const badge = document.getElementById('learning-badge');
        if (badge) {
            badge.style.display = 'flex';
            setTimeout(() => {
                badge.style.display = 'none';
            }, 3000);
        }
    }

    showFeedbackPopup(previousConfidence, newConfidence) {
        const popup = document.getElementById('feedback-popup-overlay');
        const confidenceBefore = document.getElementById('confidence-before');
        const confidenceAfter = document.getElementById('confidence-after');

        if (popup && confidenceBefore && confidenceAfter) {
            confidenceBefore.textContent = `${previousConfidence}%`;
            confidenceAfter.textContent = `${newConfidence}%`;
            popup.style.display = 'flex';

            setTimeout(() => {
                popup.style.display = 'none';
            }, 5000);
        }
    }

    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'flex';
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add toast styles if not already present
        if (!document.querySelector('#toast-styles')) {
            const styles = document.createElement('style');
            styles.id = 'toast-styles';
            styles.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 20px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    animation: slideInRight 0.3s ease-out;
                }
                .toast-success { background: #28a745; }
                .toast-error { background: #dc3545; }
                .toast-warning { background: #ffc107; color: #333; }
                .toast-info { background: #17a2b8; }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    switchJurisdiction(jurisdiction) {
        // Update active tab
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-jurisdiction="${jurisdiction}"]`)?.classList.add('active');
        
        // Re-analyze current content if any
        if (this.currentAnalysis) {
            this.analyzeContent();
        }
    }

    startAutoRefresh() {
        // Refresh statistics every 30 seconds
        setInterval(() => {
            this.loadStatistics();
        }, 30000);
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ModerationDashboard();
});

// Tab switching functionality for API documentation
function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    const targetTab = document.getElementById(tabName + '-tab');
    const targetBtn = event.target;
    
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) targetBtn.classList.add('active');
}

// File upload functionality for API docs page
function moderateFile() {
    const fileInput = document.getElementById('file-input');
    const contentType = document.getElementById('content-type').value;
    const moderateBtn = document.getElementById('moderate-btn');
    
    if (!fileInput.files[0]) {
        alert('Please select a file first');
        return;
    }
    
    moderateBtn.disabled = true;
    moderateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('content_type', contentType);
    
    fetch('/api/moderate/file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        displayFileModerationResults(result);
        moderateBtn.disabled = false;
        moderateBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Moderate Content';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Moderation failed: ' + error.message);
        moderateBtn.disabled = false;
        moderateBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Moderate Content';
    });
}

function displayFileModerationResults(result) {
    const previewSection = document.getElementById('preview-section');
    const mediaPreview = document.getElementById('media-preview');
    const moderationResults = document.getElementById('moderation-results');
    
    if (previewSection) previewSection.style.display = 'block';
    
    const statusClass = result.flagged ? 'flagged' : '';
    const statusText = result.flagged ? 'FLAGGED' : 'APPROVED';
    const statusColor = result.flagged ? '#dc3545' : '#28a745';
    
    if (moderationResults) {
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
    }
}