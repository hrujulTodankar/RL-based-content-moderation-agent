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





/**
 * Hrujul's Legal AI System - Frontend JavaScript
 * Multi-Jurisdiction Legal Intelligence with Reinforcement Learning
 */

// Global state management
class LegalAIState {
    constructor() {
        this.currentJurisdiction = 'IN';
        this.currentCountry = 'India';
        this.analysisResults = null;
        this.queryId = null;
        this.isAnalyzing = false;
    }

    setJurisdiction(jurisdiction, country) {
        this.currentJurisdiction = jurisdiction;
        this.currentCountry = country;
        this.updateJurisdictionDisplay();
    }

    updateJurisdictionDisplay() {
        const currentCountryElement = document.getElementById('current-country');
        if (currentCountryElement) {
            currentCountryElement.textContent = this.currentCountry;
        }
    }

    setAnalysisResults(results) {
        this.analysisResults = results;
        this.queryId = results.queryId || this.generateQueryId();
    }

    generateQueryId() {
        return '#' + Math.random().toString(36).substr(2, 9).toUpperCase();
    }
}

// API Service for backend communication
class LegalAIService {
    constructor() {
        this.baseUrl = '/api';
        this.timeout = 30000; // 30 seconds
    }

    async makeRequest(endpoint, data, method = 'POST') {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: method === 'POST' ? JSON.stringify(data) : null,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please try again');
            }
            throw error;
        }
    }

    async classifyQuery(query, jurisdiction) {
        return this.makeRequest('/classify', {
            text: query,
            domain_hints: []
        });
    }

    async getLegalRoute(caseDescription, caseType, jurisdiction) {
        return this.makeRequest('/legal-route', {
            case_description: caseDescription,
            case_type: caseType,
            jurisdiction: jurisdiction,
            urgency_level: 'normal'
        });
    }

    async searchConstitution(query, jurisdiction) {
        return this.makeRequest('/constitution', {
            query: query,
            jurisdiction: jurisdiction
        });
    }

    async generateTimeline(caseId, caseType, jurisdiction) {
        return this.makeRequest('/timeline', {
            case_id: caseId,
            case_type: caseType,
            jurisdiction: jurisdiction,
            priority: 'medium',
            case_severity: 'moderate'
        });
    }

    async predictSuccessRate(caseType, jurisdiction) {
        return this.makeRequest('/success-rate', {
            case_type: caseType,
            jurisdiction: jurisdiction,
            court_level: 'district',
            case_complexity: 'medium',
            lawyer_experience: 'medium'
        });
    }

    async submitFeedback(queryId, rating, jurisdiction) {
        return this.makeRequest('/feedback', {
            query_id: queryId,
            rating: rating,
            jurisdiction: jurisdiction,
            timestamp: new Date().toISOString()
        });
    }

    async getJurisdictionInfo(jurisdiction) {
        return this.makeRequest(`/jurisdiction/${jurisdiction}`, {}, 'GET');
    }
}

// UI Controller for managing interface interactions
class LegalAIController {
    constructor() {
        this.state = new LegalAIState();
        this.apiService = new LegalAIService();
        this.elements = {};
        this.initializeElements();
        this.bindEvents();
        this.initializeCharts();
    }

    initializeElements() {
        this.elements = {
            // Query input
            queryInput: document.getElementById('legal-query'),
            charCount: document.getElementById('char-count'),
            analyzeBtn: document.getElementById('analyze-btn'),
            clearBtn: document.getElementById('clear-btn'),
            
            // Jurisdiction
            jurisdictionTabs: document.querySelectorAll('.jurisdiction-tab'),
            
            // Results
            resultsSection: document.getElementById('results-section'),
            errorSection: document.getElementById('error-section'),
            retryBtn: document.getElementById('retry-btn'),
            
            // Analysis meta
            analysisTime: document.getElementById('analysis-time'),
            queryId: document.getElementById('query-id'),
            overallConfidence: document.getElementById('overall-confidence'),
            confidenceScore: document.getElementById('confidence-score'),
            
            // Domain classification
            primaryDomain: document.getElementById('primary-domain'),
            domainConfidence: document.getElementById('domain-confidence'),
            domainConfidenceText: document.getElementById('domain-confidence-text'),
            secondaryDomains: document.getElementById('secondary-domains'),
            
            // Legal route
            recommendedRoute: document.getElementById('recommended-route'),
            courtHierarchy: document.getElementById('court-hierarchy'),
            estimatedTimeline: document.getElementById('estimated-timeline'),
            successProbability: document.getElementById('success-probability'),
            requiredDocuments: document.getElementById('required-documents'),
            
            // Constitution
            articlesCount: document.getElementById('articles-count'),
            articlesList: document.getElementById('articles-list'),
            interpretation: document.getElementById('interpretation'),
            
            // Timeline
            timelineStatus: document.getElementById('timeline-status'),
            timelineEvents: document.getElementById('timeline-events'),
            criticalDeadlines: document.getElementById('critical-deadlines'),
            nextActions: document.getElementById('next-actions'),
            
            // Success rate
            predictionConfidence: document.getElementById('prediction-confidence'),
            successPercentage: document.getElementById('success-percentage'),
            confidenceInterval: document.getElementById('confidence-interval'),
            factorsInfluencing: document.getElementById('factors-influencing'),
            recommendations: document.getElementById('recommendations'),
            
            // Feedback
            feedbackButtons: document.querySelectorAll('.feedback-btn'),
            feedbackLearning: document.getElementById('feedback-learning'),
            learningStatus: document.getElementById('learning-status')
        };
    }

    bindEvents() {
        // Query input events
        this.elements.queryInput.addEventListener('input', this.handleQueryInput.bind(this));
        this.elements.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.analyzeQuery();
            }
        });

        // Button events
        this.elements.analyzeBtn.addEventListener('click', this.analyzeQuery.bind(this));
        this.elements.clearBtn.addEventListener('click', this.clearQuery.bind(this));
        this.elements.retryBtn.addEventListener('click', this.analyzeQuery.bind(this));

        // Jurisdiction switching
        this.elements.jurisdictionTabs.forEach(tab => {
            tab.addEventListener('click', this.handleJurisdictionChange.bind(this));
        });

        // Feedback events
        this.elements.feedbackButtons.forEach(btn => {
            btn.addEventListener('click', this.handleFeedback.bind(this));
        });
    }

    initializeCharts() {
        // Initialize success rate circle chart
        this.initializeSuccessCircle();
    }

    initializeSuccessCircle() {
        const canvas = document.getElementById('success-circle');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 50;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw background circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = '#e9ecef';
        ctx.lineWidth = 8;
        ctx.stroke();

        // This will be updated when results are displayed
        this.successCircleCtx = ctx;
        this.successCircleData = {
            centerX, centerY, radius
        };
    }

    handleQueryInput() {
        const query = this.elements.queryInput.value;
        const charCount = query.length;
        
        // Update character count
        this.elements.charCount.textContent = charCount;
        
        // Enable/disable analyze button
        this.elements.analyzeBtn.disabled = charCount === 0 || charCount > 1000;
        
        // Visual feedback for character limit
        const inputStats = this.elements.queryInput.parentNode.querySelector('.input-stats');
        if (charCount > 900) {
            inputStats.style.color = '#dc3545';
        } else {
            inputStats.style.color = '#6c757d';
        }
    }

    handleJurisdictionChange(e) {
        const tab = e.currentTarget;
        const jurisdiction = tab.dataset.jurisdiction;
        const country = tab.dataset.country;

        // Update active tab
        this.elements.jurisdictionTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update state
        this.state.setJurisdiction(jurisdiction, country);

        // Clear results if jurisdiction changes
        if (this.state.analysisResults) {
            this.hideResults();
        }
    }

    async analyzeQuery() {
        if (this.state.isAnalyzing) return;

        const query = this.elements.queryInput.value.trim();
        if (!query) {
            this.showError('Please enter a legal query to analyze.');
            return;
        }

        if (query.length > 1000) {
            this.showError('Query is too long. Please limit to 1000 characters.');
            return;
        }

        this.state.isAnalyzing = true;
        this.showLoading();
        this.hideError();

        try {
            // Generate query ID
            this.state.queryId = this.state.generateQueryId();
            
            // Run all analyses in parallel
            const analyses = await Promise.allSettled([
                this.apiService.classifyQuery(query, this.state.currentJurisdiction),
                this.apiService.getLegalRoute(query, 'general', this.state.currentJurisdiction),
                this.apiService.searchConstitution(query, this.state.currentJurisdiction),
                this.apiService.generateTimeline(this.state.queryId, 'general', this.state.currentJurisdiction),
                this.apiService.predictSuccessRate('general', this.state.currentJurisdiction)
            ]);

            // Check if any analysis failed
            const failures = analyses.filter(result => result.status === 'rejected');
            if (failures.length > 0) {
                console.error('Some analyses failed:', failures);
                // Continue with partial results rather than failing completely
            }

            // Combine results
            const results = {
                queryId: this.state.queryId,
                query: query,
                jurisdiction: this.state.currentJurisdiction,
                timestamp: new Date().toISOString(),
                classification: analyses[0].status === 'fulfilled' ? analyses[0].value : null,
                legalRoute: analyses[1].status === 'fulfilled' ? analyses[1].value : null,
                constitution: analyses[2].status === 'fulfilled' ? analyses[2].value : null,
                timeline: analyses[3].status === 'fulfilled' ? analyses[3].value : null,
                successRate: analyses[4].status === 'fulfilled' ? analyses[4].value : null
            };

            this.state.setAnalysisResults(results);
            this.displayResults(results);
            this.showResults();

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.state.isAnalyzing = false;
            this.hideLoading();
        }
    }

    displayResults(results) {
        // Update analysis meta
        this.elements.analysisTime.textContent = 'Just now';
        this.elements.queryId.textContent = results.queryId;

        // Calculate overall confidence
        const confidences = [];
        if (results.classification?.confidence) confidences.push(results.classification.confidence);
        if (results.legalRoute?.success_probability) confidences.push(results.legalRoute.success_probability);
        if (results.successRate?.overall_success_rate) confidences.push(results.successRate.overall_success_rate);

        const avgConfidence = confidences.length > 0 
            ? confidences.reduce((a, b) => a + b, 0) / confidences.length 
            : 0.75;

        this.elements.confidenceScore.textContent = `${Math.round(avgConfidence * 100)}%`;

        // Display individual sections
        this.displayDomainClassification(results.classification);
        this.displayLegalRoute(results.legalRoute);
        this.displayConstitution(results.constitution);
        this.displayTimeline(results.timeline);
        this.displaySuccessRate(results.successRate);

        // Add fade-in animation
        this.elements.resultsSection.classList.add('fade-in');
    }

    displayDomainClassification(classification) {
        if (!classification) return;

        // Primary domain
        this.elements.primaryDomain.textContent = classification.primary_domain;
        this.elements.domainConfidence.style.width = `${classification.confidence * 100}%`;
        this.elements.domainConfidenceText.textContent = `${Math.round(classification.confidence * 100)}%`;

        // Secondary domains
        this.elements.secondaryDomains.innerHTML = '';
        classification.secondary_domains?.forEach(domain => {
            const domainElement = document.createElement('div');
            domainElement.className = 'secondary-domain';
            domainElement.innerHTML = `
                <strong>${domain.domain}</strong> (${Math.round(domain.confidence * 100)}%)
            `;
            this.elements.secondaryDomains.appendChild(domainElement);
        });
    }

    displayLegalRoute(legalRoute) {
        if (!legalRoute) return;

        // Recommended route
        this.elements.recommendedRoute.textContent = legalRoute.recommended_route;
        this.elements.estimatedTimeline.textContent = legalRoute.estimated_timeline;
        this.elements.successProbability.textContent = `${Math.round(legalRoute.success_probability * 100)}%`;

        // Court hierarchy
        this.elements.courtHierarchy.innerHTML = '';
        legalRoute.court_hierarchy?.forEach(court => {
            const courtElement = document.createElement('div');
            courtElement.className = `court-level ${court.recommended ? 'recommended' : ''}`;
            courtElement.innerHTML = `
                <div class="court-info">
                    <div class="court-name">${court.court}</div>
                    <div class="court-timeline">Timeline: ${court.timeline}</div>
                    <div class="court-success">Success Rate: ${Math.round(court.success_rate * 100)}%</div>
                </div>
            `;
            this.elements.courtHierarchy.appendChild(courtElement);
        });

        // Required documents
        this.elements.requiredDocuments.innerHTML = '';
        legalRoute.required_documents?.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.className = 'document-item';
            docElement.innerHTML = `
                <i class="fas fa-file-alt"></i>
                <span>${doc}</span>
            `;
            this.elements.requiredDocuments.appendChild(docElement);
        });
    }

    displayConstitution(constitution) {
        if (!constitution) return;

        // Articles count
        const articleCount = constitution.articles?.length || 0;
        this.elements.articlesCount.textContent = `${articleCount} Article${articleCount !== 1 ? 's' : ''}`;

        // Articles list
        this.elements.articlesList.innerHTML = '';
        constitution.articles?.forEach(article => {
            const articleElement = document.createElement('div');
            articleElement.className = 'article-item';
            articleElement.innerHTML = `
                <div class="article-header">
                    <div class="article-number">Article ${article.number}</div>
                </div>
                <div class="article-title">${article.title}</div>
                <div class="article-content">${article.content}</div>
            `;
            this.elements.articlesList.appendChild(articleElement);
        });

        // Interpretation
        if (constitution.interpretation) {
            this.elements.interpretation.innerHTML = `
                <h4><i class="fas fa-lightbulb"></i> Legal Interpretation</h4>
                <p>${constitution.interpretation}</p>
            `;
        }
    }

    displayTimeline(timeline) {
        if (!timeline) return;

        // Timeline events
        this.elements.timelineEvents.innerHTML = '';
        timeline.timeline_events?.forEach((event, index) => {
            const eventElement = document.createElement('div');
            eventElement.className = 'timeline-event';
            eventElement.innerHTML = `
                <div class="timeline-marker">${index + 1}</div>
                <div class="timeline-content">
                    <div class="event-stage">${event.stage}</div>
                    <div class="event-date">${event.date}</div>
                    <div class="event-description">${event.description}</div>
                    <div class="event-duration">Duration: ${event.duration_days} days</div>
                </div>
            `;
            this.elements.timelineEvents.appendChild(eventElement);
        });

        // Critical deadlines
        this.elements.criticalDeadlines.innerHTML = '<h4><i class="fas fa-exclamation-triangle"></i> Critical Deadlines</h4>';
        timeline.critical_deadlines?.forEach(deadline => {
            const deadlineElement = document.createElement('div');
            deadlineElement.className = 'deadline-item';
            deadlineElement.innerHTML = `
                <div class="deadline-info">
                    <div class="deadline-event">${deadline.event}</div>
                    <div class="deadline-date">Due: ${deadline.date} (${deadline.days_from_start} days from start)</div>
                </div>
            `;
            this.elements.criticalDeadlines.appendChild(deadlineElement);
        });

        // Next actions
        this.elements.nextActions.innerHTML = '<h4><i class="fas fa-tasks"></i> Recommended Next Actions</h4>';
        timeline.next_actions?.forEach(action => {
            const actionElement = document.createElement('div');
            actionElement.className = 'action-item';
            actionElement.innerHTML = `
                <div class="action-info">
                    <div class="action-name">${action.action}</div>
                    <div class="action-timeline">Timeline: ${action.timeline}</div>
                </div>
                <div class="action-priority ${action.priority}">${action.priority.toUpperCase()}</div>
            `;
            this.elements.nextActions.appendChild(actionElement);
        });
    }

    displaySuccessRate(successRate) {
        if (!successRate) return;

        // Main percentage
        const percentage = Math.round(successRate.overall_success_rate * 100);
        this.elements.successPercentage.textContent = `${percentage}%`;

        // Update circle chart
        this.updateSuccessCircle(percentage);

        // Confidence interval
        const lower = Math.round(successRate.confidence_interval.lower * 100);
        const upper = Math.round(successRate.confidence_interval.upper * 100);
        this.elements.confidenceInterval.textContent = `${lower}% - ${upper}%`;

        // Factors influencing
        this.elements.factorsInfluencing.innerHTML = '';
        successRate.factors_influencing?.forEach(factor => {
            const factorElement = document.createElement('div');
            factorElement.className = 'factor-item';
            factorElement.innerHTML = `
                <div class="factor-name">
                    ${factor.factor}
                    <span class="factor-impact ${factor.impact}">${factor.impact}</span>
                </div>
                <div class="factor-description">${factor.description}</div>
            `;
            this.elements.factorsInfluencing.appendChild(factorElement);
        });

        // Recommendations
        this.elements.recommendations.innerHTML = '<h4><i class="fas fa-lightbulb"></i> Recommendations</h4>';
        successRate.recommendations?.forEach(rec => {
            const recElement = document.createElement('div');
            recElement.className = 'recommendation-item';
            recElement.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>${rec}</span>
            `;
            this.elements.recommendations.appendChild(recElement);
        });
    }

    updateSuccessCircle(percentage) {
        if (!this.successCircleCtx) return;

        const { centerX, centerY, radius } = this.successCircleData;
        const ctx = this.successCircleCtx;
        const startAngle = -Math.PI / 2;
        const endAngle = startAngle + (percentage / 100) * 2 * Math.PI;

        // Clear previous arc
        ctx.clearRect(centerX - radius - 10, centerY - radius - 10, 
                     (radius + 10) * 2, (radius + 10) * 2);

        // Draw progress arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.strokeStyle = percentage >= 70 ? '#28a745' : percentage >= 50 ? '#ffc107' : '#dc3545';
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();

        // Add percentage text (handled by HTML element)
    }

    async handleFeedback(e) {
        const button = e.currentTarget;
        const rating = button.dataset.rating;

        // Disable all feedback buttons
        this.elements.feedbackButtons.forEach(btn => btn.disabled = true);

        // Show learning indicator
        this.elements.feedbackLearning.style.display = 'block';
        this.elements.learningStatus.textContent = 'System Learning...';

        try {
            await this.apiService.submitFeedback(
                this.state.queryId,
                rating,
                this.state.currentJurisdiction
            );

            // Update learning status
            this.elements.learningStatus.textContent = 'Learning Complete';
            
            // Update button appearance
            button.style.background = rating === 'positive' ? '#28a745' : 
                                    rating === 'neutral' ? '#ffc107' : '#dc3545';
            button.style.color = 'white';

        } catch (error) {
            console.error('Feedback submission error:', error);
            this.elements.learningStatus.textContent = 'Learning Failed';
            
            // Re-enable buttons on error
            this.elements.feedbackButtons.forEach(btn => btn.disabled = false);
        }

        // Hide learning indicator after 3 seconds
        setTimeout(() => {
            this.elements.feedbackLearning.style.display = 'none';
        }, 3000);
    }

    clearQuery() {
        this.elements.queryInput.value = '';
        this.handleQueryInput(); // Trigger input handler to update UI
        this.hideResults();
        this.hideError();
    }

    showLoading() {
        this.elements.analyzeBtn.disabled = true;
        this.elements.analyzeBtn.querySelector('span').textContent = 'Analyzing...';
        this.elements.analyzeBtn.querySelector('.loading-spinner').style.display = 'inline-block';
    }

    hideLoading() {
        this.elements.analyzeBtn.disabled = false;
        this.elements.analyzeBtn.querySelector('span').textContent = 'Analyze Legal Query';
        this.elements.analyzeBtn.querySelector('.loading-spinner').style.display = 'none';
    }

    showResults() {
        this.elements.resultsSection.style.display = 'block';
        this.hideError();
        
        // Scroll to results
        this.elements.resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideResults() {
        this.elements.resultsSection.style.display = 'none';
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        this.elements.errorSection.style.display = 'block';
        this.hideResults();
        
        // Scroll to error
        this.elements.errorSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideError() {
        this.elements.errorSection.style.display = 'none';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Hrujul\'s Legal AI System...');
    
    // Initialize the main controller
    window.legalAIController = new LegalAIController();
    
    // Set up periodic updates for timestamps
    setInterval(() => {
        const analysisTime = document.getElementById('analysis-time');
        if (analysisTime && window.legalAIController.state.analysisResults) {
            // Update timestamp to show actual time elapsed
            const now = new Date();
            const analyzed = new Date(window.legalAIController.state.analysisResults.timestamp);
            const diffMs = now - analyzed;
            const diffMins = Math.floor(diffMs / 60000);
            
            if (diffMins < 1) {
                analysisTime.textContent = 'Just now';
            } else if (diffMins < 60) {
                analysisTime.textContent = `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
            } else {
                const diffHours = Math.floor(diffMins / 60);
                analysisTime.textContent = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
            }
        }
    }, 60000); // Update every minute

    console.log('✅ Legal AI System initialized successfully');
    
    // Add some sample queries for demonstration
    const sampleQueries = [
        "What are my legal rights if I'm accused of theft?",
        "How do I file for divorce when there's property dispute?",
        "What are the requirements for starting a business in Dubai?",
        "Can I challenge a parking fine in the UK?",
        "What are my rights during police arrest in India?",
        "How do I register a trademark in UAE?",
        "What constitutes fair dismissal in UK employment law?"
    ];
    
    // Add sample query suggestions on hover
    const queryInput = document.getElementById('legal-query');
    if (queryInput) {
        let suggestionIndex = 0;
        let suggestionInterval;
        
        queryInput.addEventListener('focus', () => {
            suggestionIndex = 0;
            suggestionInterval = setInterval(() => {
                if (queryInput.value === '') {
                    queryInput.placeholder = `Try: ${sampleQueries[suggestionIndex % sampleQueries.length]}`;
                    suggestionIndex++;
                }
            }, 3000);
        });
        
        queryInput.addEventListener('blur', () => {
            clearInterval(suggestionInterval);
            queryInput.placeholder = `Describe your legal situation, question, or case details...`;
        });
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LegalAIState, LegalAIService, LegalAIController };
}