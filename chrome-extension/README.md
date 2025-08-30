# 📱 Snapchat Score Tracker - Chrome Extension

A Chrome extension for monitoring Snapchat scores and detecting suspicious activity for relationship transparency.

## 🎯 **Features**

- **🔍 Real-time Monitoring**: Automatically tracks scores as you browse Snapchat Web
- **🚨 Suspicious Activity Alerts**: Notifies when scores increase without receiving snaps
- **📊 Score Timeline**: Visual tracking of score changes over time
- **💾 Local Storage**: All data stored locally in your browser
- **🔔 Browser Notifications**: Get alerts even when not actively browsing
- **⚡ Lightning Fast**: No external automation, works directly within Snapchat

## 🚀 **Installation**

### **Option 1: Load as Developer Extension**

1. **Open Chrome Extensions**:
   - Go to `chrome://extensions/`
   - Or click Chrome menu → More Tools → Extensions

2. **Enable Developer Mode**:
   - Toggle "Developer mode" in the top right

3. **Load Extension**:
   - Click "Load unpacked"
   - Select the `chrome-extension` folder

4. **Pin Extension**:
   - Click the puzzle piece icon in Chrome toolbar
   - Pin "Snapchat Score Tracker"

### **Option 2: Package and Install**

1. **Package Extension**:
   - Go to `chrome://extensions/`
   - Click "Pack extension"
   - Select the `chrome-extension` folder
   - This creates a `.crx` file

2. **Install Package**:
   - Drag the `.crx` file to Chrome extensions page
   - Click "Add extension"

## 📖 **How to Use**

### **1. Setup**
1. **Go to Snapchat Web**: Navigate to https://web.snapchat.com/
2. **Log In**: Sign into your Snapchat account
3. **Extension Ready**: You'll see a 📱 icon in the top-right corner

### **2. Add Users to Track**
1. **Click Extension Icon**: Click the 📱 in your Chrome toolbar
2. **Add Username**: Enter Snapchat username in the input field
3. **Start Tracking**: Click "Start Tracking" button

### **3. Monitor Activity**
- **Real-time Updates**: Scores update automatically as you browse
- **Visual Indicator**: The 📱 icon changes color based on tracking status
  - 🟢 Green: Tracking active
  - 🔴 Red: Tracking inactive
- **Popup Dashboard**: Click extension icon to see detailed stats

## 🎮 **How It Works**

### **Automatic Detection**
The extension runs invisibly in the background and:
1. **Monitors Page Changes**: Detects when you visit user profiles
2. **Extracts Scores**: Automatically reads score information
3. **Compares Changes**: Tracks increases and decreases
4. **Detects New Snaps**: Checks for new message indicators
5. **Stores Data**: Saves everything locally in browser storage

### **Smart Alerts**
- **🚨 Suspicious Activity**: Score increased but no snap received
- **✅ Normal Activity**: Score increased and snap received
- **📊 Statistical Tracking**: Historical data and patterns

## 🔍 **Understanding the Data**

### **Alert Types**

**🚨 Suspicious Activity (Red)**:
- Someone's score increased
- You didn't receive a snap from them
- **Indicates**: They're snapping with others, not you
- **Meaning**: Potential red flag for exclusive relationships

**✅ Normal Activity (Green)**:
- Someone's score increased
- You received a snap from them
- **Indicates**: They're including you in their activity
- **Meaning**: Healthy communication pattern

### **What Score Changes Mean**
- **Small increases (1-5 points)**: Individual snaps sent/received
- **Medium increases (5-20 points)**: Multiple conversations or group snaps
- **Large increases (20+ points)**: Heavy activity period or streaks
- **No changes**: User not active on Snapchat

## ⚙️ **Extension Features**

### **Popup Interface**
- **📊 Live Statistics**: Current tracking status and user count
- **👥 User Management**: Add/remove users easily
- **🚨 Recent Alerts**: See latest suspicious activity
- **⚡ Quick Controls**: Start/stop tracking with one click

### **Background Monitoring**
- **🔄 Continuous Tracking**: Works even when popup is closed
- **💾 Data Persistence**: Retains data between browser sessions
- **🧹 Auto Cleanup**: Removes old data to save space
- **🔔 Browser Notifications**: System notifications for important alerts

## 🔒 **Privacy & Security**

### **Local Data Only**
- **No External Servers**: All data stays in your browser
- **No Account Required**: No sign-ups or external accounts
- **Private Storage**: Uses Chrome's secure local storage
- **User Control**: You can clear data anytime

### **Permissions Used**
- **`storage`**: Store tracking data locally
- **`activeTab`**: Access current Snapchat tab
- **`notifications`**: Show browser notifications
- **`web.snapchat.com`**: Only works on Snapchat Web

## 🛠️ **Troubleshooting**

### **Extension Not Working**
1. **Check Permissions**: Ensure extension has proper permissions
2. **Refresh Snapchat**: Reload the Snapchat Web page
3. **Re-enable Extension**: Disable and re-enable in Chrome extensions
4. **Check Console**: Open DevTools to see any error messages

### **Scores Not Updating**
1. **Navigate to Profiles**: The extension detects scores when you visit profiles
2. **Manual Navigation**: Browse to users' profiles manually to trigger detection
3. **Wait for Updates**: Score changes may take time to reflect

### **Notifications Not Showing**
1. **Grant Permission**: Allow notifications when prompted
2. **Check Chrome Settings**: Ensure notifications are enabled for the extension
3. **Browser Focus**: Some notifications only show when Chrome is active

## ⚖️ **Ethical Usage**

### **✅ Appropriate Uses**
- Mutual monitoring with partner consent
- Verifying communication patterns in relationships
- Understanding social media behavior
- Building transparency and trust

### **❌ Inappropriate Uses**
- Secret surveillance without consent
- Stalking or harassment
- Violating someone's privacy
- Using data to manipulate or control

## 🔧 **Advanced Configuration**

### **Customizing Check Intervals**
The extension checks for updates when you naturally browse Snapchat. For more frequent checking, you can modify the intervals in the source code:

```javascript
// In content.js, change this line:
this.checkInterval = setInterval(() => {
    this.checkAllUsers();
}, 5 * 60 * 1000); // 5 minutes -> change to desired interval
```

### **Data Export**
To export your tracking data:
1. Open Chrome DevTools (F12)
2. Go to Application → Storage → Local Storage
3. Find extension data and export as needed

## 📊 **Data Storage**

The extension stores:
- **User Lists**: Usernames you're tracking
- **Score History**: Historical score data (last 100 entries per user)
- **Alert History**: Activity alerts (last 50 per user)
- **Settings**: Tracking preferences and configuration

Data is automatically cleaned up after 30 days to save space.

## 🆘 **Support**

### **Common Issues**
- **Snapchat Updates**: If Snapchat changes their interface, the extension may need updates
- **Browser Updates**: Chrome updates rarely break extensions, but may require refresh
- **Performance**: Tracking many users may slow down browsing

### **Getting Help**
1. Check this README for solutions
2. Look in Chrome DevTools console for error messages
3. Try disabling and re-enabling the extension
4. Clear extension data and start fresh if needed

## 📝 **Changelog**

### **Version 1.0**
- Initial release
- Real-time score tracking
- Suspicious activity detection
- Browser notifications
- Local data storage
- Popup interface

## ⚠️ **Disclaimer**

This extension is provided for educational and relationship transparency purposes. Users are responsible for:
- Obtaining proper consent before monitoring
- Complying with applicable laws and regulations
- Using the tool ethically and responsibly
- Respecting others' privacy and boundaries

The developers are not responsible for misuse or any consequences arising from use of this extension.

---

**Remember**: The goal is healthy, transparent communication. Use this tool to start conversations, not to replace them. 💕