# News Summarizer

This project scrapes news articles from various sources and provides AI-generated summaries of the content.

## Features
- Web scraping of news articles
- AI-powered text summarization
- Simple web interface to view summaries
- Support for multiple news sources

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Project Structure
- `app.py`: Main Flask application
- `scraper.py`: Web scraping functionality
- `summarizer.py`: Text summarization logic
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files 
