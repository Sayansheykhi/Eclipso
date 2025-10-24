# browser.py - Real browser with HTML rendering engine
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QStatusBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QFont, QWheelEvent
import requests
import warnings
from urllib.parse import urljoin
from privacy.enhanced_protector import EnhancedPrivacyProtector
from privacy.fingerprint_protector import FingerPrintProtector
from privacy.cookie_manager import cookie_manager

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class SwipeWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        self.swipe_threshold = 100  # Increased threshold for more precise detection
        self.swipe_start_x = 0
        self.swipe_start_y = 0
        
    def wheelEvent(self, event):
        # Get the scroll deltas
        delta_x = event.angleDelta().x()
        delta_y = event.angleDelta().y()
        
        # Check if this is a horizontal swipe gesture
        if abs(delta_x) > abs(delta_y) and abs(delta_x) > self.swipe_threshold:
            if delta_x > 0:
                # Swipe right - go back
                if self.parent_browser:
                    self.parent_browser.go_back()
            else:
                # Swipe left - go forward
                if self.parent_browser:
                    self.parent_browser.go_forward()
        else:
            # Normal vertical scrolling
            super().wheelEvent(event)

class PrivacyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Skip privacy components to avoid bot detection
        # self.privacy = EnhancedPrivacyProtector()
        # self.fingerprint_protector = FingerPrintProtector()
        # self.cookie_manager = cookie_manager()
        
        # Initialize browser state
        self.history = []  # Store visited URLs
        self.current_index = -1  # Current position in history
        self.current_url = ""
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main browser interface"""
        self.setWindowTitle("Eclipso - Privacy Browser")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar(main_layout)
        
        # Create web view (this is where websites will render)
        self.web_view = SwipeWebView(self)
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: none;
                background-color: white;
            }
        """)
        
        # Set a more realistic user agent immediately
        self.web_view.page().profile().setHttpUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set proper zoom and scaling
        self.web_view.setZoomFactor(1.0)  # Start with 100% zoom for proper scaling
        
        # Configure web view for proper content rendering
        self.web_view.settings().setAttribute(self.web_view.settings().AutoLoadImages, True)
        self.web_view.settings().setAttribute(self.web_view.settings().JavascriptEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().PluginsEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(self.web_view.settings().AllowRunningInsecureContent, True)
        
        # Connect signals
        self.web_view.urlChanged.connect(self.on_url_changed)
        self.web_view.loadFinished.connect(self.on_load_finished)
        
        # Add web view to layout
        main_layout.addWidget(self.web_view)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Clean browser")
        
        # No privacy protection - clean browser setup
        
        # Load Bing as the default page
        self.web_view.setUrl(QUrl("https://www.bing.com"))
        
        # Ensure web view takes up all available space and is visible
        self.web_view.setSizePolicy(self.web_view.sizePolicy().Expanding, self.web_view.sizePolicy().Expanding)
        self.web_view.setMinimumSize(800, 600)  # Set minimum size to ensure visibility
        self.web_view.show()  # Ensure the web view is visible
        
        # Add keyboard shortcuts for zoom control
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for zoom control"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Zoom in: Ctrl + Plus
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)
        
        # Zoom out: Ctrl + Minus
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)
        
        # Reset zoom: Ctrl + 0
        zoom_reset_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset_shortcut.activated.connect(self.zoom_reset)
    
    def zoom_in(self):
        """Zoom in the web view"""
        current_zoom = self.web_view.zoomFactor()
        new_zoom = min(current_zoom + 0.1, 2.0)  # Max zoom 200%
        self.web_view.setZoomFactor(new_zoom)
        self.status_bar.showMessage(f"Zoom: {int(new_zoom * 100)}%")
    
    def zoom_out(self):
        """Zoom out the web view"""
        current_zoom = self.web_view.zoomFactor()
        new_zoom = max(current_zoom - 0.1, 0.25)  # Min zoom 25%
        self.web_view.setZoomFactor(new_zoom)
        self.status_bar.showMessage(f"Zoom: {int(new_zoom * 100)}%")
    
    def zoom_reset(self):
        """Reset zoom to 100%"""
        self.web_view.setZoomFactor(1.0)
        self.status_bar.showMessage("Zoom: 100%")
        
    def create_toolbar(self, main_layout):
        """Create the browser toolbar with navigation buttons"""
        toolbar = QWidget()
        toolbar.setStyleSheet("QWidget { background-color: transparent; }")
        toolbar.setMaximumHeight(30)
        toolbar.setMinimumHeight(30)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(1)
        
        # Navigation buttons
        self.back_btn = QPushButton("←")
        self.back_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 1px 3px;
                border-radius: 3px;
                min-width: 18px;
                max-width: 18px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #303030;
                color: #808080;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.forward_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 1px 3px;
                border-radius: 3px;
                min-width: 18px;
                max-width: 18px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #303030;
                color: #808080;
            }
        """)
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                padding: 1px 3px;
                border-radius: 3px;
                min-width: 18px;
                max-width: 18px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_page)
        
        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setFont(QFont("Arial", 9))
        self.address_bar.setStyleSheet("""
            QLineEdit {
                background-color: #404040;
                color: white;
                border: 1px solid #606060;
                border-radius: 12px;
                padding: 2px 12px;
                min-width: 400px;
                max-width: 600px;
                min-height: 22px;
                max-height: 22px;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
                background-color: #505050;
            }
        """)
        self.address_bar.setText("https://www.bing.com")
        self.address_bar.returnPressed.connect(self.load_url)
        
        # Go button
        self.go_btn = QPushButton("Go")
        self.go_btn.setFont(QFont("Arial", 8, QFont.Bold))
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                padding: 1px 6px;
                border-radius: 3px;
                min-height: 18px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #5aaeff;
            }
        """)
        self.go_btn.clicked.connect(self.load_url)
        
        # Add widgets to toolbar
        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addWidget(self.forward_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addSpacing(50)  # Move address bar to the right
        toolbar_layout.addWidget(self.address_bar)
        toolbar_layout.addWidget(self.go_btn)
        toolbar_layout.addStretch()  # Push everything to the left
        
        # Add toolbar to main layout
        main_layout.addWidget(toolbar)
    
    @pyqtSlot()
    def load_url(self):
        """Load the URL from the address bar"""
        url = self.address_bar.text().strip()
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print(f"Loading URL: {url}")
        self.web_view.setUrl(QUrl(url))
        
        # Add to history
        self.add_to_history(url)
    
    # Google handling removed - use standard navigation
    
    def on_url_changed(self, url):
        """Called when the URL changes in the web view"""
        current_url = url.toString()
        self.address_bar.setText(current_url)
        self.current_url = current_url
        
        # Update status bar
        self.status_bar.showMessage(f"Loaded: {current_url}")
    
    def on_load_finished(self, success):
        """Called when page loading finishes"""
        if success:
            self.status_bar.showMessage("Page loaded successfully")
            # Force a repaint to ensure content is visible
            self.web_view.repaint()
            # Ensure web view is visible and properly sized
            self.web_view.show()
            self.web_view.raise_()
            self.web_view.activateWindow()
        else:
            self.status_bar.showMessage("Failed to load page")
            # Try to reload if failed
            self.web_view.reload()
    
    def add_to_history(self, url):
        """Add URL to browser history"""
        print(f"Adding to history: {url}")
        print(f"Before: Current index: {self.current_index}, History: {self.history}")
        
        # Remove any URLs after current index (when navigating back and then going to new URL)
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new URL
        self.history.append(url)
        self.current_index = len(self.history) - 1
        
        print(f"After: Current index: {self.current_index}, History: {self.history}")
        
        # Update navigation buttons
        self.update_navigation_buttons()
    
    def go_back(self):
        """Navigate back in browser history"""
        if self.current_index > 0:
            self.current_index -= 1
            url = self.history[self.current_index]
            print(f"Going back to: {url}")
            self.web_view.setUrl(QUrl(url))
            self.update_navigation_buttons()
    
    def go_forward(self):
        """Navigate forward in browser history"""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            url = self.history[self.current_index]
            print(f"Going forward to: {url}")
            self.web_view.setUrl(QUrl(url))
            self.update_navigation_buttons()
    
    def refresh_page(self):
        """Refresh the current page"""
        if self.current_url:
            print(f"Refreshing: {self.current_url}")
            self.web_view.reload()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons based on history"""
        # Back button
        if self.current_index > 0:
            self.back_btn.setEnabled(True)
        else:
            self.back_btn.setEnabled(False)
        
        # Forward button
        if self.current_index < len(self.history) - 1:
            self.forward_btn.setEnabled(True)
        else:
            self.forward_btn.setEnabled(False)
    
    # All privacy protection methods removed to avoid bot detection

    def run(self):
        """Start the browser"""
        self.show()

def main():
    """Main function to run the browser"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Eclipso Privacy Browser")
    app.setApplicationVersion("1.0")
    
    # Create and show browser
    browser = PrivacyBrowser()
    browser.run()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
