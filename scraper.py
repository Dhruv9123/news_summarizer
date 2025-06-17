import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_top_news(self, url: str, limit: int = 50) -> List[Dict[str, str]]:
        """
        Get top news articles from a news website.
        Returns a list of dictionaries containing article information.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = []
            article_links = []

            # Custom logic for BBC News
            if 'bbc.com/news' in url:
                for link in soup.find_all('a', class_='gs-c-promo-heading', href=True):
                    href = link['href']
                    if href.startswith('/news'):
                        href = 'https://www.bbc.com' + href
                    if href.startswith('http'):
                        article_links.append(href)
            # Custom logic for CNN
            elif 'cnn.com' in url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/'):  # CNN article links
                        href = 'https://www.cnn.com' + href
                    if '/202' in href and href.startswith('http') and 'videos' not in href:
                        article_links.append(href)
            # Custom logic for Reuters
            elif 'reuters.com' in url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/world') or href.startswith('/business') or href.startswith('/markets'):
                        href = 'https://www.reuters.com' + href
                    if href.startswith('http') and '/article/' in href:
                        article_links.append(href)
            # Custom logic for The Guardian
            elif 'theguardian.com' in url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/'):
                        href = 'https://www.theguardian.com' + href
                    if href.startswith('http') and '/202' in href:
                        article_links.append(href)
            else:
                # Generic logic for other sites
                containers = soup.find_all(['article', 'div'], class_=['article', 'story', 'news-item', 'card'])
                for container in containers:
                    link = container.find('a', href=True)
                    if link:
                        href = link['href']
                        if href.startswith('/'):
                            href = url.rstrip('/') + href
                        if href.startswith('http'):
                            article_links.append(href)

            # Remove duplicates while preserving order
            article_links = list(dict.fromkeys(article_links))
            article_links = article_links[:limit]

            for link in article_links:
                article = self.scrape_article(link)
                if article:
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error getting top news from {url}: {str(e)}")
            return []

    def scrape_article(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a news article from the given URL.
        Returns a dictionary containing the article's title and content.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Extract title
            title = soup.find('h1')
            if title:
                title = title.get_text().strip()
            else:
                title = "No title found"

            # Extract main content
            content = ""
            article_body = soup.find('article') or soup.find('main') or soup.find('div', class_=['content', 'article', 'story'])
            
            if article_body:
                paragraphs = article_body.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
            else:
                # Fallback: get all paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])

            if not content:
                logger.warning(f"No content found for URL: {url}")
                return None

            # Try to extract date
            date = None
            date_element = soup.find(['time', 'span', 'div'], class_=['date', 'time', 'published'])
            if date_element:
                date = date_element.get_text().strip()

            return {
                'title': title,
                'content': content,
                'url': url,
                'date': date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def get_news_links(self, source_url: str) -> List[str]:
        """
        Get a list of news article URLs from a news source homepage.
        This is a basic implementation - you'll need to customize it based on the news source.
        """
        try:
            response = requests.get(source_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that might be news articles
            # This is a basic implementation - you'll need to adjust the selectors
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Add logic to filter for article links
                if href.startswith('/') or source_url in href:
                    if href.startswith('/'):
                        href = source_url + href
                    links.append(href)
            
            return list(set(links))  # Remove duplicates

        except Exception as e:
            logger.error(f"Error getting news links from {source_url}: {str(e)}")
            return [] 