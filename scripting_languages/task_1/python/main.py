from requests import get
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from time import sleep
from logging import getLogger, basicConfig, INFO, StreamHandler
from time import time
from re import search, IGNORECASE

# Logger
logger = getLogger(__name__)
# Script time work in seconds
timeout_seconds = 4 * 60 * 60
# News logger config
basicConfig(filename='result_task.log', format='%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d)- %(message)s', level=INFO, encoding='utf-8')
console_handler = StreamHandler()
console_handler.setLevel(INFO)
logger.addHandler(console_handler)

start_time = time()


class MockStorage:
    def __init__(self) -> None:
        self.storage: list[str] = []
    
    def set(self, value: str) -> None:
        self.storage.append(value)

    def get(self, value: str) -> bool | None:
        return value in self.storage
    

class NewsParserData:
    def __init__(self, site_link: str, request_headers: dict[str, str]) -> None:
        self.site_link = site_link
        self.request_headers = request_headers

        self.parser_keywords: list[str] = [
            'демократы', 'республиканцы', 'партийная политика', 'предвыборная кампания', 'голосование',
            'кандидаты', 'политические дебаты', 'партийные съезды', 'политические идеологии', 'программы партий',
            'законопроекты', 'политические лидеры', 'интервью с политиками', 'партийные платформы', 'реформы',
            'бюджетные решения', 'внешняя политика', 'внутренняя политика', 'импичмент', 'политические скандалы',
            'президентские выборы', 'конгресс', 'сенат', 'палата представителей', 'губернаторы', 'министры',
            'политические резолюции', 'партийные лидеры', 'партийная риторика', 'партийные соглашения',
            'партийная платформа', 'партийные стратегии', 'партийные конвенции', 'партийные обещания',
            'законодательная инициатива', 'партийные позиции', 'партийные встречи', 'партийные реформы',
            'партийные кампании', 'партийные события', 'дебаты', 'кампании', 'политика', 'выборы', 'реформы',
            'лидерство', 'партийные инициативы', 'президент', 'законодательство', 'оппозиция', 'политическая арена',
            'выборы в Конгресс', 'выборы в Сенат', 'выборы в Палату представителей', 'решения по бюджету',
            'кампания по привлечению голосов', 'политические решения', 'партийные стратегии', 'партийные агитации', 'Трамп', 'Байден'
        ]

    @staticmethod
    def request_by_link(url: str, headers: dict[str, str]) -> str:
        """
        param: url - site url
        param: headers - user agent
        return: page html text - type string
        """
        response = get(url, headers=headers)
        return response.text
    
    def is_about_parties(self, news_title: str) -> bool:
        """
        param: news_title - title
        return: whether the news is about the US Democratic or Republican Party
        """
        for keyword in self.parser_keywords:
            if search(keyword.lower(), news_title.lower(), IGNORECASE):
                return True
        return False
    
    def links(self) -> dict[str, str]:
        """
        return: key value collection [news title  - news link]
        """
        news_html_text = self.request_by_link(self.site_link, self.request_headers)
        soup = BeautifulSoup(news_html_text, 'html.parser')
        news_data: dict[str, str] = {}
        news_titles = soup.find_all('span', class_='normal-wrap')
        news_links = soup.find_all('a', class_='item__link')

        for title, link in zip(news_titles, news_links):
            news_data[title.text.strip()] = link['href']
        return news_data
    
    def detail_data(self, news_link: str) -> None:
        """
        Refer to the detailed description of the article
        param: news_link - link to detail news page
        return: null [logging article data]
        """
        detail_article = self.request_by_link(news_link, self.request_headers)
        soup = BeautifulSoup(detail_article, 'html.parser')
        detail_authors: list[str] = [author.text.strip() for author in soup.find_all('span', class_='article__authors__author__name')]
        detail_title: str = soup.find('div', class_='article__header__title')
        detail_annotation: str = soup.find('div', class_='article__header__yandex')
        # Article news \ article title \ article annotation
        if detail_title and detail_annotation:
            log_message = f'авторы={detail_authors} заголовок = {detail_title.text.strip()} аннотация = {detail_annotation.text.strip()}'
            logger.info(log_message)


def main() -> None:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1'
    }
    short_news_url = 'https://www.rbc.ru/short_news'
    news_parser = NewsParserData(short_news_url, headers)
    news_storage = MockStorage()

    while True:
        try:
            news = news_parser.links()
            for title, link in news.items():

                print(f'TITLE: {title} - LINK: {link}')

                # Check that news exist in log file
                is_exist_news: bool = news_storage.get(title)

                if not is_exist_news and news_parser.is_about_parties(title):
                    news_parser.detail_data(link)
                    # TODO: REMOVE!!!!
                    print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {title}')
                    # save in storage 
                    news_storage.set(title)
        except ConnectionError as err:
            logger.error(err)
        finally:
            # Request update delay
            sleep(60)
            # Checking that 4 hours have passed
            elapsed_time = time() - start_time
            if elapsed_time > timeout_seconds:
                logger.info('Конец')
                exit(0)


if __name__ == "__main__":
    main()
