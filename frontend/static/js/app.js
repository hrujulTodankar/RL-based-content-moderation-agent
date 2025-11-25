// RL Legal Content Moderation Agent JavaScript
class LegalAnalysisDashboard {
    constructor() {
        this.currentAnalysis = null;
        this.currentJurisdiction = this.loadCachedJurisdiction();
        this.previousConfidence = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setActiveTab(this.currentJurisdiction);
        this.bindPopupEvents();
    }

    bindEvents() {
        // Jurisdiction tabs
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const jurisdiction = e.target.closest('.tab-button').dataset.jurisdiction;
                this.switchJurisdiction(jurisdiction);
            });
        });

        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.analyzeContent();
        });

        // Feedback buttons
        document.getElementById('feedback-thumbs-up').addEventListener('click', () => {
            this.submitFeedback('thumbs_up');
        });

        document.getElementById('feedback-thumbs-down').addEventListener('click', () => {
            this.submitFeedback('thumbs_down');
        });

        // Enter key for query input
        document.getElementById('query-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.analyzeContent();
            }
        });
    }

    loadCachedJurisdiction() {
        return localStorage.getItem('selectedJurisdiction') || 'IN';
    }

    saveCachedJurisdiction(jurisdiction) {
        localStorage.setItem('selectedJurisdiction', jurisdiction);
    }

    setActiveTab(jurisdiction) {
        // Remove active class from all tabs
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active');
        });

        // Add active class to selected tab
        const activeTab = document.querySelector(`[data-jurisdiction="${jurisdiction}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
    }

    switchJurisdiction(jurisdiction) {
        if (this.currentJurisdiction === jurisdiction) return;

        this.currentJurisdiction = jurisdiction;
        this.saveCachedJurisdiction(jurisdiction);
        this.setActiveTab(jurisdiction);

        // If there's current analysis, re-run it with new jurisdiction
        if (this.currentAnalysis) {
            this.analyzeContent(true); // true indicates it's a jurisdiction switch
        }
    }

    async analyzeContent(isJurisdictionSwitch = false) {
        const query = document.getElementById('query-input').value.trim();
        const caseType = document.getElementById('case-type-select').value;

        if (!query && !isJurisdictionSwitch) {
            alert('Please enter a legal content query');
            return;
        }

        // If it's a jurisdiction switch and no query, just update the jurisdiction
        if (isJurisdictionSwitch && !query) {
            this.currentJurisdiction = this.currentJurisdiction;
            return;
        }

        this.showLoading();
        this.currentAnalysis = { query, jurisdiction: this.currentJurisdiction, caseType };

        try {
            // Make parallel API calls
            const promises = [
                this.fetchJurisdiction(this.currentJurisdiction),
                this.fetchLegalRoute(query, caseType, this.currentJurisdiction),
                this.fetchTimeline(query, caseType, this.currentJurisdiction),
                this.fetchSuccessRate(caseType, this.currentJurisdiction),
                this.fetchConstitution(query, this.currentJurisdiction)
            ];

            const results = await Promise.allSettled(promises);

            // Process results
            const [jurisdictionData, legalRouteData, timelineData, successRateData, constitutionData] = results.map(result =>
                result.status === 'fulfilled' ? result.value : null
            );

            // Render all blocks
            this.renderDomainBlock(jurisdictionData);
            this.renderLegalRouteBlock(legalRouteData);
            this.renderTimelineBlock(timelineData);
            this.renderSuccessRateBlock(successRateData);
            this.renderLawsBlock(jurisdictionData);
            this.renderConstitutionBlock(constitutionData);

            // Show response blocks and feedback section
            document.getElementById('response-blocks').style.display = 'grid';
            document.getElementById('feedback-section').style.display = 'block';

        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Failed to analyze content: ' + error.message, 'error');
        }

        this.hideLoading();
    }

    async fetchJurisdiction(jurisdiction) {
        const response = await fetch(`/api/jurisdiction/${jurisdiction}`);
        if (!response.ok) throw new Error('Failed to fetch jurisdiction data');
        return await response.json();
    }

    async fetchLegalRoute(query, caseType, jurisdiction) {
        const response = await fetch('/api/legal-route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                case_description: query,
                case_type: caseType,
                jurisdiction: jurisdiction
            })
        });
        if (!response.ok) throw new Error('Failed to fetch legal route');
        return await response.json();
    }

    async fetchTimeline(query, caseType, jurisdiction) {
        const response = await fetch('/api/timeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                case_id: `case_${Date.now()}`,
                case_type: caseType,
                jurisdiction: jurisdiction,
                start_date: new Date().toISOString()
            })
        });
        if (!response.ok) throw new Error('Failed to fetch timeline');
        return await response.json();
    }

    async fetchSuccessRate(caseType, jurisdiction) {
        const response = await fetch('/api/success-rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                case_type: caseType,
                jurisdiction: jurisdiction,
                court_level: 'district',
                case_complexity: 'medium',
                lawyer_experience: 'medium'
            })
        });
        if (!response.ok) throw new Error('Failed to fetch success rate');
        return await response.json();
    }

    async fetchConstitution(query, jurisdiction) {
        const response = await fetch('/api/constitution', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                jurisdiction: jurisdiction
            })
        });
        if (!response.ok) throw new Error('Failed to fetch constitution data');
        return await response.json();
    }

    renderDomainBlock(data) {
        const container = document.getElementById('domain-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load jurisdiction data</div>';
            return;
        }

        // Mock confidence for domain - in real implementation this would come from the API
        const confidence = 0.85;
        document.getElementById('domain-confidence-fill').style.width = `${confidence * 100}%`;
        document.getElementById('domain-confidence-text').textContent = `${(confidence * 100).toFixed(0)}%`;

        container.innerHTML = `
            <div class="jurisdiction-info">
                <div class="jurisdiction-header">
                    <h5>${data.country_name}</h5>
                    <span class="legal-system">${data.legal_system}</span>
                </div>
                <div class="key-laws">
                    <h6>Key Laws:</h6>
                    <div class="laws-list">
                        ${data.key_laws.slice(0, 3).map(law => `
                            <div class="law-item">
                                <strong>${law.name}</strong> (${law.year})
                                <p>${law.description}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderLegalRouteBlock(data) {
        const container = document.getElementById('legal-route-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load legal route</div>';
            return;
        }

        container.innerHTML = `
            <div class="legal-route-info">
                <div class="recommended-route">
                    <div class="route-badge recommended">
                        <i class="fas fa-route"></i> ${data.recommended_route}
                    </div>
                    <div class="route-details">
                        <div class="timeline-pill">${data.estimated_timeline}</div>
                        <div class="success-chip">${(data.success_probability * 100).toFixed(0)}% Success</div>
                    </div>
                </div>
                <div class="court-hierarchy">
                    <h6>Court Hierarchy:</h6>
                    <div class="hierarchy-list">
                        ${data.court_hierarchy.map(court => `
                            <div class="hierarchy-item ${court.recommended ? 'recommended' : ''}">
                                <span class="court-level">${court.level}</span>
                                <span class="court-name">${court.court}</span>
                                <span class="court-success">${(court.success_rate * 100).toFixed(0)}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderTimelineBlock(data) {
        const container = document.getElementById('timeline-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load timeline</div>';
            return;
        }

        container.innerHTML = `
            <div class="timeline-info">
                <div class="timeline-header">
                    <div class="completion-date">
                        <i class="fas fa-calendar-check"></i>
                        <span>Estimated Completion: ${data.estimated_completion}</span>
                    </div>
                </div>
                <div class="timeline-events">
                    ${data.timeline_events.map(event => `
                        <div class="timeline-pill">
                            <div class="timeline-stage">${event.stage}</div>
                            <div class="timeline-date">${event.date}</div>
                        </div>
                    `).join('')}
                </div>
                ${data.critical_deadlines.length > 0 ? `
                    <div class="critical-deadlines">
                        <h6>Critical Deadlines:</h6>
                        ${data.critical_deadlines.map(deadline => `
                            <div class="deadline-item ${deadline.importance}">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>${deadline.event}</span>
                                <span class="deadline-date">${deadline.date}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderSuccessRateBlock(data) {
        const container = document.getElementById('success-rate-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load success rate</div>';
            return;
        }

        container.innerHTML = `
            <div class="success-rate-info">
                <div class="success-main">
                    <div class="success-percentage">
                        <div class="success-value">${(data.overall_success_rate * 100).toFixed(1)}%</div>
                        <div class="success-label">Success Rate</div>
                    </div>
                    <div class="confidence-interval">
                        <span>Confidence: ${(data.confidence_interval.lower * 100).toFixed(1)}% - ${(data.confidence_interval.upper * 100).toFixed(1)}%</span>
                    </div>
                </div>
                <div class="success-factors">
                    <h6>Influencing Factors:</h6>
                    <div class="factors-list">
                        ${data.factors_influencing.map(factor => `
                            <div class="factor-item">
                                <span class="factor-name">${factor.factor}</span>
                                <span class="factor-impact ${factor.impact}">${factor.impact}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="recommendations">
                    <h6>Recommendations:</h6>
                    <ul>
                        ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    renderLawsBlock(data) {
        const container = document.getElementById('laws-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load applicable laws</div>';
            return;
        }

        container.innerHTML = `
            <div class="laws-info">
                <div class="jurisdiction-laws">
                    <h6>Applicable Laws (${data.country_name}):</h6>
                    <div class="laws-grid">
                        ${data.key_laws.map(law => `
                            <div class="law-chip">
                                <div class="law-name">${law.name}</div>
                                <div class="law-year">${law.year}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderConstitutionBlock(data) {
        const container = document.getElementById('constitution-content');
        if (!data) {
            container.innerHTML = '<div class="error-state">Failed to load constitutional articles</div>';
            return;
        }

        // Enhanced case rendering with proper object handling
        const renderCaseDetails = (cases) => {
            if (!cases || !Array.isArray(cases)) return '';
            return cases.map(caseObj => {
                // Handle different possible case object structures
                let caseName = '';
                let caseSignificance = '';
                let casePopularity = '';
                
                if (typeof caseObj === 'string') {
                    caseName = caseObj;
                } else if (typeof caseObj === 'object' && caseObj !== null) {
                    caseName = caseObj.name || caseObj.case || caseObj.case_name || 'Unknown Case';
                    caseSignificance = caseObj.significance || caseObj.description || '';
                    casePopularity = caseObj.popularity || caseObj.relevance_score || '';
                }
                
                return `
                    <div class="case-detail-item">
                        <div class="case-name">${caseName}</div>
                        ${caseSignificance ? `<div class="case-description">${caseSignificance}</div>` : ''}
                        ${casePopularity ? `<div class="case-score">Relevance: ${casePopularity}%</div>` : ''}
                    </div>
                `;
            }).join('');
        };

        container.innerHTML = `
            <div class="constitution-info">
                ${data.query_analysis && data.query_analysis.detected_topics.length > 0 ? `
                    <div class="query-analysis">
                        <h6>Detected Legal Topics:</h6>
                        <div class="topics-list">
                            ${data.query_analysis.detected_topics.map(topic => `
                                <span class="topic-badge">${topic.charAt(0).toUpperCase() + topic.slice(1)}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${data.popular_cases && data.popular_cases.length > 0 ? `
                    <div class="popular-cases-section">
                        <h6><i class="fas fa-star"></i> Most Relevant Cases:</h6>
                        <div class="popular-cases-grid">
                            ${data.popular_cases.map(caseObj => {
                                const caseName = caseObj.name || caseObj.case || 'Unknown Case';
                                const significance = caseObj.significance || caseObj.description || '';
                                const popularity = caseObj.popularity || caseObj.relevance_score || '';
                                return `
                                    <div class="popular-case-card">
                                        <div class="case-header">
                                            <span class="case-name">${caseName}</span>
                                            ${popularity ? `<span class="popularity-score">${popularity}% Popular</span>` : ''}
                                        </div>
                                        ${significance ? `<div class="case-significance">${significance}</div>` : ''}
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div class="constitutional-articles">
                    <h6>Relevant Constitutional Articles:</h6>
                    ${data.articles.map(article => `
                        <div class="constitution-article">
                            <div class="article-header">
                                <span class="article-number">Article ${article.number}</span>
                                <span class="article-title">${article.title}</span>
                            </div>
                            <div class="article-content">${article.content}</div>
                            ${article.key_cases && article.key_cases.length > 0 ? `
                                <div class="article-cases">
                                    <strong>Related Cases:</strong> 
                                    <div class="cases-list">
                                        ${renderCaseDetails(article.key_cases)}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
                
                ${data.interpretation ? `
                    <div class="constitutional-interpretation">
                        <h6>Constitutional Analysis:</h6>
                        <p>${data.interpretation}</p>
                    </div>
                ` : ''}
                
                ${data.amendments && data.amendments.length > 0 ? `
                    <div class="relevant-amendments">
                        <h6>Related Constitutional Amendments:</h6>
                        <div class="amendments-list">
                            ${data.amendments.map(amendment => `
                                <div class="amendment-item">
                                    <span class="amendment-number">Amendment ${amendment.number}</span>
                                    <span class="amendment-year">(${amendment.year})</span>
                                    <div class="amendment-description">${amendment.description}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async submitFeedback(feedbackType) {
        if (!this.currentAnalysis) return;

        // Store previous confidence before processing
        this.previousConfidence = this.getCurrentConfidence();
        
        // Show learning indicator
        document.getElementById('learning-indicator').style.display = 'flex';

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    feedback: {
                        moderation_id: `analysis_${Date.now()}`,
                        feedback_type: feedbackType,
                        comment: `Legal analysis feedback: ${feedbackType}`,
                        user_id: 'demo_user',
                        rating: feedbackType === 'thumbs_up' ? 5 : 2
                    }
                })
            });

            if (response.ok) {
                this.showNotification('Feedback submitted successfully! The system will learn from this.', 'success');

                // If feedback is "needs improvement", re-evaluate after learning
                if (feedbackType === 'thumbs_down') {
                    setTimeout(() => {
                        this.reEvaluateAfterFeedback();
                    }, 2000); // Wait 2 seconds for learning to process
                } else {
                    // For positive feedback, just show the learning badge briefly
                    setTimeout(() => {
                        this.showLearningBadge();
                        setTimeout(() => {
                            document.getElementById('learning-indicator').style.display = 'none';
                        }, 2000);
                    }, 1500);
                }
            } else {
                throw new Error('Feedback submission failed');
            }
        } catch (error) {
            console.error('Feedback error:', error);
            this.showNotification('Failed to submit feedback: ' + error.message, 'error');
            document.getElementById('learning-indicator').style.display = 'none';
        }
    }

    async reEvaluateAfterFeedback() {
        // Update learning indicator text
        const indicator = document.getElementById('learning-indicator');
        indicator.innerHTML = '<i class="fas fa-brain"></i><span>Re-evaluating with improved analysis...</span>';

        try {
            // Re-run the analysis with the same parameters
            await this.analyzeContent();

            // Calculate new confidence and show popup
            const newConfidence = this.getCurrentConfidence();
            if (this.previousConfidence !== null) {
                this.showFeedbackPopup(this.previousConfidence, newConfidence);
            }

            // Show success message
            this.showNotification('Analysis updated based on your feedback!', 'success');

            // Show learning badge
            this.showLearningBadge();

            // Hide learning indicator
            setTimeout(() => {
                indicator.style.display = 'none';
                // Reset indicator text for future use
                indicator.innerHTML = '<i class="fas fa-brain"></i><span>Re-evaluating after learning from feedback...</span>';
            }, 2000);

        } catch (error) {
            console.error('Re-evaluation error:', error);
            this.showNotification('Re-evaluation completed with some improvements.', 'info');
            indicator.style.display = 'none';
            // Reset indicator text
            indicator.innerHTML = '<i class="fas fa-brain"></i><span>Re-evaluating after learning from feedback...</span>';
        }
    }

    getCurrentConfidence() {
        // Get current confidence from the domain block
        const confidenceText = document.getElementById('domain-confidence-text');
        if (confidenceText) {
            return parseInt(confidenceText.textContent.replace('%', '')) || 85;
        }
        return 85; // Default confidence
    }

    showLearningBadge() {
        const badge = document.getElementById('learning-badge');
        if (badge) {
            badge.style.display = 'flex';
            // Hide after 3 seconds
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
            // Update confidence values
            confidenceBefore.textContent = `${previousConfidence}%`;
            confidenceAfter.textContent = `${newConfidence}%`;
            
            // Show popup
            popup.style.display = 'flex';
            
            // Bind close event
            document.getElementById('popup-close-btn').onclick = () => {
                popup.style.display = 'none';
            };
            
            // Auto-close after 5 seconds
            setTimeout(() => {
                popup.style.display = 'none';
            }, 5000);
        }
    }

    bindPopupEvents() {
        // Close popup when clicking outside
        document.getElementById('feedback-popup-overlay').addEventListener('click', (e) => {
            if (e.target === document.getElementById('feedback-popup-overlay')) {
                document.getElementById('feedback-popup-overlay').style.display = 'none';
            }
        });
        
        // Close popup with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.getElementById('feedback-popup-overlay').style.display = 'none';
            }
        });
    }

    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    showNotification(message, type) {
        // Simple notification - could be enhanced with a proper notification system
        alert(message);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new LegalAnalysisDashboard();
});