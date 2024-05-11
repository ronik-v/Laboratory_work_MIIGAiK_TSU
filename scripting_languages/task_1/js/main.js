const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const winston = require('winston');

// Logger
const logger = winston.createLogger({
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'result_task.log' })
  ],
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ level, message, timestamp }) => {
      return `${timestamp} - [${level}] - ${message}`;
    })
  )
});

// Script time work in seconds
const timeoutSeconds = 4 * 60 * 60;
const startTime = Date.now();

class MockStorage {
  constructor() {
    this.storage = [];
  }

  set(value) {
    this.storage.push(value);
  }

  get(value) {
    return this.storage.includes(value);
  }
}

class NewsParserData {
  constructor(siteLink, requestHeaders) {
    this.siteLink = siteLink;
    this.requestHeaders = requestHeaders;

    this.parserKeywords = [
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
    ];
  }

  static async requestByLink(url, headers) {
    try {
      const response = await axios.get(url, { headers });
      return response.data;
    } catch (error) {
      logger.error(error);
    }
  }

  isAboutParties(newsTitle) {
    for (const keyword of this.parserKeywords) {
      if (newsTitle.toLowerCase().includes(keyword.toLowerCase())) {
        return true;
      }
    }
    return false;
  }

  async links() {
    const newsHtmlText = await NewsParserData.requestByLink(this.siteLink, this.requestHeaders);
    const $ = cheerio.load(newsHtmlText);
    const newsData = {};
    const newsTitles = $('span.normal-wrap').map((_, el) => $(el).text().trim()).get();
    const newsLinks = $('a.item__link').map((_, el) => $(el).attr('href')).get();

    for (let i = 0; i < newsTitles.length; i++) {
      newsData[newsTitles[i]] = newsLinks[i];
    }
    return newsData;
  }

  async detailData(newsLink) {
    const detailArticle = await NewsParserData.requestByLink(newsLink, this.requestHeaders);
    const $ = cheerio.load(detailArticle);
    const detailAuthors = $('span.article__authors__author__name').map((_, el) => $(el).text().trim()).get();
    const detailTitle = $('div.article__header__title').text().trim();
    const detailAnnotation = $('div.article__header__yandex').text().trim();

    if (detailTitle && detailAnnotation) {
      const logMessage = `авторы=${detailAuthors} заголовок = ${detailTitle} аннотация = ${detailAnnotation}`;
      logger.info(logMessage);
    }
  }
}

async function main() {
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1'
  };
  const shortNewsUrl = 'https://www.rbc.ru/short_news';
  const newsParser = new NewsParserData(shortNewsUrl, headers);
  const newsStorage = new MockStorage();

  while (true) {
    try {
      const news = await newsParser.links();  
      for (const [title, link] of Object.entries(news)) {
        const isExistNews = newsStorage.get(title);

        const news_title_log = 'TITLE: ' + title + ' - ' + 'LINK: ' + link
        console.log(news_title_log);

        if (!isExistNews && newsParser.isAboutParties(title)) {
          await newsParser.detailData(link);
          // TODO: REMOVE!!!!
          console.log('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ' + title)
          newsStorage.set(title);
        }
      }
    } catch (error) {
      logger.error(error);
    } finally {
      await new Promise(resolve => setTimeout(resolve, 60000)); // Request update delay
      const elapsedTime = Date.now() - startTime;
      if (elapsedTime > timeoutSeconds * 1000) {
        logger.info('Конец');
        process.exit(0);
      }
    }
  }
}

main();
