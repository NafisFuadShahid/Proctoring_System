import time
import psutil
import datetime
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
import win32process
import sys
import os
from pathlib import Path

class ApplicationMonitor:
    def __init__(self, allowed_apps_file="allowed_apps.txt", log_file="non_work_activity.txt"):
        self.allowed_keywords = self.load_allowed_keywords(allowed_apps_file)
        self.log_file = log_file
        print("Loaded keywords:", self.allowed_keywords)  # Debug print
        
    def load_allowed_keywords(self, filename):
        """
        Load list of allowed applications and extract keywords
        Returns a set of keywords from the process names
        """
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found. No processes will be marked as work-related.")
            return set()
        
        keywords = set()
        with open(filename, 'r') as f:
            for line in f:
                # Clean the process name and remove .exe
                process = line.strip().lower()
                if process.endswith('.exe'):
                    process = process[:-4]
                
                # Split by common separators and add each part as a keyword
                parts = process.replace('-', ' ').replace('_', ' ').split()
                keywords.update(parts)
        
        return keywords

    def is_work_process(self, process_name, window_title):
        """
        Check if a process name or window title contains any of our allowed keywords.
        Exclude irrelevant system processes.
        """
        # List of processes to exclude from monitoring
        excluded_processes = {"searchhost.exe", "explorer.exe", "runtimebroker.exe"}
        
        # Skip excluded processes
        if process_name and process_name.lower() in excluded_processes:
            return True  # Treat system processes as "work" to avoid logging them

        # Clean the process name and window title for comparison
        process_clean = process_name.lower() if process_name else ""
        window_clean = window_title.lower() if window_title else ""

        if process_clean.endswith('.exe'):
            process_clean = process_clean[:-4]

        # Split into keywords
        process_parts = process_clean.replace('-', ' ').replace('_', ' ').split()
        window_parts = window_clean.replace('-', ' ').replace('_', ' ').split()

        # Check both process and window parts against allowed keywords
        return any(part in self.allowed_keywords for part in process_parts + window_parts)


    def get_process_name_from_window(self, hwnd):
        """Get process name from window handle using GetWindowThreadProcessId"""
        try:
            # Get the process ID from the window handle
            _, pid = GetWindowThreadProcessId(hwnd)
            
            # Get the process name using psutil
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            print(f"Error getting process name: {e}")  # Debug print
            return None

    def get_active_window_process(self):
        """Get the process name and title of the currently active window"""
        try:
            active_window = GetForegroundWindow()
            window_title = GetWindowText(active_window)
            process_name = self.get_process_name_from_window(active_window)
            
            is_work = self.is_work_process(process_name, window_title)
            return process_name, window_title, is_work
            
        except Exception as e:
            print(f"Error in get_active_window_process: {e}")  # Debug print
            return None, f"Error: {str(e)}", False

    def log_activity(self, process_name, window_title):
        """Log non-work application activity"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | Process: {process_name} | Window: {window_title}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

    def monitor(self, check_interval=5):
        """Main monitoring loop"""
        print(f"Starting application monitor...")
        print(f"Loaded {len(self.allowed_keywords)} keywords for work process detection")
        
        while True:
            process_name, window_title, is_work = self.get_active_window_process()
            
            # If process is not work-related, log it
            if not is_work:
                self.log_activity(process_name, window_title)
            
            time.sleep(check_interval)

def main():
    monitor = ApplicationMonitor()
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()