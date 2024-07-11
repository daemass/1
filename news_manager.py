# news_manager.py

import sqlite3
import os

class NewsManager:
    def __init__(self):
        self.db_path = "news_articles.db"
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT UNIQUE,
         url TEXT,
         date DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')
        conn.commit()
        conn.close()

    def save_article(self, title, url):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO articles (title, url) VALUES (?, ?)", (title, url))
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def get_all_articles(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, url, date FROM articles ORDER BY date DESC")
        articles = [{"title": row[0], "url": row[1], "date": row[2]} for row in cursor.fetchall()]
        conn.close()
        return articles