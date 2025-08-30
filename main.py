import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sqlite3
from datetime import datetime
import json
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from automation import SnapchatAutomation
from database import DatabaseManager
from ui.dashboard import Dashboard

class SnapchatTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snapchat Score Tracker")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.automation = None
        self.dashboard = Dashboard(self.root, self.db_manager)
        
        # Tracking state
        self.is_tracking = False
        self.tracking_interval = 300  # 5 minutes in seconds
        self.tracked_users = []
        self.tracking_thread = None
        
        self.setup_ui()
        self.setup_menu()
        self.load_tracked_users()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Setup browser button
        ttk.Button(control_frame, text="Setup Browser", 
                  command=self.setup_browser).pack(fill=tk.X, pady=5)
        
        # Add user button
        ttk.Button(control_frame, text="Add Users to Track", 
                  command=self.add_users_dialog).pack(fill=tk.X, pady=5)
        
        # Start/Stop tracking
        self.track_button = ttk.Button(control_frame, text="Start Tracking", 
                                      command=self.toggle_tracking)
        self.track_button.pack(fill=tk.X, pady=5)
        
        # Interval setting
        ttk.Label(control_frame, text="Check Interval (minutes):").pack(anchor=tk.W, pady=(10, 0))
        self.interval_var = tk.StringVar(value="5")
        interval_spin = ttk.Spinbox(control_frame, from_=1, to=60, 
                                   textvariable=self.interval_var, width=10)
        interval_spin.pack(fill=tk.X, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready - Please setup browser first")
        ttk.Label(control_frame, text="Status:").pack(anchor=tk.W, pady=(20, 0))
        status_label = ttk.Label(control_frame, textvariable=self.status_var, wraplength=200)
        status_label.pack(anchor=tk.W)
        
        # Dashboard (right side)
        self.dashboard.create_dashboard(main_frame, row=0, column=1, rowspan=2)
        
        # User list (bottom left)
        users_frame = ttk.LabelFrame(main_frame, text="Tracked Users", padding="10")
        users_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10), pady=(10, 0))
        
        # User listbox with scrollbar
        list_frame = ttk.Frame(users_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.users_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_listbox.yview)
        self.users_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Remove user button
        ttk.Button(users_frame, text="Remove Selected", 
                  command=self.remove_user).pack(fill=tk.X, pady=(10, 0))
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Setup Browser", command=self.setup_browser)
        tools_menu.add_command(label="Test Connection", command=self.test_connection)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_browser(self):
        """Setup and initialize the browser automation"""
        try:
            self.update_status("Setting up browser...")
            
            if self.automation:
                self.automation.close()
            
            self.automation = SnapchatAutomation()
            self.update_status("Browser setup complete - ready to track")
            
        except Exception as e:
            self.update_status(f"Browser setup failed: {str(e)}")
            messagebox.showerror("Setup Error", f"Failed to setup browser:\n{str(e)}")
    
    def test_connection(self):
        """Test the browser connection"""
        if not self.automation:
            messagebox.showwarning("Warning", "Please setup browser first!")
            return
        
        try:
            self.update_status("Testing connection...")
            # Try to get current page title
            title = self.automation.driver.title
            self.update_status(f"Connection OK - Current page: {title}")
            messagebox.showinfo("Test Result", f"Connection successful!\nCurrent page: {title}")
        except Exception as e:
            self.update_status("Connection test failed")
            messagebox.showerror("Test Failed", f"Connection test failed:\n{str(e)}")
    
    def load_tracked_users(self):
        """Load previously tracked users from database"""
        users = self.db_manager.get_all_users()
        for username in users:
            self.tracked_users.append(username)
            self.users_listbox.insert(tk.END, username)
    
    def add_users_dialog(self):
        """Open dialog to add users to track"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Users to Track")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        # Instructions
        ttk.Label(dialog, text="Enter Snapchat usernames to track (one per line):").pack(pady=10)
        
        # Text area
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        text_area = tk.Text(text_frame, height=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_users():
            usernames = text_area.get("1.0", tk.END).strip().split('\n')
            usernames = [u.strip() for u in usernames if u.strip()]
            
            added_count = 0
            for username in usernames:
                if username not in self.tracked_users:
                    self.tracked_users.append(username)
                    self.users_listbox.insert(tk.END, username)
                    self.db_manager.add_user(username)
                    added_count += 1
            
            dialog.destroy()
            self.update_status(f"Added {added_count} users")
            self.dashboard.update_data()
        
        ttk.Button(button_frame, text="Add Users", command=add_users).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def remove_user(self):
        """Remove selected user from tracking"""
        selection = self.users_listbox.curselection()
        if selection:
            index = selection[0]
            username = self.users_listbox.get(index)
            
            # Confirm removal
            if messagebox.askyesno("Confirm", f"Remove {username} from tracking?"):
                self.users_listbox.delete(index)
                self.tracked_users.remove(username)
                self.update_status(f"Removed {username}")
                self.dashboard.update_data()
    
    def toggle_tracking(self):
        """Start or stop tracking"""
        if not self.is_tracking:
            if not self.automation:
                messagebox.showwarning("Warning", "Please setup browser first!")
                return
            
            if not self.tracked_users:
                messagebox.showwarning("Warning", "Please add users to track first!")
                return
            
            self.start_tracking()
        else:
            self.stop_tracking()
    
    def start_tracking(self):
        """Start the tracking process"""
        self.is_tracking = True
        self.track_button.config(text="Stop Tracking")
        self.tracking_interval = int(self.interval_var.get()) * 60
        
        # Start tracking thread
        self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        self.update_status("Tracking started")
    
    def stop_tracking(self):
        """Stop the tracking process"""
        self.is_tracking = False
        self.track_button.config(text="Start Tracking")
        self.update_status("Tracking stopped")
    
    def tracking_loop(self):
        """Main tracking loop that runs in background"""
        while self.is_tracking:
            try:
                self.update_status("Checking scores...")
                
                for i, username in enumerate(self.tracked_users):
                    if not self.is_tracking:
                        break
                    
                    self.update_status(f"Checking {username} ({i+1}/{len(self.tracked_users)})...")
                    
                    # Get current score
                    score_data = self.automation.get_user_score(username)
                    
                    if score_data:
                        # Store in database
                        self.db_manager.add_score_entry(
                            username, 
                            score_data['score'], 
                            score_data.get('has_new_snap', False)
                        )
                        
                        # Update dashboard on main thread
                        self.root.after(0, self.dashboard.update_data)
                        
                        self.update_status(f"Updated {username}: {score_data['score']}")
                    else:
                        self.update_status(f"Failed to get score for {username}")
                    
                    # Small delay between users
                    time.sleep(2)
                
                if self.is_tracking:
                    next_check_min = self.tracking_interval // 60
                    self.update_status(f"Next check in {next_check_min} minutes")
                    
                    # Wait for interval or until stopped
                    for _ in range(self.tracking_interval):
                        if not self.is_tracking:
                            break
                        time.sleep(1)
                    
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def update_status(self, status):
        """Update status display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_status = f"{status} ({timestamp})"
        
        # Update on main thread
        if threading.current_thread() == threading.main_thread():
            self.status_var.set(full_status)
        else:
            self.root.after(0, lambda: self.status_var.set(full_status))
    
    def export_data(self):
        """Export tracking data to file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = self.db_manager.export_data()
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Snapchat Score Tracker v1.0

Track Snapchat scores and activity patterns for relationship transparency.

Features:
• Automated score monitoring
• Real-time alerts and notifications
• Visual timeline graphs
• Data export capabilities

Built with Python, Tkinter, and Selenium.

⚠️ Use responsibly and with consent."""
        
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_tracking:
            if messagebox.askokcancel("Quit", "Tracking is active. Stop tracking and quit?"):
                self.stop_tracking()
                time.sleep(1)  # Give time for tracking to stop
            else:
                return
        
        if self.automation:
            try:
                self.automation.close()
            except:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SnapchatTracker()
    app.run()