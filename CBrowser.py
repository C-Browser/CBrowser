import sys
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                               QVBoxLayout, QLineEdit, QProgressBar, QWidget, 
                               QPushButton, QHBoxLayout)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createRequest(self, request_type, request, navigation_type, is_main_frame):
        request.setRawHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        return super().createRequest(request_type, request, navigation_type, is_main_frame)

class CBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CBrowser")
        self.setGeometry(100, 100, 1200, 800)

        # Tab widget to manage multiple tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Enable close button on tabs
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Add the first tab with default webpage
        self.add_new_tab("https://cbrowser.colebolebole.site/", "New Tab")

        # New tab button
        self.new_tab_button = QPushButton("+")
        self.tabs.setCornerWidget(self.new_tab_button)
        self.new_tab_button.clicked.connect(self.add_blank_tab)

    def add_blank_tab(self):
        """Add a blank tab with the default URL."""
        self.add_new_tab("https://cbrowser.colebolebole.site/", "New Tab")

    def add_new_tab(self, url, title):
        """Add a new tab with a browser view and address bar."""
        browser_widget = BrowserWidget(url)
        tab_index = self.tabs.addTab(browser_widget, title)
        self.tabs.setCurrentWidget(browser_widget)

    def close_tab(self, index):
        """Close a tab."""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_tab_title(self, index, title):
        """Update the tab title when the page title changes."""
        self.tabs.setTabText(index, title)


class BrowserWidget(QWidget):
    def __init__(self, url):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)

        # Back, forward, and refresh buttons
        self.back_button = QPushButton("<")
        self.back_button.clicked.connect(self.go_back)

        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.go_forward)

        self.refresh_button = QPushButton("↻")
        self.refresh_button.clicked.connect(self.refresh_page)

        # Navigation bar layout
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.address_bar)

        self.layout.addLayout(nav_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Web browser with custom page
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage())

        # Ensure multimedia settings are enabled
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)  # Enable fullscreen support
        settings.setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, False)  # Disable hyperlink auditing

        self.browser.setUrl(QUrl(url))
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.reset_progress)
        self.browser.titleChanged.connect(self.update_tab_title)

        self.layout.addWidget(self.browser)

        # Inject JavaScript to bypass compatibility checks
        self.browser.loadFinished.connect(self.inject_script)

        # Set the address bar to the initial URL
        self.address_bar.setText(url)

    def load_url(self):
        """Load the URL entered in the address bar."""
        url = self.address_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.browser.setUrl(QUrl(url))

    def go_back(self):
        """Go back in browser history."""
        self.browser.back()

    def go_forward(self):
        """Go forward in browser history."""
        self.browser.forward()

    def refresh_page(self):
        """Refresh the current page."""
        self.browser.reload()

    def update_progress(self, progress):
        """Update the progress bar as the page loads."""
        self.progress_bar.setValue(progress)

    def reset_progress(self):
        """Reset the progress bar when loading finishes."""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

    def update_tab_title(self, title):
        """Update the tab title when the page title changes."""
        main_window = self.window()
        index = main_window.tabs.indexOf(self)
        main_window.update_tab_title(index, title)

    def inject_script(self):
        """Inject JavaScript to modify or bypass compatibility checks."""
        script = """
        // Example JavaScript to handle unsupported media types
        function checkMediaSupport() {
            var mediaSource = new MediaSource();
            var supported = MediaSource.isTypeSupported('audio/mp4; codecs="mp4a.40.2"');
            if (!supported) {
                console.warn('Media type not supported');
                // Handle fallback or alternative media formats here
            }
        }

        // Run the media support check
        checkMediaSupport();

        // Example JavaScript to bypass some compatibility checks
        if (window.navigator.userAgent.indexOf('Chrome') === -1) {
            window.navigator.__defineGetter__('userAgent', function(){
                return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36';
            });
        }
        """
        self.browser.page().runJavaScript(script)


def main():
    app = QApplication(sys.argv)
    
    # Create and show the CBrowser window
    window = CBrowser()
    window.show()

    # Run the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
