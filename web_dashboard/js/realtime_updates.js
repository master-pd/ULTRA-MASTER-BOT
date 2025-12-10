/**
 * ⚡ REALTIME UPDATES - WebSocket & Real-time Data
 */

class RealtimeUpdater {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.startHeartbeat();
    }
    
    connectWebSocket() {
        try {
            this.socket = new WebSocket('ws://localhost:8080/ws');
            
            this.socket.onopen = () => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.sendHeartbeat();
            };
            
            this.socket.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.socket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            this.socket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
        } catch (error) {
            console.error('❌ WebSocket connection error:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch(message.type) {
                case 'stats_update':
                    this.updateStats(message.data);
                    break;
                    
                case 'message_received':
                    this.addMessageToLog('received', message.data);
                    break;
                    
                case 'message_sent':
                    this.addMessageToLog('sent', message.data);
                    break;
                    
                case 'diagram_created':
                    this.showDiagramNotification(message.data);
                    break;
                    
                case 'image_created':
                    this.showImageNotification(message.data);
                    break;
                    
                case 'bot_status':
                    this.updateBotStatus(message.data);
                    break;
                    
                case 'learning_update':
                    this.updateLearningStats(message.data);
                    break;
                    
                case 'error':
                    this.showErrorNotification(message.data);
                    break;
                    
                case 'heartbeat_response':
                    this.handleHeartbeat();
                    break;
                    
                default:
                    console.log('Unknown message type:', message.type);
            }
            
        } catch (error) {
            console.error('❌ Error handling message:', error);
        }
    }
    
    updateStats(stats) {
        // Update dashboard statistics
        if (stats.messages_sent) {
            document.getElementById('total-messages').textContent = stats.messages_sent;
        }
        
        if (stats.diagrams_created) {
            document.getElementById('diagrams-created').textContent = stats.diagrams_created;
        }
        
        if (stats.images_generated) {
            document.getElementById('images-generated').textContent = stats.images_generated;
        }
        
        if (stats.profiles_scanned) {
            document.getElementById('profiles-scanned').textContent = stats.profiles_scanned;
        }
        
        // Update charts if they exist
        if (window.messageChart && stats.hourly_messages) {
            this.updateChart(window.messageChart, stats.hourly_messages);
        }
    }
    
    updateChart(chart, data) {
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.values;
        chart.update();
    }
    
    addMessageToLog(type, messageData) {
        const log = document.getElementById('message-log');
        if (!log) return;
        
        const time = new Date().toLocaleTimeString('bn-BD');
        const className = type === 'received' ? 'message-received' : 'message-sent';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${className} fade-in`;
        logEntry.innerHTML = `
            <span class="log-time">[${time}]</span>
            <span class="log-type">${type.toUpperCase()}:</span>
            <span class="log-content">${this.escapeHtml(messageData.text)}</span>
            ${messageData.sender ? `<span class="log-sender">From: ${messageData.sender}</span>` : ''}
        `;
        
        log.appendChild(logEntry);
        log.scrollTop = log.scrollHeight;
    }
    
    showDiagramNotification(diagramData) {
        this.showNotification({
            title: 'Diagram Created',
            message: `"${diagramData.title}" created successfully!`,
            type: 'success',
            action: () => this.showDiagramModal(diagramData)
        });
        
        // Add to diagrams grid
        this.addToDiagramsGrid(diagramData);
    }
    
    showImageNotification(imageData) {
        this.showNotification({
            title: 'Image Created',
            message: `"${imageData.title}" created successfully!`,
            type: 'success',
            action: () => this.showImageModal(imageData)
        });
        
        // Add to images grid
        this.addToImagesGrid(imageData);
    }
    
    updateBotStatus(status) {
        const statusElement = document.getElementById('bot-status');
        if (statusElement) {
            statusElement.textContent = status.state;
            statusElement.className = `status-badge status-${status.state}`;
        }
    }
    
    updateLearningStats(learningData) {
        document.getElementById('total-knowledge').textContent = learningData.total_items || 0;
        document.getElementById('learned-today-count').textContent = learningData.learned_today || 0;
        document.getElementById('learning-accuracy').textContent = learningData.accuracy + '%' || '0%';
    }
    
    showErrorNotification(error) {
        this.showNotification({
            title: 'Error',
            message: error.message || 'An error occurred',
            type: 'error'
        });
    }
    
    showNotification(options) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${options.type} notification-entrance`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${options.type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${options.title}</div>
                <div class="notification-message">${options.message}</div>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Add click action
        if (options.action) {
            notification.addEventListener('click', options.action);
        }
        
        // Add close functionality
        notification.querySelector('.notification-close').addEventListener('click', (e) => {
            e.stopPropagation();
            notification.remove();
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('fade-out');
                setTimeout(() => notification.remove(), 500);
            }
        }, 5000);
        
        // Add to page
        document.body.appendChild(notification);
    }
    
    showDiagramModal(diagramData) {
        const modal = document.getElementById('diagram-modal');
        const content = document.getElementById('diagram-content');
        
        if (diagramData.image_base64) {
            content.innerHTML = `
                <h3>${diagramData.title}</h3>
                <div class="diagram-preview">
                    <img src="${diagramData.image_base64}" alt="${diagramData.title}">
                </div>
                <div class="diagram-info">
                    <p><strong>Type:</strong> ${diagramData.type}</p>
                    <p><strong>Created:</strong> ${new Date(diagramData.timestamp).toLocaleString()}</p>
                </div>
                <div class="modal-actions">
                    <a href="${diagramData.image_base64}" download="${diagramData.title}.png" class="btn btn-primary">
                        <i class="fas fa-download"></i> Download
                    </a>
                    <button class="btn btn-secondary modal-close">Close</button>
                </div>
            `;
        }
        
        modal.style.display = 'block';
    }
    
    showImageModal(imageData) {
        const modal = document.getElementById('image-modal');
        const content = document.getElementById('image-content');
        
        if (imageData.image_base64) {
            content.innerHTML = `
                <h3>${imageData.title}</h3>
                <div class="image-preview">
                    <img src="${imageData.image_base64}" alt="${imageData.title}">
                </div>
                <div class="image-info">
                    <p><strong>Description:</strong> ${imageData.description || 'No description'}</p>
                    <p><strong>Created:</strong> ${new Date(imageData.timestamp).toLocaleString()}</p>
                </div>
                <div class="modal-actions">
                    <a href="${imageData.image_base64}" download="${imageData.title}.png" class="btn btn-primary">
                        <i class="fas fa-download"></i> Download
                    </a>
                    <button class="btn btn-secondary modal-close">Close</button>
                </div>
            `;
        }
        
        modal.style.display = 'block';
    }
    
    addToDiagramsGrid(diagramData) {
        const grid = document.getElementById('diagrams-grid');
        if (!grid) return;
        
        const diagramCard = document.createElement('div');
        diagramCard.className = 'diagram-card zoom-in';
        diagramCard.innerHTML = `
            <div class="diagram-card-image">
                <img src="${diagramData.image_base64}" alt="${diagramData.title}">
            </div>
            <div class="diagram-card-info">
                <h4>${diagramData.title}</h4>
                <p class="diagram-type">${diagramData.type}</p>
                <p class="diagram-time">${new Date(diagramData.timestamp).toLocaleTimeString()}</p>
            </div>
        `;
        
        diagramCard.addEventListener('click', () => this.showDiagramModal(diagramData));
        grid.insertBefore(diagramCard, grid.firstChild);
    }
    
    addToImagesGrid(imageData) {
        const grid = document.getElementById('images-grid');
        if (!grid) return;
        
        const imageCard = document.createElement('div');
        imageCard.className = 'image-card zoom-in';
        imageCard.innerHTML = `
            <div class="image-card-image">
                <img src="${imageData.image_base64}" alt="${imageData.title}">
            </div>
            <div class="image-card-info">
                <h4>${imageData.title}</h4>
                <p class="image-description">${(imageData.description || '').substring(0, 50)}...</p>
                <p class="image-time">${new Date(imageData.timestamp).toLocaleTimeString()}</p>
            </div>
        `;
        
        imageCard.addEventListener('click', () => this.showImageModal(imageData));
        grid.insertBefore(imageCard, grid.firstChild);
    }
    
    sendMessage(type, data) {
        if (this.isConnected && this.socket) {
            const message = {
                type: type,
                data: data,
                timestamp: Date.now()
            };
            
            this.socket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }
    
    startHeartbeat() {
        // Send heartbeat every 30 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.sendHeartbeat();
            }
        }, 30000);
    }
    
    sendHeartbeat() {
        this.sendMessage('heartbeat', { ping: 'pong' });
    }
    
    handleHeartbeat() {
        // Update last heartbeat time
        this.lastHeartbeat = Date.now();
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.className = connected ? 'connected' : 'disconnected';
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Public methods for external use
    sendBotCommand(command, data = {}) {
        this.sendMessage('bot_command', {
            command: command,
            ...data
        });
    }
    
    requestStats() {
        this.sendMessage('get_stats', {});
    }
    
    sendTestMessage(message) {
        this.sendMessage('send_test_message', {
            message: message
        });
    }
}

// Initialize realtime updater
window.realtimeUpdater = new RealtimeUpdater();