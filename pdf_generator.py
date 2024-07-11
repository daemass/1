import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class PDFGenerator:
    def __init__(self):
        self.base_dir = "generated_news_reports"
        os.makedirs(self.base_dir, exist_ok=True)

    def extract_keywords(self, text, num_keywords=3):
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        filtered_words = [word for word in word_tokens if word.isalnum() and word not in stop_words]
        word_freq = nltk.FreqDist(filtered_words)
        return [word for word, _ in word_freq.most_common(num_keywords)]

    def generate_pdf(self, script_content, news_articles, presenter_name, style):
        date_str = datetime.now().strftime("%Y%m%d")
        date_folder = os.path.join(self.base_dir, date_str)
        os.makedirs(date_folder, exist_ok=True)

        keywords = self.extract_keywords(script_content)
        filename = f"{date_str}_{presenter_name}_{style}_{'_'.join(keywords)}.pdf"
        filepath = os.path.join(date_folder, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        story = []

        # Add title
        story.append(Paragraph(f"뉴스 리포트 - {date_str}", styles['Title']))
        story.append(Spacer(1, 12))

        # Add presenter and style
        story.append(Paragraph(f"진행자: {presenter_name}", styles['Normal']))
        story.append(Paragraph(f"스타일: {style}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Add script content
        story.append(Paragraph("생성된 스크립트", styles['Heading1']))
        story.append(Paragraph(script_content, styles['BodyText']))
        story.append(PageBreak())

        # Add original news articles
        for i, article in enumerate(news_articles, 1):
            story.append(Paragraph(f"뉴스 기사 {i}", styles['Heading1']))
            story.append(Paragraph(f"제목: {article['title']}", styles['Heading2']))
            story.append(Paragraph(f"URL: {article['url']}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("전체 내용:", styles['Heading3']))
            story.append(Paragraph(article['full_content'], styles['BodyText']))
            story.append(PageBreak())

        doc.build(story)
        return filepath

    def open_pdf(self, filepath):
        os.startfile(filepath)  # This works on Windows
        # For macOS, use: os.system(f"open {filepath}")
        # For Linux, use: os.system(f"xdg-open {filepath}")