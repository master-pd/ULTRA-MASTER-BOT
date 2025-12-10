#!/usr/bin/env node

/**
 * 📊 BOT MONITOR - Monitor Bot Health & Performance
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');

class BotMonitor {
    constructor() {
        this.config = this.loadConfig();
        this.metrics = {
            cpu: 0,
            memory: 0,
            disk: 0,
            uptime: 0,
            bot_status: 'unknown',
            last_check: null
        };
        
        this.alerts = [];
        this.logFile = 'logs/monitor.log';
        
        // Ensure log directory exists
        if (!fs.existsSync('logs')) {
            fs.mkdirSync('logs', { recursive: true });
        }
    }
    
    loadConfig() {
        const configPath = path.join(__dirname, '../config/monitor_config.json');
        
        if (fs.existsSync(configPath)) {
            return JSON.parse(fs.readFileSync(configPath, 'utf8'));
        }
        
        // Default configuration
        return {
            check_interval: 60, // seconds
            alert_thresholds: {
                cpu: 80, // percentage
                memory: 85, // percentage
                disk: 90, // percentage
                response_time: 5000, // milliseconds
                error_rate: 10 // percentage
            },
            alerts: {
                email: false,
                telegram: false,
                webhook: false
            },
            endpoints: {
                bot_api: 'http://localhost:8080/api',
                health_check: 'http://localhost:8080/health'
            }
        };
    }
    
    log(message, type = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${type}] ${message}\n`;
        
        console.log(logMessage.trim());
        
        // Write to log file
        fs.appendFileSync(this.logFile, logMessage, 'utf8');
    }
    
    async checkSystemMetrics() {
        try {
            // CPU usage
            const cpuUsage = os.loadavg()[0] / os.cpus().length * 100;
            this.metrics.cpu = Math.round(cpuUsage);
            
            // Memory usage
            const totalMem = os.totalmem();
            const freeMem = os.freemem();
            const usedMem = totalMem - freeMem;
            this.metrics.memory = Math.round((usedMem / totalMem) * 100);
            
            // Disk usage
            exec('df -h /', (error, stdout) => {
                if (!error) {
                    const lines = stdout.trim().split('\n');
                    if (lines.length > 1) {
                        const parts = lines[1].split(/\s+/);
                        const usage = parseInt(parts[4]); // Usage percentage
                        this.metrics.disk = usage;
                    }
                }
            });
            
            // Uptime
            this.metrics.uptime = Math.round(os.uptime() / 3600); // hours
            
            this.log(`System metrics - CPU: ${this.metrics.cpu}%, Memory: ${this.metrics.memory}%, Disk: ${this.metrics.disk}%, Uptime: ${this.metrics.uptime}h`);
            
        } catch (error) {
            this.log(`Error checking system metrics: ${error.message}`, 'ERROR');
        }
    }
    
    async checkBotHealth() {
        try {
            const response = await axios.get(`${this.config.endpoints.health_check}`, {
                timeout: 5000
            });
            
            if (response.status === 200) {
                this.metrics.bot_status = 'healthy';
                this.log('Bot health check passed');
            } else {
                this.metrics.bot_status = 'unhealthy';
                this.log(`Bot health check failed with status: ${response.status}`, 'WARNING');
            }
            
        } catch (error) {
            this.metrics.bot_status = 'offline';
            this.log(`Bot health check failed: ${error.message}`, 'ERROR');
        }
    }
    
    async checkBotMetrics() {
        try {
            const response = await axios.get(`${this.config.endpoints.bot_api}/stats`, {
                timeout: 5000
            });
            
            if (response.status === 200) {
                const data = response.data;
                
                // Update metrics
                this.metrics.bot_metrics = {
                    messages_today: data.messages_today || 0,
                    response_rate: data.response_rate || 0,
                    active_users: data.active_users || 0,
                    error_count: data.error_count || 0
                };
                
                this.log(`Bot metrics - Messages: ${this.metrics.bot_metrics.messages_today}, Response Rate: ${this.metrics.bot_metrics.response_rate}%`);
                
            }
            
        } catch (error) {
            this.log(`Error checking bot metrics: ${error.message}`, 'ERROR');
        }
    }
    
    checkThresholds() {
        const thresholds = this.config.alert_thresholds;
        const alerts = [];
        
        // Check CPU
        if (this.metrics.cpu > thresholds.cpu) {
            alerts.push({
                type: 'HIGH_CPU',
                message: `CPU usage is high: ${this.metrics.cpu}% (threshold: ${thresholds.cpu}%)`,
                severity: 'WARNING'
            });
        }
        
        // Check Memory
        if (this.metrics.memory > thresholds.memory) {
            alerts.push({
                type: 'HIGH_MEMORY',
                message: `Memory usage is high: ${this.metrics.memory}% (threshold: ${thresholds.memory}%)`,
                severity: 'WARNING'
            });
        }
        
        // Check Disk
        if (this.metrics.disk > thresholds.disk) {
            alerts.push({
                type: 'HIGH_DISK',
                message: `Disk usage is high: ${this.metrics.disk}% (threshold: ${thresholds.disk}%)`,
                severity: 'WARNING'
            });
        }
        
        // Check Bot Status
        if (this.metrics.bot_status === 'offline') {
            alerts.push({
                type: 'BOT_OFFLINE',
                message: 'Bot is offline or not responding',
                severity: 'CRITICAL'
            });
        }
        
        // Process alerts
        alerts.forEach(alert => {
            this.handleAlert(alert);
        });
        
        this.alerts = alerts;
    }
    
    handleAlert(alert) {
        this.log(`ALERT: ${alert.message}`, alert.severity);
        
        // Log to alerts file
        const alertLog = path.join('logs', 'alerts.log');
        const alertMessage = `[${new Date().toISOString()}] [${alert.severity}] ${alert.type}: ${alert.message}\n`;
        fs.appendFileSync(alertLog, alertMessage, 'utf8');
        
        // Send notifications based on configuration
        if (this.config.alerts.telegram) {
            this.sendTelegramAlert(alert);
        }
        
        if (this.config.alerts.webhook) {
            this.sendWebhookAlert(alert);
        }
    }
    
    async sendTelegramAlert(alert) {
        // Implement Telegram bot notification
        // This requires Telegram bot token and chat ID
        try {
            const telegramConfig = this.config.alerts.telegram_config;
            if (!telegramConfig || !telegramConfig.bot_token || !telegramConfig.chat_id) {
                return;
            }
            
            const message = `🚨 ${alert.severity} ALERT\n${alert.type}\n${alert.message}`;
            
            await axios.post(`https://api.telegram.org/bot${telegramConfig.bot_token}/sendMessage`, {
                chat_id: telegramConfig.chat_id,
                text: message,
                parse_mode: 'HTML'
            });
            
        } catch (error) {
            this.log(`Failed to send Telegram alert: ${error.message}`, 'ERROR');
        }
    }
    
    async sendWebhookAlert(alert) {
        try {
            const webhookUrl = this.config.alerts.webhook_url;
            if (!webhookUrl) return;
            
            await axios.post(webhookUrl, {
                timestamp: new Date().toISOString(),
                alert: alert,
                metrics: this.metrics
            });
            
        } catch (error) {
            this.log(`Failed to send webhook alert: ${error.message}`, 'ERROR');
        }
    }
    
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            metrics: this.metrics,
            alerts: this.alerts,
            system_info: {
                platform: os.platform(),
                arch: os.arch(),
                hostname: os.hostname(),
                node_version: process.version
            }
        };
        
        // Save report to file
        const reportFile = path.join('logs', `report_${new Date().toISOString().split('T')[0]}.json`);
        fs.writeFileSync(reportFile, JSON.stringify(report, null, 2), 'utf8');
        
        this.log(`Report saved: ${reportFile}`);
        
        return report;
    }
    
    async start() {
        this.log('Starting Bot Monitor...');
        
        // Initial check
        await this.performCheck();
        
        // Schedule periodic checks
        setInterval(async () => {
            await this.performCheck();
        }, this.config.check_interval * 1000);
        
        this.log(`Monitor started with ${this.config.check_interval} second interval`);
    }
    
    async performCheck() {
        this.metrics.last_check = new Date().toISOString();
        
        this.log('Performing system check...');
        
        // Check system metrics
        await this.checkSystemMetrics();
        
        // Check bot health
        await this.checkBotHealth();
        
        // Check bot metrics if bot is online
        if (this.metrics.bot_status !== 'offline') {
            await this.checkBotMetrics();
        }
        
        // Check thresholds
        this.checkThresholds();
        
        // Generate report
        this.generateReport();
        
        this.log('System check completed');
    }
    
    stop() {
        this.log('Stopping Bot Monitor...');
        process.exit(0);
    }
}

// Handle command line arguments
const monitor = new BotMonitor();

// Start monitoring
monitor.start().catch(error => {
    console.error('Failed to start monitor:', error);
    process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    monitor.stop();
});

process.on('SIGTERM', () => {
    monitor.stop();
});

// Export for testing
module.exports = BotMonitor;