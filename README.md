# 📱 Snapchat Score Tracker

A powerful desktop application for monitoring Snapchat scores and activity patterns to promote transparency in relationships and communication.

## 🌟 Features

- **🔍 Automated Score Tracking**: Monitor multiple users' Snapchat scores at regular intervals (1-60 minutes)
- **📊 Visual Dashboard**: Real-time graphs showing score trends over time
- **🚨 Smart Alerts**: Get notified when scores increase without receiving snaps (suspicious activity)
- **📈 Statistical Analysis**: Detailed stats on daily changes, activity patterns, and more
- **💾 Data Persistence**: Store historical data with SQLite database
- **📤 Data Export**: Export tracking data to JSON for external analysis
- **🎨 Clean Interface**: Intuitive desktop application with tabbed interface

## 🎯 Why Use This Tool?

In today's digital dating landscape, transparency is crucial. This tool helps you:

- **Detect Inconsistent Behavior**: See if someone is active on Snapchat but not responding to you
- **Monitor Activity Patterns**: Understand when someone is most active
- **Promote Honest Communication**: Have data-backed conversations about online behavior
- **Build Trust**: Mutual monitoring can increase relationship transparency

## ⚠️ Important Ethics Notice

This tool is designed for **mutual consent and transparency**. Always:
- Get explicit permission before monitoring someone
- Use this tool to promote honest communication, not surveillance
- Respect privacy and boundaries
- Consider having open conversations about digital behavior instead of secret monitoring

## 🚀 Installation

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Chrome** browser installed
3. **ChromeDriver** installed and in your PATH

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install ChromeDriver

**Windows:**
1. Download ChromeDriver from [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
2. Extract to a folder (e.g., `C:\chromedriver\`)
3. Add the folder to your system PATH

**Mac:**
```bash
brew install chromedriver
```

**Linux:**
```bash
sudo apt-get install chromium-chromedriver
```

### Step 3: Verify Installation

```bash
python main.py
```

## 📖 How to Use

### 1. Initial Setup

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Setup Browser**:
   - Click "Setup Browser" button
   - Chrome will open to Snapchat Web
   - Log in to your Snapchat account
   - Navigate to the main chat/friends page
   - Press Enter in the console when ready

### 2. Add Users to Track

1. Click "Add Users to Track"
2. Enter usernames (one per line)
3. Click "Add Users"

### 3. Configure Settings

- **Check Interval**: Set how often to check scores (1-60 minutes)
- **Time Range**: Choose display range for graphs (1h to 30d)

### 4. Start Tracking

1. Click "Start Tracking"
2. The app will automatically:
   - Check each user's score
   - Detect if you received new snaps
   - Store the data
   - Update the dashboard

## 📊 Dashboard Overview

### Score Timeline Tab
- **Real-time Graphs**: Visual representation of score changes over time
- **Multi-user Support**: Track multiple people simultaneously
- **Time Range Selection**: View data from 1 hour to 30 days

### Alerts Tab
- **🚨 Suspicious Activity**: Score increases without receiving snaps
- **✅ Normal Activity**: Score increases with snap received
- **Time-stamped Events**: See exactly when activities occurred

### Statistics Tab
- **Current Scores**: Latest score for each user
- **Daily Changes**: How much each score changed today
- **Activity Counts**: Number of score changes detected
- **Last Seen**: When data was last updated

### 🚨 Suspicious Activity Tab
- **High Priority Alerts**: Large score increases without snaps
- **Color-coded Warnings**: Visual indicators of suspicious activity levels
- **Historical Data**: View patterns over multiple days

## 🔍 Understanding the Data

### What Different Alerts Mean

**🚨 Red Alert - Suspicious Activity**:
- Score increased without you receiving a snap
- Indicates they're snapping with someone else
- Shows they're active but not communicating with you

**✅ Green Alert - Normal Activity**:
- Score increased and you received a snap
- Normal interaction pattern
- They're including you in their activity

### Score Change Patterns

- **Consistent Small Increases**: Regular social media usage
- **Large Sudden Increases**: Heavy activity periods or group conversations
- **No Changes**: User not active on Snapchat
- **Increases Without Snaps to You**: Potentially concerning for exclusive relationships

## 🛠️ Troubleshooting

### Common Issues

**"Could not find search box"**:
- Ensure you're logged into Snapchat Web
- Try refreshing the browser page
- Check that you're on the main chat page

**"Browser setup failed"**:
- Install/update ChromeDriver
- Check that Chrome browser is installed
- Ensure ChromeDriver is in your system PATH

**"Score extraction failed"**:
- Snapchat's web interface may have changed
- Try refreshing and re-authenticating
- Reduce check frequency to avoid rate limiting

**Performance Issues**:
- Reduce the number of tracked users
- Increase check interval (5+ minutes recommended)
- Close other resource-intensive applications

### Tips for Best Results

1. **Stable Internet**: Ensure reliable internet connection
2. **Don't Close Browser**: Keep the Chrome window open while tracking
3. **Regular Updates**: Restart the app daily for best performance
4. **Reasonable Intervals**: Use 5+ minute intervals to avoid detection
5. **Limit Users**: Track 5-10 users maximum for optimal performance

## 📁 Data Storage

- **Database**: SQLite database (`snapchat_tracker.db`)
- **Location**: Same folder as the application
- **Backup**: Export data regularly using the File menu
- **Privacy**: All data stored locally on your computer

## 🔒 Privacy & Security

- **Local Storage**: All data stays on your computer
- **No Cloud Sync**: No data sent to external servers
- **Encrypted**: Consider encrypting your device for additional security
- **Regular Cleanup**: Use built-in data cleanup features

## ⚖️ Legal Considerations

- **Terms of Service**: Using this tool may violate Snapchat's Terms of Service
- **Personal Use Only**: Intended for personal relationship transparency
- **Consent Required**: Only monitor with explicit permission
- **Local Laws**: Ensure compliance with your local privacy laws

## 🤝 Ethical Usage Guidelines

### ✅ Appropriate Uses
- Mutual monitoring with partner consent
- Verifying claims about activity levels
- Understanding communication patterns
- Building relationship transparency

### ❌ Inappropriate Uses
- Secret surveillance without consent
- Stalking or harassment
- Violating someone's privacy
- Using data to control or manipulate

## 🔧 Advanced Configuration

### Database Management

```python
# Access database directly for custom queries
from src.database import DatabaseManager
db = DatabaseManager()
users = db.get_all_users()
```

### Custom Time Ranges

Modify `dashboard.py` to add custom time ranges:
```python
time_range_combo = ttk.Combobox(values=["1h", "6h", "24h", "7d", "30d", "90d"])
```

## 🐛 Known Limitations

- **Snapchat Updates**: May break when Snapchat updates their interface
- **Rate Limiting**: Too frequent checks may trigger Snapchat's security measures
- **Browser Dependency**: Requires Chrome browser and stable internet
- **Manual Setup**: Requires manual login and initial configuration

## 🔄 Updates and Maintenance

- **Regular Updates**: Check for application updates monthly
- **Data Cleanup**: Use the cleanup feature to remove old data
- **Performance**: Restart the application daily for best performance
- **Backup**: Export important data before major updates

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure Snapchat Web is accessible in your browser
4. Try reducing the number of tracked users

## 📜 Disclaimer

This tool is provided for educational and relationship transparency purposes. Users are responsible for:
- Obtaining proper consent before monitoring
- Complying with applicable laws and regulations
- Using the tool ethically and responsibly
- Respecting others' privacy and boundaries

The developers are not responsible for misuse of this tool or any consequences arising from its use.

---

**Remember**: The goal is healthy, transparent communication. Use this tool to start conversations, not to replace them. 💕