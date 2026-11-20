import sys
import os
from pathlib import Path
import requests
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QToolBar,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QTabWidget,
    QGroupBox,
    QRadioButton,
    QWidget,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl, QSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QT_OPENGL"] = "software"

settings = QSettings("SearchEng", "String")
DefaultEng = settings.value(
    "DefaultEng",
    "https://duckduckgo.com/?q="
)

file_path = Path(__file__).parent / "Home.html"


class Ikora(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ikora")
        self.showMaximized()


        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.Ikora = QWebEngineView()
        self.Ikora.setUrl(QUrl.fromLocalFile(str(file_path)))
        self.tabs.addTab(self.Ikora, "Home")

        toolbar = QToolBar("Navigation Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        back_btn = QAction("Back ⤶", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        toolbar.addAction(back_btn)

        forward_btn = QAction("Forward ⤷", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        toolbar.addAction(forward_btn)

        reload_btn = QAction("Reload ⟳", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        toolbar.addAction(reload_btn)

        home_btn = QAction("Home ⌂", self)
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(self.new_tab)
        toolbar.addAction(new_tab_btn)

        toolbar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL")
        self.url_bar.returnPressed.connect(self.navigate)
        self.url_bar.setText("Home")
        toolbar.addWidget(self.url_bar)

        set_btn = QAction("🌣", self)
        set_btn.triggered.connect(self.open_set)
        toolbar.addAction(set_btn)

        close_btn = QAction("➜]", self)
        close_btn.triggered.connect(self.end_app)
        toolbar.addAction(close_btn)

        self.Ikora.urlChanged.connect(self.update_url)
        self.Ikora.titleChanged.connect(self.update_tab_title)

        toolbar.addSeparator()
        self.tabs.currentChanged.connect(self.update_current_tab)

    def end_app(self):
        sys.exit(0)

    def new_tab(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl.fromLocalFile(str(file_path)))
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(self.update_url)
        browser.titleChanged.connect(
            lambda title, b=browser: self.update_tab_title_for(b, title)
        )

        self.setWindowTitle("Ikora")
        self.url_bar.setText("Home")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            self.tabs.removeTab(index)
            widget.deleteLater()

    def update_current_tab(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.url_bar.setText(browser.url().toString())
            self.setWindowTitle(browser.title() or "Ikora")

    def update_tab_title(self):
        browser = self.tabs.currentWidget()
        if browser:
            self.update_tab_title_for(browser, browser.title())

    def update_tab_title_for(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title[:20] if title else "New Tab")

        if browser == self.tabs.currentWidget():
            self.setWindowTitle(title or "Ikora")

    def go_home(self):
        self.tabs.currentWidget().setUrl(QUrl.fromLocalFile(str(file_path)))
        self.url_bar.setText("Home")
        self.setWindowTitle("Ikora")

    def navigate(self):
        url = self.url_bar.text().strip()

        if not url:
            return

        if not url.startswith(("http://", "https://")):

            settings = QSettings("SearchEng", "String")

            DefaultEng = settings.value(
                "DefaultEng",
                "https://duckduckgo.com/?q="
            )

            url = DefaultEng + requests.utils.quote(url)

        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, url):
        if url.isLocalFile():
            self.url_bar.setText("Home")
        else:
            self.url_bar.setText(url.toString())

    def open_set(self):
        self.Settings = SettingsWindow()
        self.Settings.show()


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(400, 150)
        self.setWindowTitle("Ikora - Settings")

        self.settings = QSettings("SearchEng", "String")

        group = QGroupBox("Default Search Engine")

        self.search_url = QLineEdit()
        self.search_url.setPlaceholderText(
            "https://duckduckgo.com/?q="
        )
        self.search_url.setText(
            self.settings.value(
                "DefaultEng",
                "https://duckduckgo.com/?q="
            )
        )

        self.on = QRadioButton("Custom Search Engine")
        self.off = QRadioButton("duckduckgo")

        self.on.setChecked(
            self.settings.value("SearchEng", False, type=bool)
        )
        self.off.setChecked(not self.on.isChecked())

        layout = QVBoxLayout()
        layout.addWidget(self.on)
        layout.addWidget(self.off)
        layout.addWidget(QLabel("Search Engine:"))
        layout.addWidget(self.search_url)

        group.setLayout(layout)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)

        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        main_layout.addWidget(save_btn)

        self.setLayout(main_layout)

    def save_settings(self):
        settings = QSettings("SearchEng", "String")

        if self.on.isChecked():
            search_url = self.search_url.text().strip()

            if not search_url:
                return
        else:
            search_url = "https://duckduckgo.com/?q="

        settings.setValue("SearchEng", self.on.isChecked())
        settings.setValue("DefaultEng", search_url)
        settings.sync()

        self.close()


app = QApplication(sys.argv)
window = Ikora()
window.show()
sys.exit(app.exec())
