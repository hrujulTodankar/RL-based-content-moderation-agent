// RL Content Moderation Dashboard JavaScript
class ModerationDashboard {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 12;
        this.moderatedContent = [];
        this.filters = {
            contentType: 'all',
            scoreMin: 0,
            scoreMax: 1,
            status: 'all'
        };

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStats();
        this.loadModeratedContent();
        this.setupRealTimeUpdates();
    }

    bindEvents() {
        // Filters
        document.getElementById('content-type-filter').addEventListener('change', (e) => {
            this.filters.contentType = e.target.value;
            this.applyFilters();
        });

        document.getElementById('score-min').addEventListener('input', (e) => {
            this.filters.scoreMin = parseFloat(e.target.value);
            document.getElementById('score-min-value').textContent = e.target.value;
            this.applyFilters();
        });

        document.getElementById('score-max').addEventListener('input', (e) => {
            this.filters.scoreMax = parseFloat(e.target.value);
            document.getElementById('score-max-value').textContent = e.target.value;
            this.applyFilters();
        });

        document.getElementById('status-filter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.applyFilters();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadStats();
            this.loadModeratedContent();
        });

        // Content submission
        document.getElementById('moderate-btn').addEventListener('click', () => {
            this.moderateContent();
        });

        // Modal
        document.querySelector('.close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('feedback-modal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('feedback-modal')) {
                this.closeModal();
            }
        });
    }

    async loadStats() {
        try {
            const response = await fetch('/stats');
            const stats = await response.json();

            document.getElementById('total-moderated').textContent = stats.total_moderations || 0;
            document.getElementById('flagged-count').textContent = stats.flagged_count || 0;
            document.getElementById('avg-confidence').textContent = `${(stats.avg_confidence * 100 || 0).toFixed(1)}%`;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadModeratedContent() {
        this.showLoading();
        try {
            // Try to get real data from backend
            const response = await fetch('/moderated-content?page=1&limit=12');
            if (response.ok) {
                const data = await response.json();
                this.moderatedContent = data.content || [];
                this.totalItems = data.total || 0;
            } else {
                // Fallback to sample data
                const statsResponse = await fetch('/stats');
                const stats = statsResponse.ok ? await statsResponse.json() : {};
                this.moderatedContent = this.generateSampleContent(stats.total_moderations || 10);
            }
            this.applyFilters();
        } catch (error) {
            console.error('Error loading content:', error);
            this.moderatedContent = this.generateSampleContent(10);
            this.applyFilters();
        }
        this.hideLoading();
    }

    generateSampleContent(count) {
        const contentTypes = ['text', 'image', 'audio', 'video', 'code'];
        const sampleTexts = [
            "This is a sample text content for moderation testing.",
            "Check out this amazing product! Limited time offer!!!",
            "Beautiful sunset over the mountains. Nature is amazing.",
            "function calculateSum(a, b) { return a + b; }",
            "The weather today is perfect for outdoor activities."
        ];

        const content = [];
        for (let i = 0; i < count; i++) {
            const type = contentTypes[Math.floor(Math.random() * contentTypes.length)];
            const score = Math.random();
            const confidence = Math.random() * 0.5 + 0.5; // 0.5-1.0

            content.push({
                moderation_id: `mod_${i + 1}`,
                content_type: type,
                content: type === 'text' ? sampleTexts[Math.floor(Math.random() * sampleTexts.length)] : `Sample ${type} content`,
                flagged: score > 0.7,
                score: score,
                confidence: confidence,
                reasons: score > 0.7 ? ['High spam probability'] : [],
                timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
                nlp_metadata: {
                    sentiment: Math.random() > 0.5 ? 'positive' : 'negative',
                    topic: ['general', 'spam', 'entertainment', 'technical'][Math.floor(Math.random() * 4)],
                    toxicity: Math.random() * 0.3
                }
            });
        }
        return content;
    }

    applyFilters() {
        let filtered = this.moderatedContent.filter(item => {
            if (this.filters.contentType !== 'all' && item.content_type !== this.filters.contentType) {
                return false;
            }
            if (item.score < this.filters.scoreMin || item.score > this.filters.scoreMax) {
                return false;
            }
            if (this.filters.status === 'flagged' && !item.flagged) {
                return false;
            }
            if (this.filters.status === 'approved' && item.flagged) {
                return false;
            }
            return true;
        });

        this.renderContent(filtered);
        this.renderPagination(filtered.length);
    }

    renderContent(content) {
        const grid = document.getElementById('content-grid');
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const pageContent = content.slice(start, end);

        grid.innerHTML = pageContent.map(item => this.createContentCard(item)).join('');
    }

    createContentCard(item) {
        const decisionClass = item.flagged ? 'flagged' : 'approved';
        const decisionText = item.flagged ? 'Flagged' : 'Approved';

        return `
            <div class="content-card ${decisionClass}" data-id="${item.moderation_id}">
                <div class="card-header">
                    <span class="content-type">${item.content_type}</span>
                    <span class="content-timestamp">${this.formatTimestamp(item.timestamp)}</span>
                </div>

                <div class="content-preview">
                    ${this.renderContentPreview(item)}
                </div>

                <div class="moderation-result">
                    <span class="decision-badge ${decisionClass}">${decisionText}</span>
                    <div class="score-display">
                        <div class="score-value">${item.score.toFixed(2)}</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${item.confidence * 100}%"></div>
                        </div>
                        <div style="font-size: 0.8rem; color: #7f8c8d;">${(item.confidence * 100).toFixed(1)}% confident</div>
                    </div>
                </div>

                ${this.renderNLPMetadata(item.nlp_metadata)}

                <div class="feedback-section">
                    <div class="feedback-buttons">
                        <button class="feedback-btn thumbs-up" data-id="${item.moderation_id}" data-feedback="thumbs_up">
                            <i class="fas fa-thumbs-up"></i> Good
                        </button>
                        <button class="feedback-btn thumbs-down" data-id="${item.moderation_id}" data-feedback="thumbs_down">
                            <i class="fas fa-thumbs-down"></i> Poor
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderContentPreview(item) {
        if (item.content_type === 'text') {
            return `<div class="content-text">${item.content}</div>`;
        } else if (item.content_type === 'image') {
            return `<img src="/static/images/placeholder.jpg" alt="Content thumbnail" class="content-thumbnail">`;
        } else {
            return `<div class="content-text">${item.content_type.toUpperCase()} CONTENT</div>`;
        }
    }

    renderNLPMetadata(metadata) {
        if (!metadata) return '';

        return `
            <div class="nlp-metadata">
                <div class="metadata-item">
                    <span class="metadata-label">Sentiment:</span>
                    <span class="metadata-value">${metadata.sentiment}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Topic:</span>
                    <span class="metadata-value">${metadata.topic}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Toxicity:</span>
                    <span class="metadata-value">${(metadata.toxicity * 100).toFixed(1)}%</span>
                </div>
            </div>
        `;
    }

    renderPagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const pagination = document.getElementById('pagination');

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let buttons = [];
        for (let i = 1; i <= totalPages; i++) {
            buttons.push(`
                <button class="page-btn ${i === this.currentPage ? 'active' : ''}" data-page="${i}">
                    ${i}
                </button>
            `);
        }

        pagination.innerHTML = buttons.join('');

        // Bind pagination events
        pagination.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.currentPage = parseInt(e.target.dataset.page);
                this.applyFilters();
            });
        });
    }

    async moderateContent() {
        const content = document.getElementById('content-input').value.trim();
        const contentType = document.getElementById('content-type-select').value;

        if (!content) {
            alert('Please enter content to moderate');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/moderate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    content_type: contentType
                })
            });

            const result = await response.json();

            if (response.ok) {
                // Add to content list
                this.moderatedContent.unshift({
                    ...result,
                    content: content,
                    nlp_metadata: {
                        sentiment: 'neutral',
                        topic: 'general',
                        toxicity: 0.1
                    }
                });

                this.applyFilters();
                document.getElementById('content-input').value = '';

                // Show success message
                this.showNotification('Content moderated successfully!', 'success');
            } else {
                throw new Error(result.detail || 'Moderation failed');
            }
        } catch (error) {
            console.error('Moderation error:', error);
            this.showNotification('Failed to moderate content: ' + error.message, 'error');
        }

        this.hideLoading();
    }

    setupRealTimeUpdates() {
        // Listen for feedback button clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.feedback-btn')) {
                const btn = e.target.closest('.feedback-btn');
                const moderationId = btn.dataset.id;
                const feedbackType = btn.dataset.feedback;

                this.showFeedbackModal(moderationId, feedbackType);
            }
        });
    }

    showFeedbackModal(moderationId, feedbackType) {
        const item = this.moderatedContent.find(c => c.moderation_id === moderationId);
        if (!item) return;

        document.getElementById('feedback-content-preview').innerHTML = `
            <strong>Type:</strong> ${item.content_type}<br>
            <strong>Decision:</strong> ${item.flagged ? 'Flagged' : 'Approved'}<br>
            <strong>Score:</strong> ${item.score.toFixed(2)}<br>
            <strong>Confidence:</strong> ${(item.confidence * 100).toFixed(1)}%<br><br>
            <strong>Content:</strong><br>${item.content}
        `;

        // Pre-select feedback button
        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.querySelector(`.feedback-btn[data-feedback="${feedbackType}"]`).classList.add('selected');

        document.getElementById('feedback-modal').classList.add('show');

        // Store current feedback info
        this.currentFeedback = { moderationId, feedbackType };
    }

    closeModal() {
        document.getElementById('feedback-modal').classList.remove('show');
        document.getElementById('feedback-comment').value = '';
    }

    async submitFeedback() {
        const comment = document.getElementById('feedback-comment').value.trim();

        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    moderation_id: this.currentFeedback.moderationId,
                    feedback_type: this.currentFeedback.feedbackType,
                    comment: comment || null
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Feedback submitted successfully!', 'success');
                this.closeModal();

                // Highlight the updated card
                const card = document.querySelector(`[data-id="${this.currentFeedback.moderationId}"]`);
                if (card) {
                    card.classList.add('updated');
                    setTimeout(() => card.classList.remove('updated'), 2000);
                }

                // Refresh stats
                this.loadStats();
            } else {
                throw new Error(result.detail || 'Feedback submission failed');
            }
        } catch (error) {
            console.error('Feedback error:', error);
            this.showNotification('Failed to submit feedback: ' + error.message, 'error');
        }
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

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ModerationDashboard();
});

// Add submit feedback functionality to modal
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('feedback-btn') && e.target.closest('#feedback-modal')) {
        const feedbackType = e.target.dataset.feedback;
        if (window.dashboard) {
            window.dashboard.currentFeedback.feedbackType = feedbackType;
            document.querySelectorAll('#feedback-modal .feedback-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            e.target.classList.add('selected');
        }
    }
});

// Submit feedback when Enter is pressed in comment field
document.getElementById('feedback-comment').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (window.dashboard) {
            window.dashboard.submitFeedback();
        }
    }
});

// Add submit button to modal
document.addEventListener('DOMContentLoaded', () => {
    const modalBody = document.querySelector('.modal-body');
    const submitBtn = document.createElement('button');
    submitBtn.textContent = 'Submit Feedback';
    submitBtn.className = 'btn-primary';
    submitBtn.style.marginTop = '15px';
    submitBtn.addEventListener('click', () => {
        if (window.dashboard) {
            window.dashboard.submitFeedback();
        }
    });
    modalBody.appendChild(submitBtn);
});