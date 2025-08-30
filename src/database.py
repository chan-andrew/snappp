import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "snapchat_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Score entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS score_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    score INTEGER NOT NULL,
                    has_new_snap BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_score_entries_timestamp ON score_entries(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_score_entries_user_id ON score_entries(user_id)')
            
            conn.commit()
    
    def add_user(self, username: str) -> bool:
        """Add a new user to track"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error adding user: {e}")
            return False
    
    def get_user_id(self, username: str) -> Optional[int]:
        """Get user ID by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def add_score_entry(self, username: str, score: int, has_new_snap: bool = False) -> bool:
        """Add a new score entry for a user"""
        user_id = self.get_user_id(username)
        if not user_id:
            # Auto-add user if not exists
            self.add_user(username)
            user_id = self.get_user_id(username)
            if not user_id:
                return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO score_entries (user_id, score, has_new_snap)
                    VALUES (?, ?, ?)
                ''', (user_id, score, has_new_snap))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error adding score entry: {e}")
            return False
    
    def get_user_scores(self, username: str, limit: int = 100) -> List[Dict]:
        """Get recent scores for a user"""
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT score, has_new_snap, timestamp
                FROM score_entries
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            return [
                {
                    'score': row[0],
                    'has_new_snap': bool(row[1]),
                    'timestamp': row[2]
                }
                for row in cursor.fetchall()
            ]
    
    def get_latest_score(self, username: str) -> Optional[Dict]:
        """Get the most recent score for a user"""
        scores = self.get_user_scores(username, limit=1)
        return scores[0] if scores else None
    
    def get_score_changes(self, username: str, hours: int = 24) -> List[Dict]:
        """Get score changes within the last N hours"""
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s1.score, s1.has_new_snap, s1.timestamp, s2.score as prev_score
                FROM score_entries s1
                LEFT JOIN score_entries s2 ON s2.user_id = s1.user_id 
                    AND s2.timestamp < s1.timestamp
                    AND s2.id = (
                        SELECT MAX(id) FROM score_entries s3 
                        WHERE s3.user_id = s1.user_id AND s3.timestamp < s1.timestamp
                    )
                WHERE s1.user_id = ? 
                AND s1.timestamp >= datetime('now', '-{} hours')
                ORDER BY s1.timestamp
            '''.format(hours), (user_id,))
            
            changes = []
            for row in cursor.fetchall():
                if row[3] is not None:  # prev_score exists
                    change = row[0] - row[3]
                    if change > 0:
                        changes.append({
                            'timestamp': row[2],
                            'score': row[0],
                            'change': change,
                            'has_new_snap': bool(row[1])
                        })
            
            return changes
    
    def get_all_users(self) -> List[str]:
        """Get all tracked usernames"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users ORDER BY username')
            return [row[0] for row in cursor.fetchall()]
    
    def get_user_stats(self, username: str) -> Dict:
        """Get comprehensive stats for a user"""
        user_scores = self.get_user_scores(username, limit=1000)
        if not user_scores:
            return {}
        
        latest = user_scores[0]
        changes_today = self.get_score_changes(username, hours=24)
        
        total_change_today = sum(change['change'] for change in changes_today)
        changes_count_today = len(changes_today)
        
        # Get score from 24 hours ago for daily change calculation
        yesterday_score = None
        if len(user_scores) > 1:
            yesterday_score = user_scores[-1]['score']
            daily_change = latest['score'] - yesterday_score
        else:
            daily_change = 0
        
        return {
            'username': username,
            'current_score': latest['score'],
            'last_updated': latest['timestamp'],
            'changes_today': changes_count_today,
            'total_change_today': total_change_today,
            'daily_change': daily_change,
            'has_recent_snap': latest['has_new_snap']
        }
    
    def export_data(self) -> Dict:
        """Export all data to a dictionary"""
        data = {
            'export_date': datetime.now().isoformat(),
            'users': {}
        }
        
        for username in self.get_all_users():
            data['users'][username] = {
                'scores': self.get_user_scores(username, limit=1000),
                'recent_changes': self.get_score_changes(username, hours=168),  # 1 week
                'stats': self.get_user_stats(username)
            }
        
        return data
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Remove data older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM score_entries 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            conn.commit()
            return cursor.rowcount
    
    def get_suspicious_activity(self, hours: int = 24) -> List[Dict]:
        """Get suspicious activity (score increases without new snaps)"""
        suspicious = []
        
        for username in self.get_all_users():
            changes = self.get_score_changes(username, hours)
            
            for change in changes:
                if not change['has_new_snap'] and change['change'] > 0:
                    suspicious.append({
                        'username': username,
                        'timestamp': change['timestamp'],
                        'score_increase': change['change'],
                        'current_score': change['score']
                    })
        
        return sorted(suspicious, key=lambda x: x['timestamp'], reverse=True)