import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from pytrends.request import TrendReq
from config import NEWS_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, OPENAI_API_KEY
import os
from datetime import datetime
import json
import certifi
from openai import OpenAI


class ContentScraper:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        self.pytrends = TrendReq(hl='ko-KR', tz=540)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.last_request_time = 0
        self.scrape_dir = "scraped_news"
        os.makedirs(self.scrape_dir, exist_ok=True)
        self.article_limit = 10

    def get_trending_keywords(self, count=10):
        current_time = time.time()
        if current_time - self.last_request_time < 1:
            time.sleep(1 - (current_time - self.last_request_time))

        self.pytrends.build_payload(kw_list=[''], geo='KR')
        trends = self.pytrends.trending_searches(pn='south_korea')
        self.last_request_time = time.time()
        return trends.iloc[:count, 0].tolist()

    async def fetch_news_from_newsapi(self, session, query, page=1, page_size=10):
        articles = []
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=relevancy&pageSize={page_size}&page={page}&apiKey={NEWS_API_KEY}"
            async with session.get(url) as response:
                if response.status != 200:
                    return articles
                data = await response.json()
                if not data['articles']:
                    return articles
                articles.extend(data['articles'])
        except Exception as e:
            print(f"Error fetching news from News API for keyword '{query}': {str(e)}")
        return articles

    async def fetch_news_from_naver(self, session, query, start=1, display=10):
        articles = []
        headers = {
            'X-Naver-Client-Id': NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        }
        try:
            url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&start={start}&sort=sim"
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return articles
                data = await response.json()
                items = data.get('items', [])
                for item in items:
                    article_data = {
                        'title': item['title'],
                        'url': item['link'],
                        'description': item['description'],
                        'source': 'Naver News'
                    }
                    articles.append(article_data)
        except Exception as e:
            print(f"Error fetching news from Naver API for keyword '{query}': {str(e)}")
        return articles

    async def get_news_by_keyword(self, keyword, limit=10):
        query = f"{keyword} AND (한국 OR 코리아 OR Korea)"
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_news_from_newsapi(session, query, page_size=limit),
                self.fetch_news_from_naver(session, query, display=limit)
            ]
            results = await asyncio.gather(*tasks)
            all_articles = [item for sublist in results for item in sublist]
        return [await self.scrape_and_save_article(article) for article in all_articles[:limit]]

    async def fetch_additional_news(self, keyword, page, start, page_size=10):
        query = f"{keyword} AND (한국 OR 코리아 OR Korea)"
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_news_from_newsapi(session, query, page=page, page_size=page_size),
                self.fetch_news_from_naver(session, query, start=start, display=page_size)
            ]
            results = await asyncio.gather(*tasks)
            all_articles = [item for sublist in results for item in sublist]
        return [await self.scrape_and_save_article(article) for article in all_articles]

    async def scrape_article_content(self, session, url):
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                paragraphs = soup.find_all('p')
                content = []
                for p in paragraphs:
                    if '기사' not in p.text and '광고' not in p.text:
                        content.append(p.text)

                full_content = ' '.join(content)
                return full_content
        except Exception as e:
            return None, f"Error occurred while scraping article content: {str(e)}"

    async def classify_content(self, content):
        prompt = f"다음 내용에서 기사 제목과 내용, 광고 및 기타 내용을 분류해 주세요:\n\n{content}"
        try:
            response = await self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 기사 내용을 분류하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                n=1,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"분류 중 오류 발생: {str(e)}"

    async def scrape_and_save_article(self, article):
        async with aiohttp.ClientSession() as session:
            full_content = await self.scrape_article_content(session, article['url'])
            classified_content = await self.classify_content(full_content)

            # AI로부터 제목과 내용을 분류
            title, content = self.extract_title_and_content(classified_content)

            article['title'] = title
            article['full_content'] = content

            # 기사 저장
            self.save_article(article)

            return article

    def extract_title_and_content(self, classified_content):
        lines = classified_content.split('\n')
        title = "No title found"
        content = []
        for line in lines:
            if line.startswith("제목:"):
                title = line.replace("제목:", "").strip()
            else:
                content.append(line)
        return title, ' '.join(content)

    def save_article(self, article):
        date_str = datetime.now().strftime("%Y%m%d")
        date_folder = os.path.join(self.scrape_dir, date_str)
        os.makedirs(date_folder, exist_ok=True)

        safe_title = "".join([c for c in article['title'] if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        filename = f"{safe_title[:50]}.json"
        filepath = os.path.join(date_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=4)

    async def get_trending_news(self, count=5):
        keywords = self.get_trending_keywords(count)
        news = {}
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_news_by_keyword(keyword) for keyword in keywords]
            results = await asyncio.gather(*tasks)
            for keyword, articles in zip(keywords, results):
                if articles:
                    news[keyword] = articles
        return news, list(news.keys())

    async def get_news_by_topic(self, topic, count=10):
        return await self.get_news_by_keyword(topic)[:count]
