// Snapchat Score Tracker - Content Script
// Runs directly on Snapchat Web pages

class SnapchatTracker {
    constructor() {
        this.isTracking = false;
        this.trackedUsers = [];
        this.scoreData = {};
        this.checkInterval = null;
        this.initializeTracker();
    }

    async initializeTracker() {
        console.log('🔍 Snapchat Score Tracker initialized');
        
        // Load settings from storage
        await this.loadSettings();
        
        // Start monitoring if enabled
        if (this.isTracking) {
            this.startTracking();
        }
        
        // Listen for messages from popup
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleMessage(request, sendResponse);
            return true; // Keep message channel open for async response
        });
        
        // Inject tracking UI
        this.injectTrackingUI();
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.local.get(['isTracking', 'trackedUsers', 'scoreData']);
            this.isTracking = result.isTracking || false;
            this.trackedUsers = result.trackedUsers || [];
            this.scoreData = result.scoreData || {};
            
            console.log('📊 Loaded settings:', {
                tracking: this.isTracking,
                users: this.trackedUsers.length,
                scores: Object.keys(this.scoreData).length
            });
        } catch (error) {
            console.error('❌ Error loading settings:', error);
        }
    }

    async saveSettings() {
        try {
            await chrome.storage.local.set({
                isTracking: this.isTracking,
                trackedUsers: this.trackedUsers,
                scoreData: this.scoreData
            });
        } catch (error) {
            console.error('❌ Error saving settings:', error);
        }
    }

    handleMessage(request, sendResponse) {
        switch (request.action) {
            case 'getStatus':
                sendResponse({
                    isTracking: this.isTracking,
                    trackedUsers: this.trackedUsers,
                    scoreData: this.scoreData,
                    alerts: this.getRecentAlerts()
                });
                break;
                
            case 'startTracking':
                this.startTracking();
                sendResponse({ success: true });
                break;
                
            case 'stopTracking':
                this.stopTracking();
                sendResponse({ success: true });
                break;
                
            case 'addUser':
                this.addUser(request.username);
                sendResponse({ success: true });
                break;
                
            case 'removeUser':
                this.removeUser(request.username);
                sendResponse({ success: true });
                break;
                
            case 'clearUsers':
                this.clearUsers();
                sendResponse({ success: true });
                break;
                
            case 'clearAlerts':
                this.clearAlerts();
                sendResponse({ success: true });
                break;
                
            default:
                sendResponse({ error: 'Unknown action' });
        }
    }

    startTracking() {
        if (this.isTracking) return;
        
        this.isTracking = true;
        console.log('✅ Started tracking');
        
        // Check scores every 5 minutes
        this.checkInterval = setInterval(() => {
            this.checkAllUsers();
        }, 5 * 60 * 1000);
        
        // Initial check
        this.checkAllUsers();
        this.saveSettings();
        this.updateTrackingUI();
    }

    stopTracking() {
        if (!this.isTracking) return;
        
        this.isTracking = false;
        console.log('⛔ Stopped tracking');
        
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        
        this.saveSettings();
        this.updateTrackingUI();
    }

    addUser(username) {
        if (!username || this.trackedUsers.includes(username)) return;
        
        this.trackedUsers.push(username);
        console.log(`👤 Added user: ${username}`);
        
        // Initialize score data for new user
        if (!this.scoreData[username]) {
            this.scoreData[username] = {
                scores: [],
                alerts: []
            };
        }
        
        this.saveSettings();
        
        // Check this user immediately if tracking is active
        if (this.isTracking) {
            this.checkUserScore(username);
        }
    }

    removeUser(username) {
        const index = this.trackedUsers.indexOf(username);
        if (index > -1) {
            this.trackedUsers.splice(index, 1);
            console.log(`❌ Removed user: ${username}`);
            this.saveSettings();
        }
    }

    clearUsers() {
        this.trackedUsers = [];
        this.scoreData = {};
        console.log('🗑️ Cleared all users');
        this.saveSettings();
    }

    clearAlerts() {
        for (const username in this.scoreData) {
            this.scoreData[username].alerts = [];
        }
        console.log('🗑️ Cleared all alerts');
        this.saveSettings();
    }

    async checkAllUsers() {
        if (!this.isTracking || this.trackedUsers.length === 0) return;
        
        console.log(`🔍 Checking ${this.trackedUsers.length} users...`);
        
        for (const username of this.trackedUsers) {
            try {
                await this.checkUserScore(username);
                // Wait 2 seconds between users to avoid rate limiting
                await this.sleep(2000);
            } catch (error) {
                console.error(`❌ Error checking ${username}:`, error);
            }
        }
    }

    async checkUserScore(username) {
        try {
            // Search for the user
            const userFound = await this.searchForUser(username);
            if (!userFound) {
                console.log(`❌ User not found: ${username}`);
                return;
            }

            // Extract score from current page
            const scoreInfo = this.extractScoreFromPage();
            if (!scoreInfo) {
                console.log(`❌ Could not extract score for: ${username}`);
                return;
            }

            // Store the score data
            this.storeScoreData(username, scoreInfo);
            
            console.log(`📊 ${username}: ${scoreInfo.score} (new snap: ${scoreInfo.hasNewSnap})`);
            
        } catch (error) {
            console.error(`❌ Error checking score for ${username}:`, error);
        }
    }

    async searchForUser(username) {
        // Look for search input
        const searchSelectors = [
            'input[placeholder*="Search"]',
            'input[placeholder*="search"]',
            '[data-testid*="search"] input',
            '.search-input',
            'input[type="text"]'
        ];

        let searchInput = null;
        for (const selector of searchSelectors) {
            searchInput = document.querySelector(selector);
            if (searchInput && searchInput.offsetParent !== null) {
                break;
            }
        }

        if (!searchInput) {
            console.log('❌ Search input not found');
            return false;
        }

        // Clear and search for username
        searchInput.focus();
        searchInput.value = '';
        await this.sleep(500);
        
        // Type username character by character
        for (const char of username) {
            searchInput.value += char;
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            await this.sleep(100);
        }

        // Wait for search results
        await this.sleep(2000);

        // Look for user in results and click
        const userFound = await this.findAndClickUser(username);
        return userFound;
    }

    async findAndClickUser(username) {
        // Try multiple strategies to find the user
        const strategies = [
            // Strategy 1: Look for exact text matches
            () => {
                const elements = Array.from(document.querySelectorAll('*')).filter(el => 
                    el.textContent && 
                    el.textContent.toLowerCase().includes(username.toLowerCase()) &&
                    el.offsetParent !== null
                );
                return elements.find(el => this.isClickable(el));
            },
            
            // Strategy 2: Look for friend/user list items
            () => {
                const selectors = [
                    '[data-testid*="friend"]',
                    '[data-testid*="user"]',
                    '.friend-item',
                    '.user-item',
                    '[role="button"]'
                ];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        if (el.textContent && el.textContent.toLowerCase().includes(username.toLowerCase())) {
                            return el;
                        }
                    }
                }
                return null;
            }
        ];

        for (const strategy of strategies) {
            const element = strategy();
            if (element) {
                try {
                    element.click();
                    await this.sleep(3000); // Wait for profile to load
                    return true;
                } catch (error) {
                    console.log('Click failed, trying next strategy...');
                }
            }
        }

        return false;
    }

    isClickable(element) {
        const style = window.getComputedStyle(element);
        return (
            element.tagName === 'BUTTON' ||
            element.tagName === 'A' ||
            style.cursor === 'pointer' ||
            element.onclick ||
            element.getAttribute('role') === 'button'
        );
    }

    extractScoreFromPage() {
        // Multiple strategies to find the score
        const strategies = [
            // Strategy 1: Look for score-related selectors
            () => {
                const selectors = [
                    '[data-testid*="score"]',
                    '.snap-score',
                    '*[class*="score"]',
                    '*[aria-label*="score"]'
                ];
                
                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        const score = this.parseScore(element.textContent);
                        if (score !== null) return { score, hasNewSnap: this.checkForNewSnap() };
                    }
                }
                return null;
            },
            
            // Strategy 2: Look for numbers in profile area
            () => {
                const profileSelectors = [
                    '.profile',
                    '[data-testid*="profile"]',
                    '.user-info',
                    '.friend-profile'
                ];
                
                for (const selector of profileSelectors) {
                    const container = document.querySelector(selector);
                    if (container) {
                        const numbers = this.extractNumbersFromElement(container);
                        for (const num of numbers) {
                            if (num >= 100 && num <= 10000000) { // Reasonable score range
                                return { score: num, hasNewSnap: this.checkForNewSnap() };
                            }
                        }
                    }
                }
                return null;
            },
            
            // Strategy 3: Look for any large numbers on page
            () => {
                const allElements = document.querySelectorAll('*');
                for (const element of allElements) {
                    if (element.children.length === 0) { // Text nodes only
                        const score = this.parseScore(element.textContent);
                        if (score !== null && score >= 1000 && score <= 10000000) {
                            return { score, hasNewSnap: this.checkForNewSnap() };
                        }
                    }
                }
                return null;
            }
        ];

        for (const strategy of strategies) {
            const result = strategy();
            if (result) return result;
        }

        return null;
    }

    parseScore(text) {
        if (!text) return null;
        
        // Remove all non-digit characters and parse
        const cleaned = text.replace(/[^\d]/g, '');
        if (cleaned.length >= 3 && cleaned.length <= 8) {
            const score = parseInt(cleaned);
            return isNaN(score) ? null : score;
        }
        return null;
    }

    extractNumbersFromElement(element) {
        const text = element.textContent || '';
        const numbers = text.match(/\d{3,8}/g);
        return numbers ? numbers.map(n => parseInt(n)) : [];
    }

    checkForNewSnap() {
        // Look for indicators of new snaps
        const indicators = [
            '.new-snap',
            '.unread',
            '.notification',
            '*[class*="new"]',
            '*[class*="unread"]',
            '*[class*="notification"]'
        ];

        for (const selector of indicators) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                if (el.offsetParent !== null) { // Visible
                    return true;
                }
            }
        }

        return false;
    }

    storeScoreData(username, scoreInfo) {
        if (!this.scoreData[username]) {
            this.scoreData[username] = { scores: [], alerts: [] };
        }

        const userData = this.scoreData[username];
        const timestamp = Date.now();
        
        // Get previous score
        const lastEntry = userData.scores[userData.scores.length - 1];
        const previousScore = lastEntry ? lastEntry.score : null;
        
        // Add new score entry
        userData.scores.push({
            score: scoreInfo.score,
            hasNewSnap: scoreInfo.hasNewSnap,
            timestamp: timestamp
        });

        // Keep only last 100 entries per user
        if (userData.scores.length > 100) {
            userData.scores = userData.scores.slice(-100);
        }

        // Check for suspicious activity
        if (previousScore !== null) {
            const scoreIncrease = scoreInfo.score - previousScore;
            if (scoreIncrease > 0 && !scoreInfo.hasNewSnap) {
                // Suspicious: score increased but no new snap received
                const alert = {
                    type: 'suspicious',
                    message: `${username} score increased by ${scoreIncrease} (NO snap received!)`,
                    scoreIncrease: scoreIncrease,
                    timestamp: timestamp
                };
                
                userData.alerts.push(alert);
                console.log(`🚨 SUSPICIOUS ACTIVITY: ${alert.message}`);
                
                // Show browser notification
                this.showNotification(alert.message, 'suspicious');
            } else if (scoreIncrease > 0 && scoreInfo.hasNewSnap) {
                // Normal: score increased and snap received
                const alert = {
                    type: 'normal',
                    message: `${username} score increased by ${scoreIncrease} (snap received)`,
                    scoreIncrease: scoreIncrease,
                    timestamp: timestamp
                };
                
                userData.alerts.push(alert);
                console.log(`✅ Normal activity: ${alert.message}`);
            }
        }

        // Keep only last 50 alerts per user
        if (userData.alerts.length > 50) {
            userData.alerts = userData.alerts.slice(-50);
        }

        this.saveSettings();
    }

    showNotification(message, type) {
        try {
            const title = type === 'suspicious' ? '🚨 Suspicious Activity' : '✅ Normal Activity';
            chrome.runtime.sendMessage({
                action: 'showNotification',
                title: title,
                message: message,
                type: type
            });
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }

    getRecentAlerts() {
        const allAlerts = [];
        for (const username in this.scoreData) {
            const userAlerts = this.scoreData[username].alerts || [];
            allAlerts.push(...userAlerts);
        }
        
        // Sort by timestamp (newest first) and return last 20
        return allAlerts
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, 20);
    }

    injectTrackingUI() {
        // Create a small floating indicator
        const indicator = document.createElement('div');
        indicator.id = 'snaptracker-indicator';
        indicator.innerHTML = '📱';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            z-index: 10000;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        `;
        
        indicator.addEventListener('mouseenter', () => {
            indicator.style.transform = 'scale(1.1)';
        });
        
        indicator.addEventListener('mouseleave', () => {
            indicator.style.transform = 'scale(1)';
        });
        
        indicator.addEventListener('click', () => {
            // Open extension popup (this will be handled by the browser)
            console.log('Tracker indicator clicked');
        });
        
        document.body.appendChild(indicator);
        this.updateTrackingUI();
    }

    updateTrackingUI() {
        const indicator = document.getElementById('snaptracker-indicator');
        if (indicator) {
            if (this.isTracking) {
                indicator.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
                indicator.title = `Tracking ${this.trackedUsers.length} users`;
            } else {
                indicator.style.background = 'linear-gradient(135deg, #f44336, #d32f2f)';
                indicator.title = 'Tracking inactive';
            }
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the tracker when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new SnapchatTracker();
    });
} else {
    new SnapchatTracker();
}