from transformers import pipeline
from typing import Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSummarizer:
    def __init__(self):
        try:
            # Initialize the summarization pipeline with a pre-trained model
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # Use CPU. Change to 0 for GPU if available
            )
        except Exception as e:
            logger.error(f"Error initializing summarizer: {str(e)}")
            raise

    def summarize(self, article: Dict[str, str], max_length: int = 150, min_length: int = 50) -> Optional[Dict[str, str]]:
        """
        Generate a summary for the given article.
        Returns a dictionary containing the original article and its summary.
        """
        try:
            if not article or 'content' not in article:
                logger.warning("Invalid article format")
                return None

            # Split content into chunks if it's too long
            content = article['content']
            if len(content.split()) > 1024:  # Model's maximum input length
                chunks = self._split_text(content)
                summaries = []
                for chunk in chunks:
                    summary = self.summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )[0]['summary_text']
                    summaries.append(summary)
                final_summary = ' '.join(summaries)
            else:
                final_summary = self.summarizer(
                    content,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )[0]['summary_text']

            # Convert summary to bullet points
            bullet_points = self._convert_to_bullet_points(final_summary)

            return {
                'title': article['title'],
                'content': article['content'],
                'summary': bullet_points,
                'url': article['url'],
                'date': article.get('date', '')
            }

        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return None

    def _split_text(self, text: str, max_words: int = 1000) -> list:
        """
        Split text into chunks of approximately max_words.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            current_chunk.append(word)
            current_length += 1
            if current_length >= max_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _convert_to_bullet_points(self, text: str) -> str:
        """
        Convert a text summary into bullet points.
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter out empty sentences and clean them
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Convert to bullet points
        bullet_points = ['• ' + sentence for sentence in sentences]
        
        # Join with newlines
        return '\n'.join(bullet_points) 