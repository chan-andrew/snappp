import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import threading

class Dashboard:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.canvas = None
        self.figure = None
        self.alerts_text = None
        self.stats_tree = None
        
    def create_dashboard(self, parent_frame, row, column, rowspan=1):
        """Create the main dashboard interface"""
        # Dashboard frame
        dashboard_frame = ttk.LabelFrame(parent_frame, text="Dashboard", padding="10")
        dashboard_frame.grid(row=row, column=column, rowspan=rowspan, 
                           sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(1, weight=1)
        
        # Control buttons
        controls_frame = ttk.Frame(dashboard_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.update_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # Time range selector
        ttk.Label(controls_frame, text="Time Range:").pack(side=tk.LEFT, padx=(10, 5))
        self.time_range_var = tk.StringVar(value="24h")
        time_range_combo = ttk.Combobox(controls_frame, textvariable=self.time_range_var,
                                       values=["1h", "6h", "24h", "7d", "30d"], width=8, state="readonly")
        time_range_combo.pack(side=tk.LEFT)
        time_range_combo.bind('<<ComboboxSelected>>', lambda e: self.update_data())
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(dashboard_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Graph tab
        graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(graph_frame, text="Score Timeline")
        self.create_graph(graph_frame)
        
        # Alerts tab
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alerts")
        self.create_alerts(alerts_frame)
        
        # Stats tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        self.create_stats(stats_frame)
        
        # Suspicious Activity tab
        suspicious_frame = ttk.Frame(self.notebook)
        self.notebook.add(suspicious_frame, text="🚨 Suspicious Activity")
        self.create_suspicious_activity(suspicious_frame)
    
    def create_graph(self, parent):
        """Create the score timeline graph"""
        # Create matplotlib figure
        plt.style.use('default')
        self.figure = Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty plot
        ax = self.figure.add_subplot(111)
        ax.set_title("Snapchat Score Timeline", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time")
        ax.set_ylabel("Score")
        ax.grid(True, alpha=0.3)
        ax.text(0.5, 0.5, 'No data to display\nAdd users and start tracking', 
                ha='center', va='center', transform=ax.transAxes, 
                fontsize=12, alpha=0.7)
        
        self.canvas.draw()
    
    def create_alerts(self, parent):
        """Create the alerts panel"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Recent Activity Alerts", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Clear Alerts", 
                  command=self.clear_alerts).pack(side=tk.RIGHT)
        
        # Alerts text area with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.alerts_text = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.alerts_text.yview)
        self.alerts_text.configure(yscrollcommand=scrollbar.set)
        
        self.alerts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for styling
        self.alerts_text.tag_configure("warning", foreground="red", font=('Courier', 10, 'bold'))
        self.alerts_text.tag_configure("normal", foreground="green")
        self.alerts_text.tag_configure("timestamp", foreground="blue")
    
    def create_stats(self, parent):
        """Create the statistics panel"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="User Statistics", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Statistics tree with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("User", "Current Score", "Last Change", "Changes Today", "Total +Today", "Last Seen")
        self.stats_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings and widths
        column_widths = {"User": 120, "Current Score": 100, "Last Change": 100, 
                        "Changes Today": 100, "Total +Today": 100, "Last Seen": 100}
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.stats_tree.xview)
        self.stats_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.stats_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def create_suspicious_activity(self, parent):
        """Create the suspicious activity monitoring panel"""
        # Header with warning
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="🚨 Suspicious Activity Monitor", 
                 font=('Arial', 12, 'bold'), foreground='red').pack(side=tk.LEFT)
        
        ttk.Label(header_frame, text="(Score increases without receiving snaps)", 
                 font=('Arial', 10), foreground='gray').pack(side=tk.LEFT, padx=(10, 0))
        
        # Suspicious activity list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("Time", "User", "Score Increase", "Current Score", "Alert Level")
        self.suspicious_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        col_widths = {"Time": 150, "User": 120, "Score Increase": 120, 
                     "Current Score": 120, "Alert Level": 100}
        
        for col in columns:
            self.suspicious_tree.heading(col, text=col)
            self.suspicious_tree.column(col, width=col_widths.get(col, 100), anchor='center')
        
        # Scrollbar for suspicious activity
        sus_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.suspicious_tree.yview)
        self.suspicious_tree.configure(yscrollcommand=sus_scrollbar.set)
        
        self.suspicious_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sus_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for color coding
        self.suspicious_tree.tag_configure("high", background="#ffcccc")
        self.suspicious_tree.tag_configure("medium", background="#ffffcc")
        self.suspicious_tree.tag_configure("low", background="#ccffcc")
    
    def update_data(self):
        """Update all dashboard components with latest data"""
        # Run update in a separate thread to avoid blocking UI
        def update_thread():
            try:
                self.update_graph()
                self.update_alerts()
                self.update_stats()
                self.update_suspicious_activity()
            except Exception as e:
                print(f"Error updating dashboard: {e}")
        
        # Use threading to prevent UI blocking
        threading.Thread(target=update_thread, daemon=True).start()
    
    def update_graph(self):
        """Update the score timeline graph"""
        if not self.figure:
            return
        
        try:
            # Schedule UI update on main thread
            self.parent.after(0, self._update_graph_ui)
        except Exception as e:
            print(f"Error in update_graph: {e}")
    
    def _update_graph_ui(self):
        """Update graph UI - runs on main thread"""
        try:
            # Clear previous plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Get time range
            time_range = self.time_range_var.get()
            hours = self._parse_time_range(time_range)
            
            # Plot data for each user
            users = self.db_manager.get_all_users()
            
            if not users:
                ax.text(0.5, 0.5, 'No users to display\nAdd users to start tracking', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=12, alpha=0.7)
            else:
                colors = plt.cm.Set1(range(len(users)))
                plotted_any = False
                
                for i, username in enumerate(users):
                    scores = self.db_manager.get_user_scores(username, limit=1000)
                    
                    if scores:
                        # Filter by time range
                        cutoff_time = datetime.now() - timedelta(hours=hours)
                        filtered_scores = []
                        
                        for s in scores:
                            try:
                                # Handle different timestamp formats
                                timestamp_str = s['timestamp']
                                if 'T' in timestamp_str:
                                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
                                else:
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                
                                if timestamp >= cutoff_time:
                                    filtered_scores.append((timestamp, s['score']))
                            except Exception as e:
                                print(f"Error parsing timestamp {timestamp_str}: {e}")
                                continue
                        
                        if filtered_scores:
                            # Sort by time
                            filtered_scores.sort(key=lambda x: x[0])
                            times = [item[0] for item in filtered_scores]
                            scores_values = [item[1] for item in filtered_scores]
                            
                            ax.plot(times, scores_values, marker='o', label=username, 
                                   color=colors[i % len(colors)], linewidth=2, markersize=4)
                            plotted_any = True
                
                if not plotted_any:
                    ax.text(0.5, 0.5, f'No data in last {time_range}\nStart tracking to see results', 
                           ha='center', va='center', transform=ax.transAxes, 
                           fontsize=12, alpha=0.7)
            
            ax.set_title("Snapchat Score Timeline", fontsize=14, fontweight='bold')
            ax.set_xlabel("Time")
            ax.set_ylabel("Score")
            ax.grid(True, alpha=0.3)
            
            if len(users) > 0 and any(self.db_manager.get_user_scores(u) for u in users):
                ax.legend()
            
            # Format x-axis
            self.figure.autofmt_xdate()
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating graph UI: {e}")
    
    def update_alerts(self):
        """Update the alerts panel"""
        try:
            self.parent.after(0, self._update_alerts_ui)
        except Exception as e:
            print(f"Error in update_alerts: {e}")
    
    def _update_alerts_ui(self):
        """Update alerts UI - runs on main thread"""
        if not self.alerts_text:
            return
        
        try:
            # Get recent score changes
            alerts = []
            users = self.db_manager.get_all_users()
            
            for username in users:
                changes = self.db_manager.get_score_changes(username, hours=24)
                
                for change in changes:
                    try:
                        # Parse timestamp
                        timestamp_str = change['timestamp']
                        if 'T' in timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
                        else:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        time_str = timestamp.strftime("%H:%M")
                        date_str = timestamp.strftime("%m/%d")
                        
                        if not change['has_new_snap']:
                            alert_text = f"🚨 {date_str} {time_str} - {username}: +{change['change']} points (NO SNAP RECEIVED!)"
                            alert_type = "warning"
                        else:
                            alert_text = f"✅ {date_str} {time_str} - {username}: +{change['change']} points (snap received)"
                            alert_type = "normal"
                        
                        alerts.append((timestamp, alert_text, alert_type))
                        
                    except Exception as e:
                        print(f"Error processing alert: {e}")
                        continue
            
            # Sort by time (newest first)
            alerts.sort(key=lambda x: x[0], reverse=True)
            
            # Update text widget
            self.alerts_text.delete('1.0', tk.END)
            
            if not alerts:
                self.alerts_text.insert(tk.END, "No recent activity to display.\n")
                self.alerts_text.insert(tk.END, "Start tracking users to see alerts here.\n")
            else:
                for timestamp, alert, alert_type in alerts[:50]:  # Show last 50 alerts
                    start_pos = self.alerts_text.index(tk.INSERT)
                    self.alerts_text.insert(tk.END, alert + "\n")
                    end_pos = self.alerts_text.index(tk.INSERT)
                    self.alerts_text.tag_add(alert_type, start_pos, end_pos)
                    self.alerts_text.insert(tk.END, "\n")
                    
        except Exception as e:
            print(f"Error updating alerts UI: {e}")
    
    def update_stats(self):
        """Update the statistics table"""
        try:
            self.parent.after(0, self._update_stats_ui)
        except Exception as e:
            print(f"Error in update_stats: {e}")
    
    def _update_stats_ui(self):
        """Update stats UI - runs on main thread"""
        if not self.stats_tree:
            return
        
        try:
            # Clear existing items
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            # Add user statistics
            users = self.db_manager.get_all_users()
            
            for username in users:
                try:
                    stats = self.db_manager.get_user_stats(username)
                    
                    if stats:
                        # Format last seen time
                        try:
                            last_updated = stats['last_updated']
                            if 'T' in last_updated:
                                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00').replace('+00:00', ''))
                            else:
                                dt = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                            last_seen = dt.strftime("%H:%M")
                        except:
                            last_seen = "Unknown"
                        
                        # Calculate recent change
                        latest_scores = self.db_manager.get_user_scores(username, limit=2)
                        if len(latest_scores) >= 2:
                            last_change = latest_scores[0]['score'] - latest_scores[1]['score']
                            last_change_str = f"+{last_change}" if last_change > 0 else str(last_change)
                        else:
                            last_change_str = "0"
                        
                        self.stats_tree.insert('', tk.END, values=(
                            username,
                            stats['current_score'],
                            last_change_str,
                            stats['changes_today'],
                            f"+{stats['total_change_today']}",
                            last_seen
                        ))
                    else:
                        # User with no data yet
                        self.stats_tree.insert('', tk.END, values=(
                            username, "No data", "0", "0", "+0", "Never"
                        ))
                        
                except Exception as e:
                    print(f"Error processing stats for {username}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error updating stats UI: {e}")
    
    def update_suspicious_activity(self):
        """Update the suspicious activity monitor"""
        try:
            self.parent.after(0, self._update_suspicious_ui)
        except Exception as e:
            print(f"Error in update_suspicious_activity: {e}")
    
    def _update_suspicious_ui(self):
        """Update suspicious activity UI - runs on main thread"""
        if not hasattr(self, 'suspicious_tree') or not self.suspicious_tree:
            return
        
        try:
            # Clear existing items
            for item in self.suspicious_tree.get_children():
                self.suspicious_tree.delete(item)
            
            # Get suspicious activity
            suspicious_activities = self.db_manager.get_suspicious_activity(hours=72)  # Last 3 days
            
            for activity in suspicious_activities:
                try:
                    # Parse timestamp
                    timestamp_str = activity['timestamp']
                    if 'T' in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
                    else:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    time_str = timestamp.strftime("%m/%d %H:%M")
                    
                    # Determine alert level based on score increase
                    score_increase = activity['score_increase']
                    if score_increase >= 50:
                        alert_level = "HIGH"
                        tag = "high"
                    elif score_increase >= 20:
                        alert_level = "MEDIUM"
                        tag = "medium"
                    else:
                        alert_level = "LOW"
                        tag = "low"
                    
                    self.suspicious_tree.insert('', tk.END, values=(
                        time_str,
                        activity['username'],
                        f"+{score_increase}",
                        activity['current_score'],
                        alert_level
                    ), tags=(tag,))
                    
                except Exception as e:
                    print(f"Error processing suspicious activity: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error updating suspicious activity UI: {e}")
    
    def clear_alerts(self):
        """Clear the alerts display"""
        if self.alerts_text:
            self.alerts_text.delete('1.0', tk.END)
            self.alerts_text.insert(tk.END, "Alerts cleared.\n")
    
    def _parse_time_range(self, time_range: str) -> int:
        """Convert time range string to hours"""
        range_map = {
            "1h": 1,
            "6h": 6,
            "24h": 24,
            "7d": 168,
            "30d": 720
        }
        return range_map.get(time_range, 24)