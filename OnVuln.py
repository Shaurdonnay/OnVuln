import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QScrollArea
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
import feedparser
from plyer import notification
import os
from bs4 import BeautifulSoup

class PostWidget(QWidget):
    def __init__(self, title, description, link):
        super().__init__()

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        link_label = QLabel(f"<a href=\"{link}\">{link}</a>")
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnVuln")
        self.setGeometry(100, 100, 800, 400)

        self.container = QWidget(self)
        self.setCentralWidget(self.container)
        self.layout = QVBoxLayout()
        self.container.setLayout(self.layout)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("OnVulnLogo.png")
        larger_pixmap = pixmap.scaledToWidth(300)
        self.logo_label.setPixmap(larger_pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo_label)

        self.scroll_area = QScrollArea()
        self.layout.addWidget(self.scroll_area)

        self.inner_container = QWidget()
        self.inner_layout = QVBoxLayout()
        self.inner_container.setLayout(self.inner_layout)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.inner_container)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFont(QFont("Arial", 20, QFont.Bold))
        self.refresh_button.setFixedHeight(50)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        self.inner_layout.addWidget(self.refresh_button)

        app_icon = QIcon("OnVulnLogo.ico")
        self.setWindowIcon(app_icon)

        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_refresh)
        self.auto_refresh_interval = 5 * 60 * 1000
        self.auto_refresh_timer.start(self.auto_refresh_interval)

    def on_refresh_clicked(self):
        self.refresh_button.setVisible(False)
        self.logo_label.setVisible(False)
        self.fetch_feeds()

    def fetch_feeds(self):
        self.clear_post_widgets()

        url = "https://rss.app/feeds/_RP0KDFz1LWXGaEns.xml"

        try:
            feeds = feedparser.parse(url)

            for entry in feeds.entries:
                title = entry.title
                description = entry.description
                link = entry.link

                post_widget = PostWidget(title, description, link)
                self.inner_layout.addWidget(post_widget)

                self.show_notification(title, description, link)

        except Exception as e:
            error_message = f"Error fetching feeds: {str(e)}"
            print(error_message)

    def show_notification(self, title, description, link):
        max_description_length = 100

        truncated_description = description[:max_description_length] + "..." if len(description) > max_description_length else description

        soup = BeautifulSoup(truncated_description, "html.parser")
        clean_description = soup.get_text(separator=" ")

        notification_title = "New Post"
        notification_text = f"{title}\n{clean_description}"

        app_icon_url = "https://raw.githubusercontent.com/shaurdonnay/OnVuln/main/OnVulnLogo.ico"
        app_icon = QIcon(app_icon_url)

        notification.notify(
            title=notification_title,
            message=notification_text,
            timeout=10,
            app_icon=app_icon,
            toast=True
        )

    def clear_post_widgets(self):
        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def auto_refresh(self):
        self.fetch_feeds()

    def closeEvent(self, event):
        self.auto_refresh_timer.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
