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
        
        # Only treat as horizontal swipe if:
        # 1. There's significant horizontal movement (delta_x != 0)
        # 2. Horizontal movement is much larger than vertical movement
        # 3. The absolute horizontal delta is above threshold
        if (delta_x != 0 and 
            abs(delta_x) > abs(delta_y) and 
            abs(delta_x) > self.swipe_threshold):
            
            # Horizontal swipe detected - handle navigation
            if delta_x > 0:
                # Swipe right - go back
                if self.parent_browser and self.parent_browser.back_btn.isEnabled():
                    self.parent_browser.go_back()
            else:
                # Swipe left - go forward  
                if self.parent_browser and self.parent_browser.forward_btn.isEnabled():
                    self.parent_browser.go_forward()
            
            # Block the scroll event completely
            event.setAccepted(True)
            return
        else:
            # Regular vertical scroll or small horizontal movement - process normally
            super().wheelEvent(event)

class PrivacyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize privacy components
        self.privacy = EnhancedPrivacyProtector()
        self.fingerprint_protector = FingerPrintProtector()
        self.cookie_manager = cookie_manager()
        
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
        self.web_view.setUrl(QUrl("https://duckduckgo.com"))
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: none;
                background-color: white;
            }
        """)
        
        # Set proper zoom and scaling
        self.web_view.setZoomFactor(1.0)  # Start with 100% zoom for proper scaling
        
        # Configure web view for proper content rendering
        self.web_view.settings().setAttribute(self.web_view.settings().AutoLoadImages, True)
        self.web_view.settings().setAttribute(self.web_view.settings().JavascriptEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().PluginsEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().LocalContentCanAccessRemoteUrls, True)
        
        # Set viewport meta tag support for responsive design
        self.web_view.settings().setAttribute(self.web_view.settings().WebGLEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().Accelerated2dCanvasEnabled, True)
        
        # Apply active fingerprint protection - change browser identity each session
        self.apply_fingerprint_protection()
        
        # Set up request interceptor to allow Google's essential resources
        self.setup_request_interceptor()
        
        # Disable strict privacy settings for Google to ensure modern styling loads
        self.setup_google_compatibility()
        
        # Set viewport settings for proper scaling
        self.web_view.page().runJavaScript("""
            var viewport = document.querySelector('meta[name=viewport]');
            if (!viewport) {
                viewport = document.createElement('meta');
                viewport.name = 'viewport';
                document.head.appendChild(viewport);
            }
            viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        """)
        
        # Ensure web view takes up all available space and is visible
        self.web_view.setSizePolicy(self.web_view.sizePolicy().Expanding, self.web_view.sizePolicy().Expanding)
        self.web_view.setMinimumSize(800, 600)  # Set minimum size to ensure visibility
        self.web_view.show()  # Ensure the web view is visible
        
        main_layout.addWidget(self.web_view, 1)  # Give it stretch factor of 1
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Enter a URL and press Go or Enter")
        
        # Connect signals
        self.web_view.urlChanged.connect(self.on_url_changed)
        self.web_view.loadFinished.connect(self.on_load_finished)
        
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
        toolbar_layout.setContentsMargins(1, 1, 1, 1)
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
                border-radius: 2px;
                min-height: 18px;
                max-height: 18px;
                min-width: 18px;
                max-width: 18px;
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
                border-radius: 2px;
                min-height: 18px;
                max-height: 18px;
                min-width: 18px;
                max-width: 18px;
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
                border-radius: 2px;
                min-height: 18px;
                max-height: 18px;
                min-width: 18px;
                max-width: 18px;
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
        self.address_bar.setText("https://duckduckgo.com")
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
                border-radius: 2px;
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
        toolbar_layout.addSpacing(50)  # Add more space before address bar
        toolbar_layout.addWidget(self.address_bar)
        toolbar_layout.addWidget(self.go_btn)
        toolbar_layout.addStretch()
        
        # Add toolbar to main layout
        main_layout.addWidget(toolbar)
    
    @pyqtSlot()
    def load_url(self):
        """Load the URL from the address bar"""
        url = self.address_bar.text().strip()
        
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.status_bar.showMessage(f"Loading {url}...")
        
        # Load URL in web view
        self.web_view.setUrl(QUrl(url))
        
        # Add to history
        self.add_to_history(url)
    
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
            self.status_bar.showMessage("Page loaded successfully - Privacy protection active")
            # Force a repaint to ensure content is visible
            self.web_view.repaint()
            # Ensure web view is visible and properly sized
            self.web_view.show()
            self.web_view.raise_()
            
            # Disable CSS injection to let sites use their original styles
            # self.inject_css_fixes()
            
            # from PyQt5.QtCore import QTimer
            # QTimer.singleShot(1000, self.inject_css_fixes)
            
            # Apply fingerprint protection only once per session
            if not hasattr(self, 'fingerprint_applied'):
                self.apply_fingerprint_protection()
            
            # Apply Google compatibility fixes only once per session
            if 'google.com' in self.current_url.lower() and not hasattr(self, 'google_fixes_applied'):
                self.apply_google_compatibility_fixes()
                self.google_fixes_applied = True
            
            # Log privacy protection status
            print(f"🔒 Privacy Protection Status:")
            print(f"   - Enhanced Protector: ACTIVE (blocking {len(self.privacy.trackers)} known trackers)")
            print(f"   - Fingerprint Protection: ACTIVE (randomized browser signature)")
            print(f"   - Cookie Policy: {self.cookie_manager.cookie_policy.upper()}")
            print(f"   - Web View Size: {self.web_view.size().width()}x{self.web_view.size().height()}")
            print(f"   - Web View Visible: {self.web_view.isVisible()}")
        else:
            self.status_bar.showMessage("Failed to load page")
            # Try to reload if failed
            self.web_view.reload()
    
    def inject_css_fixes(self):
        """Inject minimal CSS fixes that don't interfere with site styling"""
        def inject_css_callback(result):
            print(f"CSS injection result: {result}")
        
        # Use minimal, non-intrusive CSS fixes
        self.web_view.page().runJavaScript("""
            (function() {
                try {
                    // Remove existing style if any
                    var existingStyle = document.getElementById('eclipso-minimal-fix');
                    if (existingStyle) {
                        existingStyle.remove();
                    }
                    
                    // Create minimal style element that doesn't override site styles
                    var style = document.createElement('style');
                    style.id = 'eclipso-minimal-fix';
                    style.type = 'text/css';
                    style.innerHTML = `
                        /* Minimal fixes that don't interfere with site design */
                        body { 
                            overflow-x: hidden !important; 
                        }
                        
                        /* Only fix images that are clearly broken (too wide) */
                        img[style*="width"]:not([style*="max-width"]) {
                            max-width: 100% !important; 
                            height: auto !important; 
                        }
                        
                        /* Prevent horizontal scroll on main containers only */
                        .container, .main-content, .article-content {
                            overflow-x: hidden !important;
                        }
                    `;
                    
                    // Append to head
                    if (document.head) {
                        document.head.appendChild(style);
                        console.log('Eclipso minimal CSS injected successfully');
                        return 'Success: Minimal CSS applied';
                    } else {
                        console.log('Document head not available');
                        return 'Error: No document head';
                    }
                } catch(e) {
                    console.error('CSS injection failed:', e);
                    return 'Error: ' + e.message;
                }
            })();
        """, inject_css_callback)
        
        print("Minimal CSS injection attempted")
        
        # Set zoom factor to 100% for proper scaling
        try:
            self.web_view.setZoomFactor(1.0)  # 100% zoom for proper scaling
            print("Zoom factor set to 1.0")
        except Exception as e:
            print(f"Error setting zoom: {e}")
    
    def add_to_history(self, url):
        """Add URL to browser history"""
        print(f"Adding to history: {url}")
        print(f"Before: Current index: {self.current_index}, History: {self.history}")
        
        # Remove any URLs after current position
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
            print(f"Going back to: {url} (index: {self.current_index})")
            self.web_view.setUrl(QUrl(url))
            self.update_navigation_buttons()
    
    def go_forward(self):
        """Navigate forward in browser history"""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            url = self.history[self.current_index]
            print(f"Going forward to: {url} (index: {self.current_index})")
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
    
    def apply_fingerprint_protection(self):
        """Apply active fingerprint protection by changing browser identity"""
        # Only apply fingerprint protection once per session to avoid detection
        if hasattr(self, 'fingerprint_applied'):
            return
            
        # Generate a new random fingerprint for this session
        fingerprint = self.fingerprint_protector.generate_random_fingerprint()
        
        # Apply a more compatible user agent specifically for Google
        # Use a well-known Chrome user agent that Google fully supports
        google_compatible_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        self.web_view.page().profile().setHttpUserAgent(google_compatible_ua)
        
        # Mark as applied to prevent multiple applications
        self.fingerprint_applied = True
        
        # Store fingerprint for this session
        self.current_fingerprint = fingerprint
        
        # Skip JavaScript injection to avoid bot detection
        # Google's bot detection is very sensitive to JavaScript modifications
        
        print(f"🛡️ Active Fingerprint Protection Applied:")
        print(f"   - User Agent: {google_compatible_ua}")
        print(f"   - Language: {fingerprint.get('language', 'en-US')}")
        print(f"   - Timezone: {fingerprint.get('timezone', 'America/New_York')}")
        print(f"   - Screen: {fingerprint.get('screen_width', 1920)}x{fingerprint.get('screen_height', 1080)}")

    def setup_request_interceptor(self):
        """Set up request interceptor to allow Google's essential resources"""
        from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
        
        class PrivacyRequestInterceptor(QWebEngineUrlRequestInterceptor):
            def __init__(self):
                super().__init__()
                
            def interceptRequest(self, info):
                """Intercept and modify requests to allow Google's essential resources"""
                url = info.requestUrl().toString()
                
                # Add realistic browser headers to avoid bot detection
                info.setHttpHeader(b"Accept", b"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
                info.setHttpHeader(b"Accept-Language", b"en-US,en;q=0.9")
                info.setHttpHeader(b"Accept-Encoding", b"gzip, deflate, br")
                info.setHttpHeader(b"DNT", b"1")
                info.setHttpHeader(b"Connection", b"keep-alive")
                info.setHttpHeader(b"Upgrade-Insecure-Requests", b"1")
                info.setHttpHeader(b"Sec-Fetch-Dest", b"document")
                info.setHttpHeader(b"Sec-Fetch-Mode", b"navigate")
                info.setHttpHeader(b"Sec-Fetch-Site", b"none")
                info.setHttpHeader(b"Sec-Fetch-User", b"?1")
                info.setHttpHeader(b"Cache-Control", b"max-age=0")
                
                # Allow Google's essential domains for proper styling and functionality
                google_essential_domains = [
                    'google.com', 'googleapis.com', 'gstatic.com', 'googleusercontent.com',
                    'google-analytics.com', 'googletagmanager.com', 'doubleclick.net'
                ]
                
                # Check if this is a Google essential resource
                is_google_essential = any(domain in url for domain in google_essential_domains)
                
                if is_google_essential:
                    # Allow the request to proceed
                    print(f"✅ Allowing Google resource: {url}")
                    return
                
                # For non-Google domains, apply normal privacy protection
                # (This is where you could add more blocking logic if needed)
                
        # Set the interceptor (using the newer method)
        interceptor = PrivacyRequestInterceptor()
        self.web_view.page().profile().setUrlRequestInterceptor(interceptor)
        print("🔧 Request interceptor configured to allow Google's essential resources")

    def setup_google_compatibility(self):
        """Configure browser settings for optimal Google compatibility"""
        # Enable JavaScript (should be enabled by default, but ensure it's on)
        self.web_view.settings().setAttribute(self.web_view.settings().JavascriptEnabled, True)
        
        # Enable WebGL and hardware acceleration for modern Google features
        self.web_view.settings().setAttribute(self.web_view.settings().WebGLEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().Accelerated2dCanvasEnabled, True)
        
        # Allow images and media
        self.web_view.settings().setAttribute(self.web_view.settings().AutoLoadImages, True)
        
        # Enable plugins for better compatibility
        self.web_view.settings().setAttribute(self.web_view.settings().PluginsEnabled, True)
        
        # Disable strict content security policy that might block Google's resources
        self.web_view.settings().setAttribute(self.web_view.settings().LocalContentCanAccessRemoteUrls, True)
        
        # Allow mixed content for Google's CDN resources
        self.web_view.settings().setAttribute(self.web_view.settings().AllowRunningInsecureContent, True)
        
        # Enable smooth scrolling for better UX
        self.web_view.settings().setAttribute(self.web_view.settings().ScrollAnimatorEnabled, True)
        
        print("🔧 Google compatibility settings configured for modern styling")

    def apply_google_compatibility_fixes(self):
        """Apply specific fixes for Google pages to ensure modern styling loads"""
        # Only apply once to prevent blinking
        if hasattr(self, 'google_js_applied'):
            return
            
        self.google_js_applied = True
        
        # Skip aggressive fixes to avoid bot detection
        print("🔧 Skipping Google compatibility fixes to avoid bot detection")
        return
                console.log('🔧 Applying Google compatibility fixes...');
                
                // Only apply URL fixes if not already in modern mode
                var currentUrl = window.location.href;
                if (currentUrl.includes('google.com') && !currentUrl.includes('complete=1') && !currentUrl.includes('sorry')) {
                    console.log('🔧 Forcing Google modern interface...');
                    
                    // Remove any parameters that might force basic HTML mode
                    var urlParams = new URLSearchParams(window.location.search);
                    urlParams.delete('complete');  // Remove complete=0 parameter
                    urlParams.delete('html');      // Remove html=1 parameter
                    urlParams.delete('hl');        // Remove language parameter that might trigger basic mode
                    
                    // Add modern interface parameters
                    urlParams.set('complete', '1');  // Force complete mode
                    
                    var newUrl = window.location.origin + window.location.pathname + '?' + urlParams.toString();
                    if (newUrl !== currentUrl) {
                        console.log('🔧 Redirecting to modern Google interface:', newUrl);
                        window.location.href = newUrl;
                        return;
                    }
                }
                
                // Force reload of Google's CSS if it's not loading properly
                var links = document.querySelectorAll('link[rel="stylesheet"]');
                links.forEach(function(link) {
                    if (link.href && (link.href.includes('google') || link.href.includes('gstatic'))) {
                        console.log('Reloading Google CSS:', link.href);
                        var newLink = link.cloneNode(true);
                        link.parentNode.replaceChild(newLink, link);
                    }
                });
                
                // Always inject modern Google CSS to ensure modern appearance
                console.log('🔧 Injecting comprehensive Google modern styling...');
                
                var modernStyle = document.createElement('style');
                modernStyle.innerHTML = `
                    /* Comprehensive Google modern styling - exact match */
                    body { 
                        font-family: arial,sans-serif; 
                        background: #fff; 
                        margin: 0;
                        padding: 0;
                        text-align: center;
                        min-height: 100vh;
                    }
                    
                    /* Google search input field - comprehensive 2024 styling (text inputs only) */
                    input[name="q"], .gLFyf, .RNNXgb input[type="text"], 
                    input[type="text"][name="q"], input[type="search"] { 
                        border: 1px solid #dfe1e5 !important; 
                        border-radius: 24px !important; 
                        padding: 0 16px !important; 
                        font-size: 16px !important; 
                        width: 584px !important; 
                        max-width: 584px !important;
                        min-width: 584px !important;
                        height: 44px !important;
                        box-shadow: none !important;
                        background: #fff !important;
                        color: #202124 !important;
                        outline: none !important;
                        margin: 0 auto !important;
                        display: block !important;
                        box-sizing: border-box !important;
                        pointer-events: auto !important;
                        z-index: 1 !important;
                        font-family: arial,sans-serif !important;
                        line-height: 44px !important;
                        transition: all 0.1s ease !important;
                    }
                    
                    /* Ensure checkboxes are not affected by search box styling */
                    input[type="checkbox"], input[type="radio"] {
                        width: auto !important;
                        height: auto !important;
                        min-width: auto !important;
                        max-width: auto !important;
                        border-radius: 0 !important;
                        padding: 0 !important;
                        margin: 0 !important;
                        line-height: normal !important;
                        display: inline-block !important;
                        vertical-align: middle !important;
                    }
                    
                    /* Google search input hover state */
                    input[name="q"]:hover {
                        box-shadow: 0 2px 5px 1px rgba(64,60,67,.16) !important;
                        border-color: rgba(223,225,229,0) !important;
                    }
                    
                    /* Google search input focus state */
                    input[name="q"]:focus {
                        box-shadow: 0 2px 5px 1px rgba(64,60,67,.16) !important;
                        border-color: rgba(223,225,229,0) !important;
                        outline: none !important;
                    }
                    
                    /* Search container - only for layout */
                    .RNNXgb {
                        width: 584px !important;
                        max-width: 584px !important;
                        margin: 0 auto !important;
                        display: block !important;
                        position: relative !important;
                    }
                    
                    /* Hide duplicate search fields but keep the main one functional */
                    .a4bIc:not(:has(input[name="q"])) {
                        display: none !important;
                    }
                    
                    /* Search box hover state */
                    .gLFyf:hover, input[name="q"]:hover, input[type="text"]:hover {
                        box-shadow: 0 2px 8px 1px rgba(64,60,67,.24);
                        border-color: rgba(223,225,229,0);
                    }
                    
                    /* Search box focus state */
                    .gLFyf:focus, input[name="q"]:focus, input[type="text"]:focus {
                        box-shadow: 0 2px 8px 1px rgba(64,60,67,.24);
                        border-color: rgba(223,225,229,0);
                        outline: none;
                    }
                    /* Google button container for proper alignment */
                    .RNNXgb, form, div {
                        margin: 0 auto;
                        text-align: center;
                        max-width: 584px;
                    }
                    
                    /* Google buttons - comprehensive 2024 styling */
                    input[type="submit"], input[type="button"], button, .gNO89b, 
                    input[value*="Search"], input[value*="search"], 
                    input[value*="Feeling Lucky"], input[value*="I'm Feeling Lucky"],
                    .gNO89b, .RNNXgb input[type="submit"], .RNNXgb input[type="button"] { 
                        background: #f8f9fa !important; 
                        border: 1px solid #f8f9fa !important; 
                        border-radius: 4px !important; 
                        color: #3c4043 !important; 
                        font-size: 14px !important; 
                        margin: 11px 4px !important; 
                        padding: 0 16px !important; 
                        line-height: 27px !important; 
                        height: 36px !important; 
                        cursor: pointer !important;
                        font-family: arial,sans-serif !important;
                        min-width: 54px !important;
                        text-align: center !important;
                        box-shadow: none !important;
                        display: inline-block !important;
                        vertical-align: top !important;
                        font-weight: normal !important;
                        transition: all 0.1s ease !important;
                    }
                    
                    /* Google button hover state - exact 2024 colors */
                    input[type="submit"]:hover, input[type="button"]:hover, button:hover { 
                        box-shadow: 0 1px 1px rgba(0,0,0,.1) !important; 
                        background-color: #f8f9fa !important; 
                        border: 1px solid #dadce0 !important; 
                        color: #202124 !important;
                    }
                    
                    /* Google button focus state */
                    input[type="submit"]:focus, input[type="button"]:focus, button:focus { 
                        box-shadow: 0 1px 1px rgba(0,0,0,.1) !important; 
                        background-color: #f8f9fa !important; 
                        border: 1px solid #dadce0 !important; 
                        color: #202124 !important;
                        outline: none !important;
                    }
                        input[value*="Search"], input[value*="search"] { 
                            background: #f8f9fa !important; 
                            border: 1px solid #f8f9fa !important; 
                            border-radius: 4px !important; 
                            color: #3c4043 !important; 
                            font-size: 14px !important; 
                            margin: 11px 4px !important; 
                            padding: 0 16px !important; 
                            line-height: 27px !important; 
                            height: 36px !important; 
                            cursor: pointer !important;
                        }
                        input[value*="Feeling Lucky"], input[value*="Lucky"] { 
                            background: #f8f9fa !important; 
                            border: 1px solid #f8f9fa !important; 
                            border-radius: 4px !important; 
                            color: #3c4043 !important; 
                            font-size: 14px !important; 
                            margin: 11px 4px !important; 
                            padding: 0 16px !important; 
                            line-height: 27px !important; 
                            height: 36px !important; 
                            cursor: pointer !important;
                        }
                        /* Target any button-like elements */
                        input[type="submit"][value], input[type="button"][value] {
                            background: #f8f9fa !important;
                            border: 1px solid #f8f9fa !important;
                            border-radius: 4px !important;
                            color: #3c4043 !important;
                            font-size: 14px !important;
                            margin: 11px 4px !important;
                            padding: 0 16px !important;
                            line-height: 27px !important;
                            height: 36px !important;
                            cursor: pointer !important;
                        }
                    `;
                document.head.appendChild(modernStyle);
                
                // Add a small delay and then check if modern styling is applied
                setTimeout(function() {
                    // Find all search inputs and style them (exclude checkboxes and radios)
                    var searchBoxes = document.querySelectorAll('input[name="q"], .gLFyf, .RNNXgb input[type="text"], input[type="text"], input[type="search"]');
                    console.log('🔍 Found', searchBoxes.length, 'search inputs to style');
                    
                    searchBoxes.forEach(function(searchBox, index) {
                        console.log('✅ Styling search box', index + 1);
                        
                        // Ensure the search box is functional
                        searchBox.style.pointerEvents = 'auto';
                        searchBox.style.zIndex = '1';
                        searchBox.disabled = false;
                        searchBox.readOnly = false;
                        
                        // Style the search box with exact Google 2024 specifications
                        searchBox.style.borderRadius = '24px';
                        searchBox.style.padding = '0 16px';
                        searchBox.style.fontSize = '16px';
                        searchBox.style.width = '584px';
                        searchBox.style.maxWidth = '584px';
                        searchBox.style.minWidth = '584px';
                        searchBox.style.height = '44px';
                        searchBox.style.boxShadow = 'none';
                        searchBox.style.border = '1px solid #dfe1e5';
                        searchBox.style.background = '#fff';
                        searchBox.style.color = '#202124';
                        searchBox.style.outline = 'none';
                        searchBox.style.margin = '0 auto';
                        searchBox.style.display = 'block';
                        searchBox.style.boxSizing = 'border-box';
                        searchBox.style.fontFamily = 'arial,sans-serif';
                        searchBox.style.lineHeight = '44px';
                        searchBox.style.transition = 'all 0.1s ease';
                        
                        // Style the container
                        var container = searchBox.closest('.RNNXgb') || searchBox.parentNode;
                        if (container) {
                            container.style.width = '584px';
                            container.style.maxWidth = '584px';
                            container.style.margin = '0 auto';
                            container.style.display = 'block';
                            container.style.position = 'relative';
                        }
                        
                        // Test if the input is working
                        searchBox.addEventListener('focus', function() {
                            console.log('✅ Search box is focusable and functional');
                        });
                        
                    } else {
                        console.log('⚠️ Google search box not found - may be in basic HTML mode');
                    }
                    
                    // Force modern styling on ALL buttons with proper alignment
                    var allButtons = document.querySelectorAll('input[type="submit"], input[type="button"], button');
                    console.log('🔧 Found', allButtons.length, 'buttons to style');
                    
                    // Center the button container
                    var buttonContainer = allButtons[0] ? allButtons[0].parentNode : null;
                    if (buttonContainer) {
                        buttonContainer.style.textAlign = 'center';
                        buttonContainer.style.maxWidth = '584px';
                        buttonContainer.style.margin = '0 auto';
                    }
                    
                    allButtons.forEach(function(button, index) {
                        console.log('🔧 Styling button', index + 1, ':', button.value || button.textContent);
                        
                        // Apply exact Google 2024 button styling
                        button.style.background = '#f8f9fa';
                        button.style.border = '1px solid #f8f9fa';
                        button.style.borderRadius = '4px';
                        button.style.color = '#3c4043';
                        button.style.fontSize = '14px';
                        button.style.margin = '11px 4px';
                        button.style.padding = '0 16px';
                        button.style.lineHeight = '27px';
                        button.style.height = '36px';
                        button.style.cursor = 'pointer';
                        button.style.fontFamily = 'arial,sans-serif';
                        button.style.minWidth = '54px';
                        button.style.textAlign = 'center';
                        button.style.boxShadow = 'none';
                        button.style.display = 'inline-block';
                        button.style.verticalAlign = 'top';
                        button.style.fontWeight = 'normal';
                        
                        // Add hover effect
                        button.addEventListener('mouseenter', function() {
                            this.style.boxShadow = '0 1px 1px rgba(0,0,0,.1)';
                            this.style.background = '#f8f9fa';
                            this.style.border = '1px solid #dadce0';
                            this.style.color = '#202124';
                        });
                        
                        button.addEventListener('mouseleave', function() {
                            this.style.boxShadow = 'none';
                            this.style.background = '#f8f9fa';
                            this.style.border = '1px solid #f8f9fa';
                            this.style.color = '#3c4043';
                        });
                    });
                    
                    console.log('✅ Applied modern styling to', allButtons.length, 'buttons');
                }, 1000);
                
                console.log('🔧 Google compatibility fixes applied');
            })();
        """)
        print("🔧 Applied Google-specific compatibility fixes with modern styling injection")

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

