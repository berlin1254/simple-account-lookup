import sys
import time
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QCheckBox, QFileDialog, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class AccountLookupThread(QThread):
    results_signal = pyqtSignal(dict)
    
    def __init__(self, username, platforms):
        super().__init__()
        self.username = username
        self.platforms = platforms
    
    def run(self):
        results = {}
        platforms_dict = {
            'YouTube': f"https://www.youtube.com/{self.username}",
            'Twitter': f"https://twitter.com/{self.username}",
            'Instagram': f"https://www.instagram.com/{self.username}/",
            'LinkedIn': f"https://www.linkedin.com/in/{self.username}/",
            'Facebook': f"https://www.facebook.com/{self.username}",
            'TikTok': f"https://www.tiktok.com/@{self.username}",
            'Pinterest': f"https://www.pinterest.com/{self.username}",
            'Snapchat': f"https://www.snapchat.com/add/{self.username}",
            'Reddit': f"https://www.reddit.com/user/{self.username}",
            'GitHub': f"https://github.com/{self.username}",
            'Medium': f"https://medium.com/@{self.username}",
            'Tumblr': f"https://{self.username}.tumblr.com",
            'Vimeo': f"https://vimeo.com/{self.username}",
            'Twitch': f"https://www.twitch.tv/{self.username}",
            'Spotify': f"https://open.spotify.com/user/{self.username}",
            'Quora': f"https://www.quora.com/profile/{self.username}",
            'Discord': f"https://discordapp.com/users/{self.username}",
            'SoundCloud': f"https://soundcloud.com/{self.username}",
            'Periscope': f"https://www.pscp.tv/{self.username}",
            'Flickr': f"https://www.flickr.com/photos/{self.username}",
            'Steam': f"https://steamcommunity.com/id/{self.username}",
            'Patreon': f"https://www.patreon.com/{self.username}",
            'Amazon': f"https://www.amazon.com/shops/{self.username}"
        }

        for platform, url in platforms_dict.items():
            if platform not in self.platforms:
                continue
            
            try:
                response = requests.get(url)
                
                if response.status_code == 404:
                    results[platform] = f"{self.username} does not exist on {platform}."
                else:
                    results[platform] = f"{self.username} exists on {platform}: {url}"

            except requests.exceptions.RequestException as e:
                results[platform] = f"Error checking {platform}: {str(e)}"
        
        self.results_signal.emit(results)

class AccountLookupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Account Lookup Tool")
        self.setGeometry(100, 100, 800, 600)  # Windowed mode size

        self.init_ui()
        self.load_search_history()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top-right layout for the toggle button
        top_layout = QHBoxLayout()
        
        # Fullscreen Toggle Button in top-right
        self.fullscreen_button = QPushButton("Toggle Fullscreen", self)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        top_layout.addStretch(1)  # Push the button to the right
        top_layout.addWidget(self.fullscreen_button)

        # Add the top_layout to the main layout
        layout.addLayout(top_layout)

        # Title Label
        self.title_label = QLabel("Enter the username to check across platforms:")
        layout.addWidget(self.title_label)
        
        # Username Input Field
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter username")
        layout.addWidget(self.username_input)
        
        # Platforms Selection (Checkboxes)
        self.platforms_checkbox = {}
        self.platforms_list = ['YouTube', 'Twitter', 'Instagram', 'LinkedIn', 'Facebook', 'TikTok', 
                               'Pinterest', 'Snapchat', 'Reddit', 'GitHub', 'Medium', 'Tumblr', 
                               'Vimeo', 'Twitch', 'Spotify', 'Quora', 'Discord', 'SoundCloud', 
                               'Periscope', 'Flickr', 'Steam', 'Patreon', 'Amazon']
        for platform in self.platforms_list:
            checkbox = QCheckBox(platform, self)
            self.platforms_checkbox[platform] = checkbox
            layout.addWidget(checkbox)

        # Select All Button
        self.select_all_button = QPushButton("Select All", self)
        self.select_all_button.clicked.connect(self.select_all_platforms)
        layout.addWidget(self.select_all_button)

        # Search Button
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.on_search)
        layout.addWidget(self.search_button)
        
        # Loading Indicator (Hidden initially)
        self.loading_label = QLabel("Searching...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        layout.addWidget(self.loading_label)
        
        # Results List (Taller box)
        self.results_list = QListWidget(self)
        self.results_list.setFixedHeight(300)  # Increased height for the result box
        layout.addWidget(self.results_list)

        # Export Button
        self.export_button = QPushButton("Export Results", self)
        self.export_button.clicked.connect(self.export_results)
        layout.addWidget(self.export_button)
        
        # Clear Button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_results)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def select_all_platforms(self):
        for checkbox in self.platforms_checkbox.values():
            checkbox.setChecked(True)

    def on_search(self):
        username = self.username_input.text().strip()
        
        if not username:
            self.results_list.clear()
            self.results_list.addItem("Please enter a username.")
            return
        
        platforms = [platform for platform, checkbox in self.platforms_checkbox.items() if checkbox.isChecked()]
        
        # Clear previous results and show loading indicator
        self.results_list.clear()
        self.loading_label.setVisible(True)
        
        # Start the lookup in a separate thread
        self.thread = AccountLookupThread(username, platforms)
        self.thread.results_signal.connect(self.display_results)
        self.thread.start()

    def display_results(self, results):
        self.loading_label.setVisible(False)
        self.results_list.clear()
        
        if results:
            for platform, result in results.items():
                self.results_list.addItem(result)
        else:
            self.results_list.addItem("No results found.")

    def clear_results(self):
        self.username_input.clear()
        self.results_list.clear()
        self.loading_label.setVisible(False)

    def load_search_history(self):
        try:
            with open('search_history.json', 'r') as f:
                history = json.load(f)
                self.username_input.addItems(history)  # Add items to the input box
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def export_results(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "Text Files (*.txt);;CSV Files (*.csv)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                for i in range(self.results_list.count()):
                    file.write(self.results_list.item(i).text() + '\n')

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AccountLookupApp()
    window.show()
    sys.exit(app.exec_())
