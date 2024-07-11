import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTextEdit, QComboBox,
                             QHBoxLayout, QLabel, QLineEdit, QListWidget,
                             QSplitter, QGridLayout, QListWidgetItem, QDialog,
                             QTextBrowser, QScrollArea)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
from content_scraper import ContentScraper
from script_generator import ScriptGenerator
from news_manager import NewsManager
from image_generator import ImageGenerator
from script_validator import ScriptValidator

class ArticleViewerDialog(QDialog):
    def __init__(self, article):
        super().__init__()
        self.setWindowTitle(article['title'])
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        content_browser = QTextBrowser()
        content_browser.setOpenExternalLinks(True)

        content_browser.setHtml(f"""
            <h2>{article['title']}</h2>
            <p><a href="{article['url']}">원본 기사 링크</a></p>
            <h3>전체 내용:</h3>
            <p>{article['full_content']}</p>
        """)
        layout.addWidget(content_browser)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced News Script Generator")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Initialize components
        self.scraper = ContentScraper()
        self.generator = ScriptGenerator()
        self.news_manager = NewsManager()
        self.image_generator = ImageGenerator()
        self.validator = ScriptValidator()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Left side: Controls and search trends
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Search trends
        self.search_trends_widget = QListWidget()
        self.search_trends_widget.setFont(QFont("Arial", 10))
        self.search_trends_widget.setMaximumHeight(300)
        self.search_trends_widget.itemClicked.connect(self.show_related_news)
        left_layout.addWidget(QLabel("Search Trends:"))
        left_layout.addWidget(self.search_trends_widget)

        # Related news
        self.related_news_widget = QListWidget()
        self.related_news_widget.setFont(QFont("Arial", 10))
        self.related_news_widget.itemChanged.connect(self.update_selected_news)
        self.related_news_widget.itemDoubleClicked.connect(self.show_news_article)
        left_layout.addWidget(QLabel("Related News:"))
        left_layout.addWidget(self.related_news_widget)

        # Selected news
        self.selected_news_widget = QListWidget()
        self.selected_news_widget.setFont(QFont("Arial", 10))
        self.selected_news_widget.itemDoubleClicked.connect(self.show_selected_news_article)
        left_layout.addWidget(QLabel("Selected News:"))
        left_layout.addWidget(self.selected_news_widget)

        # Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        name_layout = QHBoxLayout()
        name_label = QLabel("Presenter Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter presenter name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        controls_layout.addLayout(name_layout)

        style_layout = QHBoxLayout()
        style_label = QLabel("Style:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(self.generator.get_available_styles())
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        controls_layout.addLayout(style_layout)

        language_layout = QHBoxLayout()
        language_label = QLabel("Output Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["한국어", "English", "日本語", "中文"])
        self.language_combo.setCurrentText("한국어")
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        controls_layout.addLayout(language_layout)

        self.generate_button = QPushButton("Generate Script and Image")
        self.generate_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;"
        )
        self.generate_button.clicked.connect(self.generate_content)
        controls_layout.addWidget(self.generate_button)

        # 뉴스 기사 열람 버튼 추가
        self.view_article_button = QPushButton("View Selected Article")
        self.view_article_button.clicked.connect(self.view_selected_article)
        controls_layout.addWidget(self.view_article_button)

        left_layout.addWidget(controls_widget)

        # Right side: Script output and image display
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output.setFont(QFont("Arial", 12))
        right_layout.addWidget(self.script_output)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.image_label)

        # Add left and right widgets to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 1000])  # Set initial sizes
        self.layout.addWidget(splitter)

        # Update trends initially and set up a timer to update periodically
        self.update_trends()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_trends)
        self.timer.start(300000)  # Update every 5 minutes (300,000 ms)

        self.current_news_articles = {}
        self.selected_news = []

    def show_related_news(self, item):
        keyword = item.text().split(". ", 1)[1]
        self.related_news_widget.clear()
        news_articles = self.scraper.get_news_by_topic(keyword, 10)
        self.current_news_articles[keyword] = news_articles
        for article in news_articles:
            item = QListWidgetItem(article['title'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.related_news_widget.addItem(item)

    def update_selected_news(self, item):
        keyword = self.search_trends_widget.currentItem().text().split(". ", 1)[1]
        index = self.related_news_widget.row(item)
        article = self.current_news_articles[keyword][index]
        if item.checkState() == Qt.Checked:
            if article not in self.selected_news:
                self.selected_news.append(article)
        else:
            if article in self.selected_news:
                self.selected_news.remove(article)
        self.update_selected_news_widget()

    def update_selected_news_widget(self):
        self.selected_news_widget.clear()
        for article in self.selected_news:
            self.selected_news_widget.addItem(article['title'])

    def show_news_article(self, item):
        keyword = self.search_trends_widget.currentItem().text().split(". ", 1)[1]
        index = self.related_news_widget.row(item)
        article = self.current_news_articles[keyword][index]
        dialog = ArticleViewerDialog(article)
        dialog.exec_()

    def show_selected_news_article(self, item):
        index = self.selected_news_widget.row(item)
        article = self.selected_news[index]
        dialog = ArticleViewerDialog(article)
        dialog.exec_()

    def view_selected_article(self):
        selected_items = self.selected_news_widget.selectedItems()
        if selected_items:
            index = self.selected_news_widget.row(selected_items[0])
            article = self.selected_news[index]
            dialog = ArticleViewerDialog(article)
            dialog.exec_()
        else:
            self.script_output.setPlainText("Please select an article to view.")

    def generate_content(self):
        if not self.selected_news:
            self.script_output.setPlainText("Please select at least one news article.")
            return

        self.script_output.setPlainText("Generating content...")
        QApplication.processEvents()

        selected_style = self.style_combo.currentText()
        presenter_name = self.name_input.text() or "진행자"
        selected_language = self.language_combo.currentText()

        script = self.generator.generate_script(self.selected_news, style=selected_style, presenter_name=presenter_name,
                                                language=selected_language)
        self.script_output.setPlainText("Validating script...")
        QApplication.processEvents()

        validated_script = self.validator.validate_script(script, self.selected_news)
        self.script_output.setPlainText(validated_script)

        # Generate and display image
        image_path = self.image_generator.generate_announcer_image(presenter_name)
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def update_trends(self):
        self.search_trends_widget.clear()
        self.search_trends_widget.addItem("Updating trends...")
        QApplication.processEvents()

        try:
            search_trends = self.scraper.get_trending_keywords()

            self.search_trends_widget.clear()
            for i, trend in enumerate(search_trends, 1):
                self.search_trends_widget.addItem(f"{i}. {trend}")
        except Exception as e:
            self.search_trends_widget.clear()
            self.search_trends_widget.addItem(f"Error updating trends: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
