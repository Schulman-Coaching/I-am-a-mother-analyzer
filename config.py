"""
Configuration settings for Imamother Forum Scraper
"""
import os
from typing import Dict, List

class ScrapingConfig:
    """Configuration class for scraping parameters"""
    
    # Base URL and endpoints
    BASE_URL = "https://www.imamother.com"
    LOGIN_URL = f"{BASE_URL}/login"
    FORUM_SECTIONS = {
        'pregnancy_childbirth': '/forum/pregnancy-childbirth',
        'married_life': '/forum/married-life',
        'taharas_hamishpacha': '/forum/taharas-hamishpacha',
        'infertility_support': '/forum/infertility-support',
        'general_discussion': '/forum/general-discussion'
    }
    
    # Rate limiting settings
    REQUEST_DELAY = 1.5  # seconds between requests
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds to wait before retry
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_CONCURRENT_SESSIONS = 1
    
    # User agent rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Data extraction settings
    MAX_PAGES_PER_SECTION = 50
    MAX_POSTS_PER_PAGE = 100
    EXTRACT_IMAGES = False
    EXTRACT_ATTACHMENTS = False
    
    # Output settings
    OUTPUT_DIR = "scraped_data"
    OUTPUT_FORMATS = ['json', 'csv']
    BACKUP_ENABLED = True
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Privacy and compliance
    RESPECT_ROBOTS_TXT = True
    EXCLUDE_PERSONAL_INFO = True
    ANONYMIZE_USERNAMES = True
    
    # Business intelligence settings
    EXTRACT_KEYWORDS = True
    ANALYZE_SENTIMENT = False
    TRACK_ENGAGEMENT = True
    IDENTIFY_TRENDS = True
    
    @classmethod
    def get_credentials(cls) -> Dict[str, str]:
        """Get login credentials from environment variables"""
        return {
            'username': os.getenv('IMAMOTHER_USERNAME', ''),
            'password': os.getenv('IMAMOTHER_PASSWORD', '')
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        credentials = cls.get_credentials()
        if not credentials['username'] or not credentials['password']:
            print("Warning: Login credentials not found in environment variables")
            return False
        return True