// Snapchat Score Tracker - Background Service Worker

class TrackerBackground {
    constructor() {
        this.setupMessageListener();
        this.setupNotifications();
        console.log('🔧 Background service worker initialized');
    }

    setupMessageListener() {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sender, sendResponse);
            return true; // Keep message channel open for async response
        });
    }

    setupNotifications() {
        // Request notification permission
        if (typeof Notification !== 'undefined') {
            Notification.requestPermission();
        }
    }

    handleMessage(request, sender, sendResponse) {
        switch (request.action) {
            case 'showNotification':
                this.showNotification(request.title, request.message, request.type);
                sendResponse({ success: true });
                break;
                
            case 'getStorageData':
                this.getStorageData(request.keys).then(data => {
                    sendResponse({ data });
                });
                break;
                
            case 'setStorageData':
                this.setStorageData(request.data).then(() => {
                    sendResponse({ success: true });
                });
                break;
                
            default:
                sendResponse({ error: 'Unknown action' });
        }
    }

    showNotification(title, message, type) {
        try {
            // Create Chrome notification
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: title,
                message: message,
                priority: type === 'suspicious' ? 2 : 1
            });
            
            console.log(`📢 Notification: ${title} - ${message}`);
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }

    async getStorageData(keys) {
        try {
            return await chrome.storage.local.get(keys);
        } catch (error) {
            console.error('Error getting storage data:', error);
            return {};
        }
    }

    async setStorageData(data) {
        try {
            await chrome.storage.local.set(data);
            return true;
        } catch (error) {
            console.error('Error setting storage data:', error);
            return false;
        }
    }

    // Cleanup old data periodically
    async cleanupOldData() {
        try {
            const data = await chrome.storage.local.get(['scoreData']);
            const scoreData = data.scoreData || {};
            
            const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
            
            for (const username in scoreData) {
                const userData = scoreData[username];
                
                // Remove old score entries (keep last 100)
                if (userData.scores && userData.scores.length > 100) {
                    userData.scores = userData.scores.slice(-100);
                }
                
                // Remove old alerts (keep last 50)
                if (userData.alerts && userData.alerts.length > 50) {
                    userData.alerts = userData.alerts.slice(-50);
                }
                
                // Remove very old entries
                if (userData.scores) {
                    userData.scores = userData.scores.filter(entry => 
                        entry.timestamp > thirtyDaysAgo
                    );
                }
                
                if (userData.alerts) {
                    userData.alerts = userData.alerts.filter(alert => 
                        alert.timestamp > thirtyDaysAgo
                    );
                }
            }
            
            await chrome.storage.local.set({ scoreData });
            console.log('🧹 Cleaned up old data');
            
        } catch (error) {
            console.error('Error cleaning up data:', error);
        }
    }
}

// Initialize background service
const trackerBackground = new TrackerBackground();

// Cleanup data daily
setInterval(() => {
    trackerBackground.cleanupOldData();
}, 24 * 60 * 60 * 1000); // 24 hours

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('📱 Snapchat Score Tracker installed');
        
        // Open setup page
        chrome.tabs.create({
            url: 'https://web.snapchat.com/'
        });
    }
});