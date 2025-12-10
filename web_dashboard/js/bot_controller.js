/**
 * 🎮 BOT CONTROLLER - Control Bot Operations
 */

class BotController {
    constructor() {
        this.botStatus = 'disconnected';
        this.statsInterval = null;
        this.commandHistory = [];
        this.maxCommandHistory = 50;
        
        this.init();
    }
    
    init() {
        this.loadBotConfig();
        this.setupEventListeners();
        this.startStatsPolling();
        this.loadCommandHistory();
    }
    
    loadBotConfig() {
        // Load bot configuration from localStorage
        const savedConfig = localStorage.getItem('bot_config');
        if (savedConfig) {
            const config = JSON.parse(savedConfig);
            
            // Apply config to form
            if (config.bot_name) {
                document.getElementById('bot-name-input').value = config.bot_name;
            }
            if (config.learning_rate) {
                document.getElementById('learning-rate').value = config.learning_rate;
                document.getElementById('learning-rate-value').textContent = config.learning_rate;
            }
            if (config.response_speed) {
                document.getElementById('response-speed').value = config.response_speed;
            }
            // ... load other config values
        }
    }
    
    setupEventListeners() {
        // Start/Stop bot buttons
        document.getElementById('start-bot').addEventListener('click', () => this.startBot());
        document.getElementById('stop-bot').addEventListener('click', () => this.stopBot());
        
        // Settings controls
        document.getElementById('update-bot-name').addEventListener('click', () => this.updateBotName());
        document.getElementById('learning-rate').addEventListener('input', (e) => {
            document.getElementById('learning-rate-value').textContent = e.target.value;
        });
        
        // Save settings
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
        document.getElementById('reset-settings').addEventListener('click', () => this.resetSettings());
        document.getElementById('export-settings').addEventListener('click', () => this.exportSettings());
        
        // Command input
        const commandInput = document.getElementById('command-input');
        if (commandInput) {
            commandInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.executeCommand(commandInput.value);
                    commandInput.value = '';
                }
            });
            
            document.getElementById('send-command').addEventListener('click', () => {
                this.executeCommand(commandInput.value);
                commandInput.value = '';
            });
        }
        
        // Backup buttons
        document.getElementById('backup-now').addEventListener('click', () => this.createBackup());
        document.getElementById('restore-backup').addEventListener('click', () => this.restoreBackup());
        
        // Update buttons
        document.getElementById('check-updates').addEventListener('click', () => this.checkForUpdates());
        document.getElementById('apply-update').addEventListener('click', () => this.applyUpdate());
    }
    
    startStatsPolling() {
        // Poll for stats every 10 seconds
        this.statsInterval = setInterval(() => {
            this.fetchBotStats();
        }, 10000);
        
        // Initial fetch
        this.fetchBotStats();
    }
    
    fetchBotStats() {
        fetch('/api/bot/stats')
            .then(response => response.json())
            .then(data => {
                this.updateStatsDisplay(data);
            })
            .catch(error => console.error('Error fetching stats:', error));
    }
    
    updateStatsDisplay(stats) {
        // Update stats cards
        const elements = {
            'total-messages': stats.messages_sent || 0,
            'messages-sent': stats.messages_sent_today || 0,
            'messages-received': stats.messages_received_today || 0,
            'response-rate': stats.response_rate ? `${stats.response_rate}%` : '0%',
            'diagrams-created': stats.diagrams_created || 0,
            'diagrams-today': stats.diagrams_today || 0,
            'images-generated': stats.images_generated || 0,
            'images-today': stats.images_today || 0,
            'profiles-scanned': stats.profiles_scanned || 0,
            'knowledge-items': stats.knowledge_items || 0,
            'learned-today': stats.learned_today || 0,
            'accuracy-rate': stats.accuracy_rate ? `${stats.accuracy_rate}%` : '0%',
            'memory-usage': stats.memory_usage ? `${stats.memory_usage}%` : '0%'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Update bot status
        if (stats.bot_status) {
            this.updateBotStatus(stats.bot_status);
        }
    }
    
    updateBotStatus(status) {
        this.botStatus = status;
        const statusElement = document.getElementById('bot-status');
        
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-badge status-${status}`;
            
            // Update button states
            const startBtn = document.getElementById('start-bot');
            const stopBtn = document.getElementById('stop-bot');
            
            if (status === 'running') {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
    }
    
    startBot() {
        this.showLoading('start-bot', 'Starting...');
        
        fetch('/api/bot/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateBotStatus('running');
                this.showNotification('Bot started successfully!', 'success');
            } else {
                this.showNotification(`Failed to start bot: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        })
        .finally(() => {
            this.hideLoading('start-bot', 'Start Bot');
        });
    }
    
    stopBot() {
        if (!confirm('Are you sure you want to stop the bot?')) {
            return;
        }
        
        this.showLoading('stop-bot', 'Stopping...');
        
        fetch('/api/bot/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateBotStatus('stopped');
                this.showNotification('Bot stopped successfully!', 'success');
            } else {
                this.showNotification(`Failed to stop bot: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        })
        .finally(() => {
            this.hideLoading('stop-bot', 'Stop Bot');
        });
    }
    
    executeCommand(command) {
        if (!command.trim()) return;
        
        // Add to command history
        this.addToCommandHistory(command);
        
        // Send command to bot
        fetch('/api/bot/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Command executed successfully!', 'success');
                this.addCommandResponse(data.response);
            } else {
                this.showNotification(`Command failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        });
    }
    
    addToCommandHistory(command) {
        this.commandHistory.unshift({
            command: command,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last N commands
        if (this.commandHistory.length > this.maxCommandHistory) {
            this.commandHistory = this.commandHistory.slice(0, this.maxCommandHistory);
        }
        
        this.saveCommandHistory();
        this.updateCommandHistoryDisplay();
    }
    
    addCommandResponse(response) {
        const historyList = document.getElementById('command-history');
        if (!historyList) return;
        
        const responseItem = document.createElement('div');
        responseItem.className = 'command-response';
        responseItem.innerHTML = `
            <div class="response-header">
                <i class="fas fa-robot"></i>
                <span class="response-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="response-content">${response}</div>
        `;
        
        historyList.prepend(responseItem);
    }
    
    updateCommandHistoryDisplay() {
        const historyList = document.getElementById('command-history');
        if (!historyList) return;
        
        historyList.innerHTML = '';
        
        this.commandHistory.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'command-history-item';
            historyItem.innerHTML = `
                <div class="history-header">
                    <i class="fas fa-terminal"></i>
                    <span class="history-time">${new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="history-command">${item.command}</div>
            `;
            
            historyList.appendChild(historyItem);
        });
    }
    
    saveCommandHistory() {
        localStorage.setItem('bot_command_history', JSON.stringify(this.commandHistory));
    }
    
    loadCommandHistory() {
        const savedHistory = localStorage.getItem('bot_command_history');
        if (savedHistory) {
            this.commandHistory = JSON.parse(savedHistory);
            this.updateCommandHistoryDisplay();
        }
    }
    
    updateBotName() {
        const newName = document.getElementById('bot-name-input').value.trim();
        if (!newName) {
            this.showNotification('Please enter a bot name', 'warning');
            return;
        }
        
        fetch('/api/bot/update-name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Bot name updated successfully!', 'success');
                // Update in UI
                document.getElementById('bot-name').textContent = newName;
            } else {
                this.showNotification(`Failed to update name: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        });
    }
    
    saveSettings() {
        const settings = {
            bot_name: document.getElementById('bot-name-input').value,
            learning_rate: document.getElementById('learning-rate').value,
            response_speed: document.getElementById('response-speed').value,
            auto_learning: document.getElementById('auto-learning').checked,
            fb_delay: document.getElementById('fb-delay').value,
            max_messages: document.getElementById('max-messages').value,
            auto_join: document.getElementById('auto-join').checked,
            stealth_mode: document.getElementById('stealth-mode').checked
        };
        
        // Save to localStorage
        localStorage.setItem('bot_config', JSON.stringify(settings));
        
        // Send to server
        fetch('/api/bot/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Settings saved successfully!', 'success');
            } else {
                this.showNotification(`Failed to save settings: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        });
    }
    
    resetSettings() {
        if (!confirm('Are you sure you want to reset all settings to default?')) {
            return;
        }
        
        const defaultSettings = {
            bot_name: 'MASTER 🪓',
            learning_rate: 0.8,
            response_speed: 'normal',
            auto_learning: true,
            fb_delay: 3,
            max_messages: 100,
            auto_join: true,
            stealth_mode: true
        };
        
        // Apply default settings to form
        Object.entries(defaultSettings).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
        
        // Update display
        document.getElementById('learning-rate-value').textContent = defaultSettings.learning_rate;
        
        this.showNotification('Settings reset to default', 'success');
    }
    
    exportSettings() {
        const settings = localStorage.getItem('bot_config');
        if (!settings) {
            this.showNotification('No settings to export', 'warning');
            return;
        }
        
        const blob = new Blob([settings], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'bot_settings.json';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        this.showNotification('Settings exported successfully!', 'success');
    }
    
    createBackup() {
        this.showLoading('backup-now', 'Creating backup...');
        
        fetch('/api/backup/create', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Backup created successfully!', 'success');
                this.updateBackupList();
            } else {
                this.showNotification(`Backup failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        })
        .finally(() => {
            this.hideLoading('backup-now', 'Create Backup');
        });
    }
    
    restoreBackup() {
        // Show backup selection modal
        this.showBackupSelectionModal();
    }
    
    updateBackupList() {
        fetch('/api/backup/list')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.displayBackupList(data.backups);
                }
            })
            .catch(error => console.error('Error fetching backup list:', error));
    }
    
    displayBackupList(backups) {
        const backupList = document.getElementById('backup-list');
        if (!backupList) return;
        
        backupList.innerHTML = '';
        
        backups.forEach(backup => {
            const backupItem = document.createElement('div');
            backupItem.className = 'backup-item';
            backupItem.innerHTML = `
                <div class="backup-info">
                    <div class="backup-name">${backup.name}</div>
                    <div class="backup-details">
                        <span class="backup-size">${backup.size}</span>
                        <span class="backup-date">${new Date(backup.date).toLocaleString()}</span>
                    </div>
                </div>
                <div class="backup-actions">
                    <button class="btn-restore" data-backup="${backup.name}">
                        <i class="fas fa-undo"></i> Restore
                    </button>
                    <button class="btn-delete-backup" data-backup="${backup.name}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            
            backupList.appendChild(backupItem);
        });
    }
    
    showBackupSelectionModal() {
        // Create modal for backup selection
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'backup-modal';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Select Backup to Restore</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="backup-list" id="backup-list">
                        Loading backups...
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="close-backup-modal">Cancel</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        // Load backup list
        this.updateBackupList();
        
        // Setup event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.querySelector('#close-backup-modal').addEventListener('click', () => modal.remove());
        
        // Delegate events for restore/delete buttons
        modal.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-restore')) {
                const backupName = e.target.getAttribute('data-backup');
                this.confirmRestore(backupName);
            }
            
            if (e.target.classList.contains('btn-delete-backup')) {
                const backupName = e.target.getAttribute('data-backup');
                this.confirmDeleteBackup(backupName);
            }
        });
    }
    
    confirmRestore(backupName) {
        if (!confirm(`Are you sure you want to restore backup "${backupName}"? This will overwrite current data.`)) {
            return;
        }
        
        fetch('/api/backup/restore', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ backup: backupName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Backup restored successfully!', 'success');
                // Close modal
                const modal = document.getElementById('backup-modal');
                if (modal) modal.remove();
            } else {
                this.showNotification(`Restore failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        });
    }
    
    confirmDeleteBackup(backupName) {
        if (!confirm(`Are you sure you want to delete backup "${backupName}"?`)) {
            return;
        }
        
        fetch('/api/backup/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ backup: backupName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Backup deleted successfully!', 'success');
                this.updateBackupList();
            } else {
                this.showNotification(`Delete failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        });
    }
    
    checkForUpdates() {
        this.showLoading('check-updates', 'Checking...');
        
        fetch('/api/updates/check')
            .then(response => response.json())
            .then(data => {
                if (data.update_available) {
                    this.showUpdateAvailableModal(data);
                } else {
                    this.showNotification('Bot is up to date!', 'success');
                }
            })
            .catch(error => {
                this.showNotification(`Error checking updates: ${error.message}`, 'error');
            })
            .finally(() => {
                this.hideLoading('check-updates', 'Check Updates');
            });
    }
    
    showUpdateAvailableModal(updateInfo) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'update-modal';
        
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Update Available!</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="update-info">
                        <p><strong>New Version:</strong> ${updateInfo.new_version}</p>
                        <p><strong>Current Version:</strong> ${updateInfo.current_version}</p>
                        <p><strong>Release Date:</strong> ${new Date(updateInfo.release_date).toLocaleDateString()}</p>
                        ${updateInfo.changelog ? `
                        <div class="changelog">
                            <h4>Changelog:</h4>
                            <pre>${updateInfo.changelog}</pre>
                        </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" id="apply-update-now">Apply Update</button>
                    <button class="btn btn-secondary" id="cancel-update">Later</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
        
        // Setup event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.querySelector('#cancel-update').addEventListener('click', () => modal.remove());
        modal.querySelector('#apply-update-now').addEventListener('click', () => {
            this.applyUpdate();
            modal.remove();
        });
    }
    
    applyUpdate() {
        if (!confirm('Apply update now? The bot will restart automatically.')) {
            return;
        }
        
        this.showLoading('apply-update', 'Updating...');
        
        fetch('/api/updates/apply', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Update applied successfully! Bot will restart.', 'success');
                
                // Show countdown for restart
                let countdown = 5;
                const countdownInterval = setInterval(() => {
                    if (countdown > 0) {
                        this.showNotification(`Restarting in ${countdown} seconds...`, 'info');
                        countdown--;
                    } else {
                        clearInterval(countdownInterval);
                        // Reload page
                        location.reload();
                    }
                }, 1000);
                
            } else {
                this.showNotification(`Update failed: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            this.showNotification(`Error: ${error.message}`, 'error');
        })
        .finally(() => {
            this.hideLoading('apply-update', 'Apply Update');
        });
    }
    
    showLoading(buttonId, loadingText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
        }
    }
    
    hideLoading(buttonId, originalText) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.innerHTML = originalText;
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

// Initialize bot controller
window.botController = new BotController();