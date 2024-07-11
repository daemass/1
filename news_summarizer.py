from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

class NewsSummarizer:
    def __init__(self):
        pass

    def summarize_article(self, article):
        prompt = f"""다음 뉴스 기사의 핵심 내용을 간결한 문장으로 요약해주세요. 
        중요한 사실만을 포함하고, 불필요한 세부 사항은 제외하세요.

        제목: {article['title']}
        내용: {article['description']}

        요약:"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 사실을 정확하게 전달하는 아나운서이며, 뉴스 기사를 간결하고 정확하게 요약하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                n=1,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"요약 중 오류 발생: {str(e)}"

    def summarize_multiple_articles(self, articles):
        summaries = []
        for article in articles:
            summary = self.summarize_article(article)
            summaries.append({"title": article['title'], "summary": summary, "url": article['url']})
        return summaries