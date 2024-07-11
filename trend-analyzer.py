from pytrends.request import TrendReq
import time

class TrendAnalyzer:
    def __init__(self):
        self.pytrends = TrendReq(hl='ko-KR', tz=540)
        self.last_request_time = 0

    def get_search_trends(self, count=10):
        current_time = time.time()
        if current_time - self.last_request_time < 1:
            time.sleep(1 - (current_time - self.last_request_time))

        try:
            trends = self.pytrends.trending_searches(pn='south_korea')
            self.last_request_time = time.time()
            return trends.iloc[:count, 0].tolist()
        except Exception as e:
            print(f"Error fetching search trends: {str(e)}")
            return []
