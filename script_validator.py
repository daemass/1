from openai import OpenAI
from config import OPENAI_API_KEY


class ScriptValidator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def validate_script(self, script, articles):
        prompt = f"""다음 뉴스 스크립트가 주어진 뉴스 기사와 일치하는지 확인하고, 사실과 다른 부분이 있다면 수정해 주세요. 
        뉴스 기사의 내용을 정확히 반영하도록 수정해 주세요.

        뉴스 스크립트:
        {script}

        뉴스 기사:
        """
        for article in articles:
            prompt += f"\n\n제목: {article['title']}\n내용: {article['full_content']}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 사실을 정확하게 검증하고 수정하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                n=1,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"검증 및 수정 중 오류 발생: {str(e)}"
