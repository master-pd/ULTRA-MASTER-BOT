/**
 * 🎮 MASTER BOT CONTROLLER - Main JavaScript
 * Ultra Advanced Control Panel
 */

class MasterBotController {
    constructor() {
        this.botStatus = 'disconnected';
        this.stats = {};
        this.websocket = null;
        this.chart = null;
        
        this.init();
    }
    
    init() {
        // Load bot info
        this.loadBotInfo();
        
        // Initialize charts
        this.initCharts();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Connect WebSocket
        this.connectWebSocket();
        
        // Load realtime stats
        this.loadRealtimeStats();
    }
    
    loadBotInfo() {
        fetch('/api/bot/info')
            .then(response => response.json())
            .then(data => {
                document.getElementById('bot-name').textContent = data.name;
                document.getElementById('bot-author').textContent = data.author;
                document.getElementById('bot-version').textContent = data.version;
                document.getElementById('bot-status').textContent = data.status;
                document.getElementById('bot-status').className = `status-${data.status}`;
            })
            .catch(error => console.error('Error loading bot info:', error));
    }
    
    initCharts() {
        // Messages chart
        const ctx = document.getElementById('messagesChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Messages per Hour',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: true,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Message Activity'
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Start/Stop bot
        document.getElementById('start-bot').addEventListener('click', () => this.startBot());
        document.getElementById('stop-bot').addEventListener('click', () => this.stopBot());
        
        // Send test message
        document.getElementById('send-test').addEventListener('click', () => this.sendTestMessage());
        
        // Generate diagram
        document.getElementById('generate-diagram').addEventListener('click', () => this.generateDiagram());
        
        // Create image
        document.getElementById('create-image').addEventListener('click', () => this.createImage());
        
        // Backup data
        document.getElementById('backup-data').addEventListener('click', () => this.backupData());
        
        // Update from GitHub
        document.getElementById('github-update').addEventListener('click', () => this.updateFromGitHub());
    }
    
    connectWebSocket() {
        this.websocket = new WebSocket('ws://localhost:8080/ws');
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.botStatus = 'connected';
            this.updateStatus();
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.botStatus = 'error';
            this.updateStatus();
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.botStatus = 'disconnected';
            this.updateStatus();
            // Reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }
    
    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'stats_update':
                this.updateStats(data.data);
                break;
            case 'message_received':
                this.addMessageToLog('received', data.data);
                break;
            case 'message_sent':
                this.addMessageToLog('sent', data.data);
                break;
            case 'diagram_created':
                this.showDiagram(data.data);
                break;
            case 'image_created':
                this.showImage(data.data);
                break;
            case 'error':
                this.showError(data.data);
                break;
        }
    }
    
    updateStats(stats) {
        this.stats = stats;
        
        // Update UI
        document.getElementById('total-messages').textContent = stats.messages_sent || 0;
        document.getElementById('diagrams-created').textContent = stats.diagrams_created || 0;
        document.getElementById('images-generated').textContent = stats.images_generated || 0;
        document.getElementById('profiles-scanned').textContent = stats.profiles_scanned || 0;
        
        // Update chart
        if (this.chart && stats.hourly_messages) {
            this.chart.data.labels = stats.hourly_messages.labels;
            this.chart.data.datasets[0].data = stats.hourly_messages.data;
            this.chart.update();
        }
    }
    
    addMessageToLog(type, message) {
        const log = document.getElementById('message-log');
        const time = new Date().toLocaleTimeString();
        const className = type === 'received' ? 'message-received' : 'message-sent';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${className}`;
        logEntry.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-type">${type.toUpperCase()}:</span>
            <span class="log-content">${this.escapeHtml(message)}</span>
        `;
        
        log.appendChild(logEntry);
        log.scrollTop = log.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    startBot() {
        fetch('/api/bot/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Bot started successfully!', 'success');
                    this.botStatus = 'running';
                    this.updateStatus();
                } else {
                    this.showNotification('Failed to start bot: ' + data.error, 'error');
                }
            })
            .catch(error => {
                this.showNotification('Error starting bot: ' + error, 'error');
            });
    }
    
    stopBot() {
        fetch('/api/bot/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Bot stopped successfully!', 'success');
                    this.botStatus = 'stopped';
                    this.updateStatus();
                } else {
                    this.showNotification('Failed to stop bot: ' + data.error, 'error');
                }
            })
            .catch(error => {
                this.showNotification('Error stopping bot: ' + error, 'error');
            });
    }
    
    sendTestMessage() {
        const message = document.getElementById('test-message').value;
        if (!message) {
            this.showNotification('Please enter a message', 'warning');
            return;
        }
        
        fetch('/api/bot/test-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Test message sent!', 'success');
                document.getElementById('test-message').value = '';
            } else {
                this.showNotification('Failed to send message: ' + data.error, 'error');
            }
        })
        .catch(error => {
            this.showNotification('Error: ' + error, 'error');
        });
    }
    
    generateDiagram() {
        const text = document.getElementById('diagram-text').value;
        if (!text) {
            this.showNotification('Please enter text for diagram', 'warning');
            return;
        }
        
        fetch('/api/diagram/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Diagram generated successfully!', 'success');
                this.showDiagram(data.diagram);
                document.getElementById('diagram-text').value = '';
            } else {
                this.showNotification('Failed to generate diagram: ' + data.error, 'error');
            }
        })
        .catch(error => {
            this.showNotification('Error: ' + error, 'error');
        });
    }
    
    createImage() {
        const description = document.getElementById('image-description').value;
        if (!description) {
            this.showNotification('Please enter image description', 'warning');
            return;
        }
        
        fetch('/api/image/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description: description })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Image created successfully!', 'success');
                this.showImage(data.image);
                document.getElementById('image-description').value = '';
            } else {
                this.showNotification('Failed to create image: ' + data.error, 'error');
            }
        })
        .catch(error => {
            this.showNotification('Error: ' + error, 'error');
        });
    }
    
    showDiagram(diagram) {
        const modal = document.getElementById('diagram-modal');
        const content = document.getElementById('diagram-content');
        
        if (diagram.image_base64) {
            content.innerHTML = `
                <h3>${diagram.title}</h3>
                <img src="${diagram.image_base64}" alt="${diagram.title}" style="max-width: 100%;">
                <p><strong>Type:</strong> ${diagram.type}</p>
                <a href="${diagram.download_url}" download="${diagram.title}.png" class="btn-download">
                    Download Diagram
                </a>
            `;
        } else if (diagram.diagram_html) {
            content.innerHTML = diagram.diagram_html;
        }
        
        modal.style.display = 'block';
    }
    
    showImage(image) {
        const modal = document.getElementById('image-modal');
        const content = document.getElementById('image-content');
        
        if (image.image_base64) {
            content.innerHTML = `
                <h3>${image.title}</h3>
                <img src="${image.image_base64}" alt="${image.title}" style="max-width: 100%;">
                <p><strong>Description:</strong> ${image.description}</p>
                <a href="${image.download_url}" download="${image.title}.png" class="btn-download">
                    Download Image
                </a>
            `;
        }
        
        modal.style.display = 'block';
    }
    
    backupData() {
        fetch('/api/backup', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Backup completed successfully!', 'success');
                } else {
                    this.showNotification('Backup failed: ' + data.error, 'error');
                }
            })
            .catch(error => {
                this.showNotification('Backup error: ' + error, 'error');
            });
    }
    
    updateFromGitHub() {
        fetch('/api/github/update', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Updated from GitHub successfully!', 'success');
                    this.loadBotInfo(); // Reload bot info
                } else {
                    this.showNotification('Update failed: ' + data.error, 'error');
                }
            })
            .catch(error => {
                this.showNotification('Update error: ' + error, 'error');
            });
    }
    
    updateStatus() {
        const statusElement = document.getElementById('bot-status');
        statusElement.textContent = this.botStatus;
        statusElement.className = `status-${this.botStatus}`;
        
        // Update button states
        const startBtn = document.getElementById('start-bot');
        const stopBtn = document.getElementById('stop-bot');
        
        if (this.botStatus === 'running') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }
    
    showNotification(message, type) {
        // Remove existing notifications
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }
        
        // Create new notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Add to page
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
    }
    
    showError(error) {
        this.showNotification(`Error: ${error}`, 'error');
    }
    
    loadRealtimeStats() {
        // Load stats every 10 seconds
        setInterval(() => {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => this.updateStats(data))
                .catch(error => console.error('Error loading stats:', error));
        }, 10000);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.botController = new MasterBotController();
});

// Close modals
document.querySelectorAll('.modal-close').forEach(button => {
    button.addEventListener('click', function() {
        this.closest('.modal').style.display = 'none';
    });
});

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});