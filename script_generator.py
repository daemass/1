from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

class ScriptGenerator:
    def __init__(self):
        self.styles = {
            "아나운서": "공식적이고 전문적인 톤으로, 객관적인 사실 전달에 중점을 둡니다.",
            "친구": "편안하고 친근한 톤으로, 일상적인 대화 스타일을 사용합니다.",
            "선생님": "교육적이고 설명적인 톤으로, 정보를 쉽게 이해할 수 있도록 합니다.",
            "정치가": "설득력 있고 강한 톤으로, 의견을 제시하고 주장을 펼칩니다.",
            "코미디언": "유머러스하고 가벼운 톤으로, 재미있게 정보를 전달합니다."
        }

    def get_available_styles(self):
        return list(self.styles.keys())

    def generate_script(self, news_articles, style="아나운서", presenter_name="진행자", language="한국어"):
        news_content_str = "\n\n".join([f"Title: {article['title']}\nContent: {article['full_content']}" for article in news_articles])
        news_count = len(news_articles)

        language_instructions = {
            "한국어": "한국어로 작성하세요.",
            "English": "Write in English.",
            "日本語": "日本語で書いてください。",
            "中文": "请用中文写作。"
        }

        prompt = f"""Create a natural and engaging script for a YouTube news video discussing the following news articles:

Presenter Name: {presenter_name}

News Articles:
{news_content_str}

The script should:
1. Start with a brief greeting and introduction using the presenter's name.
2. Present each news article in a flowing, conversational manner, as if naturally transitioning from one topic to another.
3. Include specific details for each news item:
   - For products: mention features, prices, and any other key information viewers might be curious about.
   - For sports events: include results, scores, key players involved in scoring, and any significant moments.
   - For political or economic news: mention key figures, important data or statistics, and potential impacts.
   - For entertainment news: include names of celebrities, event details, and any notable quotes or incidents.
4. Avoid using numbering or explicit segmentation between news items.
5. Integrate the information from all articles into a cohesive narrative, using appropriate transitions between topics.
6. End with a brief conclusion and a subtle call to action for viewers to engage with the channel.
7. Be approximately {'1000-1200' if news_count > 1 else '600-800'} words long.
8. Use a tone and style suitable for a {style}. {self.styles[style]}
9. {language_instructions[language]}

Please write the entire script in {language}, adapting the content and style to match that of a {style}, ensuring a smooth flow throughout the entire script while including specific, detailed information for each news item."""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a skilled YouTube script writer, creating content in the style of a {style} for a {language}-speaking audience. Focus on the provided news articles and include specific details."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error occurred: {str(e)}"
