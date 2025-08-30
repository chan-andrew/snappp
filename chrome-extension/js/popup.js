// Snapchat Score Tracker - Popup Script

class TrackerPopup {
    constructor() {
        this.isTracking = false;
        this.trackedUsers = [];
        this.scoreData = {};
        this.alerts = [];
        this.initializePopup();
    }

    async initializePopup() {
        // Get current tab to send messages to content script
        this.currentTab = await this.getCurrentTab();
        
        // Load current status
        await this.loadStatus();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Update UI
        this.updateUI();
        
        // Auto-refresh every 5 seconds
        setInterval(() => {
            this.loadStatus();
        }, 5000);
    }

    async getCurrentTab() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        return tab;
    }

    async sendMessageToContent(message) {
        try {
            if (this.currentTab && this.currentTab.url.includes('web.snapchat.com')) {
                return await chrome.tabs.sendMessage(this.currentTab.id, message);
            } else {
                throw new Error('Not on Snapchat Web');
            }
        } catch (error) {
            console.error('Error sending message to content script:', error);
            return { error: error.message };
        }
    }

    async loadStatus() {
        try {
            const response = await this.sendMessageToContent({ action: 'getStatus' });
            
            if (response && !response.error) {
                this.isTracking = response.isTracking;
                this.trackedUsers = response.trackedUsers || [];
                this.scoreData = response.scoreData || {};
                this.alerts = response.alerts || [];
                this.updateUI();
            }
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }

    setupEventListeners() {
        // Toggle tracking button
        document.getElementById('toggleTracking').addEventListener('click', () => {
            this.toggleTracking();
        });

        // Add user button
        document.getElementById('addUser').addEventListener('click', () => {
            this.addUser();
        });

        // Add user on Enter key
        document.getElementById('usernameInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addUser();
            }
        });

        // Clear users button
        document.getElementById('clearUsers').addEventListener('click', () => {
            this.clearUsers();
        });

        // Clear alerts button
        document.getElementById('clearAlerts').addEventListener('click', () => {
            this.clearAlerts();
        });
    }

    async toggleTracking() {
        const action = this.isTracking ? 'stopTracking' : 'startTracking';
        const response = await this.sendMessageToContent({ action });
        
        if (response && response.success) {
            this.isTracking = !this.isTracking;
            this.updateUI();
        }
    }

    async addUser() {
        const input = document.getElementById('usernameInput');
        const username = input.value.trim();
        
        if (!username) return;
        
        if (this.trackedUsers.includes(username)) {
            this.showMessage('User already being tracked', 'warning');
            input.value = '';
            return;
        }

        const response = await this.sendMessageToContent({ 
            action: 'addUser', 
            username 
        });
        
        if (response && response.success) {
            this.trackedUsers.push(username);
            input.value = '';
            this.updateUI();
            this.showMessage(`Added ${username} to tracking`, 'success');
        }
    }

    async clearUsers() {
        if (this.trackedUsers.length === 0) return;
        
        if (confirm('Clear all tracked users?')) {
            const response = await this.sendMessageToContent({ action: 'clearUsers' });
            
            if (response && response.success) {
                this.trackedUsers = [];
                this.scoreData = {};
                this.updateUI();
                this.showMessage('Cleared all users', 'success');
            }
        }
    }

    async clearAlerts() {
        if (this.alerts.length === 0) return;
        
        const response = await this.sendMessageToContent({ action: 'clearAlerts' });
        
        if (response && response.success) {
            this.alerts = [];
            this.updateUI();
            this.showMessage('Cleared all alerts', 'success');
        }
    }

    updateUI() {
        this.updateStatus();
        this.updateUserList();
        this.updateStatistics();
        this.updateAlerts();
    }

    updateStatus() {
        const statusElement = document.getElementById('status');
        const toggleButton = document.getElementById('toggleTracking');
        
        if (this.currentTab && !this.currentTab.url.includes('web.snapchat.com')) {
            statusElement.textContent = 'Not on Snapchat Web';
            statusElement.className = 'status inactive';
            toggleButton.textContent = 'Go to Snapchat';
            toggleButton.onclick = () => {
                chrome.tabs.update(this.currentTab.id, { url: 'https://web.snapchat.com/' });
            };
            return;
        }
        
        if (this.isTracking) {
            statusElement.textContent = `Tracking ${this.trackedUsers.length} users`;
            statusElement.className = 'status active';
            toggleButton.textContent = 'Stop Tracking';
        } else {
            statusElement.textContent = 'Tracking Inactive';
            statusElement.className = 'status inactive';
            toggleButton.textContent = 'Start Tracking';
        }
    }

    updateUserList() {
        const userListElement = document.getElementById('userList');
        
        if (this.trackedUsers.length === 0) {
            userListElement.innerHTML = '<div class="loading">No users added yet</div>';
            return;
        }
        
        userListElement.innerHTML = this.trackedUsers.map(username => {
            const userData = this.scoreData[username];
            const latestScore = userData && userData.scores.length > 0 
                ? userData.scores[userData.scores.length - 1].score 
                : 'Unknown';
            
            return `
                <div class="user-item">
                    <div>
                        <div class="user-name">${username}</div>
                        <div class="user-score">Score: ${latestScore}</div>
                    </div>
                    <button onclick="tracker.removeUser('${username}')">×</button>
                </div>
            `;
        }).join('');
    }

    async removeUser(username) {
        const response = await this.sendMessageToContent({ 
            action: 'removeUser', 
            username 
        });
        
        if (response && response.success) {
            this.trackedUsers = this.trackedUsers.filter(u => u !== username);
            delete this.scoreData[username];
            this.updateUI();
            this.showMessage(`Removed ${username}`, 'success');
        }
    }

    updateStatistics() {
        document.getElementById('totalUsers').textContent = this.trackedUsers.length;
        document.getElementById('totalAlerts').textContent = this.alerts.length;
    }

    updateAlerts() {
        const alertListElement = document.getElementById('alertList');
        
        if (this.alerts.length === 0) {
            alertListElement.innerHTML = '<div class="loading">No alerts yet</div>';
            return;
        }
        
        // Show last 10 alerts
        const recentAlerts = this.alerts.slice(0, 10);
        
        alertListElement.innerHTML = recentAlerts.map(alert => {
            const timeStr = new Date(alert.timestamp).toLocaleTimeString();
            const alertClass = alert.type === 'suspicious' ? 'alert-suspicious' : 'alert-normal';
            const emoji = alert.type === 'suspicious' ? '🚨' : '✅';
            
            return `
                <div class="${alertClass} alert-item">
                    ${emoji} ${timeStr}<br>
                    ${alert.message}
                </div>
            `;
        }).join('');
    }

    showMessage(message, type) {
        // Create temporary message element
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.style.cssText = `
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#4CAF50' : '#FF9800'};
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 10000;
        `;
        
        document.body.appendChild(messageElement);
        
        setTimeout(() => {
            document.body.removeChild(messageElement);
        }, 3000);
    }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.tracker = new TrackerPopup();
});