# import requests
# from src.FUNCTION.Tools.get_env import load_variable
# from typing import Union
# # in , us 
# def news_headlines(top:int = 10) -> Union[list[str] , None]:
#     """Fetch top news headlines."""
#     api_key = load_variable("News_api")
#     country = "india"
#     headlines = []
#     url = ('https://newsapi.org/v2/top-headlines?'
#         f'q={country}&from=2025-04-03&to=2025-04-03&sortBy=popularity&'
#         f'apiKey={api_key}')
#     try:
#         response = requests.get(url).json()
#         all_articles = response['articles']
#         total_results = int(response['totalResults'])
        
#         for i in range(min(top , total_results)):
#             headline = all_articles[i]['title']
#             headlines.append(headline)
#         return "\n".join(headlines)
#     except Exception as e:
#         print(e)
#         pass
#     return None 



#....



import requests
from src.FUNCTION.Tools.get_env import EnvManager
from typing import Union

class NewsHeadlines:
    def __init__(self, top: int = 10, country: str = "india"):
        self.top = top
        self.country = country
        self.api_key = EnvManager.load_variable("News_api")

    def fetch_headlines(self) -> Union[list[str], None]:
        """Fetch top news headlines."""
        headlines = []
        url = (
            f'https://newsapi.org/v2/top-headlines?'
            f'q={self.country}&from=2025-04-03&to=2025-04-03&sortBy=popularity&'
            f'apiKey={self.api_key}'
        )
        
        try:
            response = requests.get(url).json()
            all_articles = response['articles']
            total_results = int(response['totalResults'])
            
            for i in range(min(self.top, total_results)):
                headline = all_articles[i]['title']
                headlines.append(headline)
            return "\n".join(headlines)
        except Exception as e:
            print(f"Error: {e}")
            return None



def news_headlines(top=5):
    # Usage Example:
    news = NewsHeadlines(top)
    headlines = news.fetch_headlines()
    return headlines
