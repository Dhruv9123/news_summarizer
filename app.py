from flask import Flask, render_template, request, jsonify
from scraper import NewsScraper
from summarizer import NewsSummarizer
import logging

app = Flask(__name__)
scraper = NewsScraper()
summarizer = NewsSummarizer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/top-news', methods=['POST'])
def get_top_news():
    try:
        url = request.json.get('url')
        limit = request.json.get('limit', 50)
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Get top news articles
        articles = scraper.get_top_news(url, limit=limit)
        if not articles:
            return jsonify({'error': 'Could not fetch news articles'}), 400

        # Generate summaries for each article
        summarized_articles = []
        for article in articles:
            result = summarizer.summarize(article)
            if result:
                summarized_articles.append(result)

        return jsonify({
            'articles': summarized_articles,
            'count': len(summarized_articles)
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/summarize', methods=['POST'])
def summarize_article():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Scrape the article
        article = scraper.scrape_article(url)
        if not article:
            return jsonify({'error': 'Could not scrape article'}), 400

        # Generate summary
        result = summarizer.summarize(article)
        if not result:
            return jsonify({'error': 'Could not generate summary'}), 500

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True) 