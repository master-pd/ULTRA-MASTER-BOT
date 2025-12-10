/**
 * 📊 DIAGRAM RENDERER - Render & Display Diagrams
 */

class DiagramRenderer {
    constructor() {
        this.diagrams = [];
        this.currentDiagram = null;
        this.chartInstances = {};
        
        this.init();
    }
    
    init() {
        this.loadDiagrams();
        this.setupEventListeners();
    }
    
    loadDiagrams() {
        // Load saved diagrams from localStorage
        const savedDiagrams = localStorage.getItem('master_diagrams');
        if (savedDiagrams) {
            this.diagrams = JSON.parse(savedDiagrams);
            this.renderDiagramGrid();
        }
        
        // Load from API
        this.fetchDiagrams();
    }
    
    fetchDiagrams() {
        fetch('/api/diagrams')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.diagrams) {
                    this.diagrams = data.diagrams;
                    this.renderDiagramGrid();
                    this.saveToLocalStorage();
                }
            })
            .catch(error => console.error('Error fetching diagrams:', error));
    }
    
    renderDiagramGrid() {
        const grid = document.getElementById('diagrams-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        this.diagrams.forEach((diagram, index) => {
            const diagramCard = this.createDiagramCard(diagram, index);
            grid.appendChild(diagramCard);
        });
        
        if (this.diagrams.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-project-diagram"></i>
                    <h3>No Diagrams Yet</h3>
                    <p>Create your first diagram using the form above!</p>
                </div>
            `;
        }
    }
    
    createDiagramCard(diagram, index) {
        const card = document.createElement('div');
        card.className = 'diagram-card animate__animated animate__fadeIn';
        card.style.animationDelay = `${index * 0.1}s`;
        
        let previewHTML = '';
        
        if (diagram.image_base64) {
            previewHTML = `<img src="${diagram.image_base64}" alt="${diagram.title}">`;
        } else if (diagram.chart_data) {
            previewHTML = `<canvas id="diagram-preview-${index}"></canvas>`;
        } else {
            previewHTML = `<div class="diagram-placeholder">
                <i class="fas fa-project-diagram"></i>
                <span>${diagram.type.toUpperCase()}</span>
            </div>`;
        }
        
        card.innerHTML = `
            <div class="diagram-card-header">
                <h4>${diagram.title}</h4>
                <span class="diagram-badge diagram-${diagram.type}">${diagram.type}</span>
            </div>
            <div class="diagram-preview">
                ${previewHTML}
            </div>
            <div class="diagram-card-footer">
                <span class="diagram-date">
                    <i class="far fa-calendar"></i>
                    ${new Date(diagram.timestamp).toLocaleDateString()}
                </span>
                <div class="diagram-actions">
                    <button class="btn-view" data-index="${index}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-download" data-index="${index}">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-delete" data-index="${index}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        card.querySelector('.btn-view').addEventListener('click', () => this.viewDiagram(diagram));
        card.querySelector('.btn-download').addEventListener('click', () => this.downloadDiagram(diagram));
        card.querySelector('.btn-delete').addEventListener('click', () => this.deleteDiagram(index));
        
        // Render chart if needed
        if (diagram.chart_data && !diagram.image_base64) {
            setTimeout(() => this.renderChartPreview(`diagram-preview-${index}`, diagram), 100);
        }
        
        return card;
    }
    
    renderChartPreview(canvasId, diagram) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        switch(diagram.type) {
            case 'bar_chart':
                this.renderBarChart(ctx, diagram.data);
                break;
            case 'pie_chart':
                this.renderPieChart(ctx, diagram.data);
                break;
            case 'line_chart':
                this.renderLineChart(ctx, diagram.data);
                break;
        }
    }
    
    renderBarChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || ['A', 'B', 'C', 'D', 'E'],
                datasets: [{
                    label: data.title || 'Data',
                    data: data.values || [10, 20, 30, 40, 50],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(231, 76, 60, 0.7)',
                        'rgba(155, 89, 182, 0.7)',
                        'rgba(241, 196, 15, 0.7)'
                    ],
                    borderColor: [
                        'rgb(52, 152, 219)',
                        'rgb(46, 204, 113)',
                        'rgb(231, 76, 60)',
                        'rgb(155, 89, 182)',
                        'rgb(241, 196, 15)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        this.chartInstances[ctx.canvas.id] = chart;
    }
    
    renderPieChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels || ['Category 1', 'Category 2', 'Category 3'],
                datasets: [{
                    data: data.values || [30, 40, 30],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(231, 76, 60, 0.7)'
                    ],
                    borderColor: [
                        'rgb(52, 152, 219)',
                        'rgb(46, 204, 113)',
                        'rgb(231, 76, 60)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        this.chartInstances[ctx.canvas.id] = chart;
    }
    
    renderLineChart(ctx, data) {
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                datasets: [{
                    label: data.title || 'Trend',
                    data: data.values || [10, 25, 15, 30, 20],
                    borderColor: 'rgb(52, 152, 219)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        this.chartInstances[ctx.canvas.id] = chart;
    }
    
    viewDiagram(diagram) {
        this.currentDiagram = diagram;
        this.showDiagramModal(diagram);
    }
    
    showDiagramModal(diagram) {
        const modal = document.getElementById('diagram-modal');
        const content = document.getElementById('diagram-content');
        
        let modalContent = '';
        
        if (diagram.image_base64) {
            modalContent = `
                <div class="diagram-full-view">
                    <img src="${diagram.image_base64}" alt="${diagram.title}" class="diagram-image">
                </div>
            `;
        } else if (diagram.chart_data) {
            modalContent = `
                <div class="diagram-chart-view">
                    <canvas id="diagram-full-chart"></canvas>
                </div>
            `;
        } else {
            modalContent = `
                <div class="diagram-text-view">
                    <h3>${diagram.title}</h3>
                    <pre>${JSON.stringify(diagram.data, null, 2)}</pre>
                </div>
            `;
        }
        
        modalContent += `
            <div class="diagram-info">
                <h3>${diagram.title}</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Type:</strong>
                        <span class="diagram-badge diagram-${diagram.type}">${diagram.type}</span>
                    </div>
                    <div class="info-item">
                        <strong>Created:</strong>
                        <span>${new Date(diagram.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="info-item">
                        <strong>Data Points:</strong>
                        <span>${diagram.data?.labels?.length || diagram.data?.values?.length || 'N/A'}</span>
                    </div>
                </div>
                
                ${diagram.text ? `
                <div class="diagram-original-text">
                    <strong>Original Text:</strong>
                    <p>${diagram.text.substring(0, 200)}...</p>
                </div>
                ` : ''}
                
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="diagramRenderer.downloadDiagram(diagramRenderer.currentDiagram)">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-secondary modal-close">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        
        content.innerHTML = modalContent;
        modal.style.display = 'block';
        
        // Render full chart if needed
        if (diagram.chart_data && !diagram.image_base64) {
            setTimeout(() => {
                const canvas = document.getElementById('diagram-full-chart');
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    this.renderFullChart(ctx, diagram);
                }
            }, 100);
        }
        
        // Add close button event
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    renderFullChart(ctx, diagram) {
        // Destroy existing chart if any
        if (this.chartInstances['full-chart']) {
            this.chartInstances['full-chart'].destroy();
        }
        
        switch(diagram.type) {
            case 'bar_chart':
                this.renderBarChart(ctx, diagram.data);
                break;
            case 'pie_chart':
                this.renderPieChart(ctx, diagram.data);
                break;
            case 'line_chart':
                this.renderLineChart(ctx, diagram.data);
                break;
        }
        
        this.chartInstances['full-chart'] = ctx.chart;
    }
    
    downloadDiagram(diagram) {
        if (diagram.image_base64) {
            // Download as image
            const link = document.createElement('a');
            link.href = diagram.image_base64;
            link.download = `${diagram.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            // Download as JSON
            const dataStr = JSON.stringify(diagram, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `${diagram.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            setTimeout(() => URL.revokeObjectURL(link.href), 100);
        }
        
        this.showNotification('Diagram downloaded successfully!', 'success');
    }
    
    deleteDiagram(index) {
        if (confirm('Are you sure you want to delete this diagram?')) {
            this.diagrams.splice(index, 1);
            this.renderDiagramGrid();
            this.saveToLocalStorage();
            
            // Also delete from server
            this.deleteFromServer(index);
            
            this.showNotification('Diagram deleted successfully!', 'success');
        }
    }
    
    deleteFromServer(index) {
        const diagram = this.diagrams[index];
        if (diagram && diagram.id) {
            fetch(`/api/diagrams/${diagram.id}`, {
                method: 'DELETE'
            }).catch(error => console.error('Error deleting from server:', error));
        }
    }
    
    saveToLocalStorage() {
        localStorage.setItem('master_diagrams', JSON.stringify(this.diagrams));
    }
    
    setupEventListeners() {
        // Generate diagram button
        const generateBtn = document.getElementById('generate-diagram-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateDiagram());
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('diagram-modal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // Text area auto-resize
        const textArea = document.getElementById('diagram-text');
        if (textArea) {
            textArea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        }
    }
    
    generateDiagram() {
        const text = document.getElementById('diagram-text').value;
        const type = document.getElementById('diagram-type').value;
        
        if (!text.trim()) {
            this.showNotification('Please enter some text to create a diagram', 'warning');
            return;
        }
        
        // Show loading
        this.showLoading();
        
        // Send to server
        fetch('/api/diagrams/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                type: type
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add to diagrams array
                this.diagrams.unshift(data.diagram);
                this.renderDiagramGrid();
                this.saveToLocalStorage();
                
                // Clear input
                document.getElementById('diagram-text').value = '';
                
                // Show success
                this.showNotification('Diagram created successfully!', 'success');
                
                // Show modal
                this.viewDiagram(data.diagram);
            } else {
                this.showNotification(data.error || 'Failed to create diagram', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Network error. Please try again.', 'error');
        })
        .finally(() => {
            this.hideLoading();
        });
    }
    
    showLoading() {
        const button = document.getElementById('generate-diagram-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            button.disabled = true;
        }
    }
    
    hideLoading() {
        const button = document.getElementById('generate-diagram-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-magic"></i> Generate Diagram';
            button.disabled = false;
        }
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize diagram renderer
window.diagramRenderer = new DiagramRenderer();