"""
Main scraper class for Imamother Forum
"""
import requests
import time
import json
import csv
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

from config import ScrapingConfig
from data_extractor import DataExtractor
from utils import setup_logging, create_output_directory, sanitize_filename

class ImamotherScraper:
    """Main scraper class for Imamother forum"""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.ua = UserAgent()
        self.logger = setup_logging(self.config.LOG_LEVEL, self.config.LOG_FILE)
        self.data_extractor = DataExtractor()
        self.scraped_data = []
        self.session_active = False
        self.last_request_time = 0
        
        # Create output directory
        create_output_directory(self.config.OUTPUT_DIR)
        
        # Set initial headers
        self._set_random_user_agent()
        
    def _set_random_user_agent(self):
        """Set a random user agent for the session"""
        user_agent = random.choice(self.config.USER_AGENTS)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.logger.info(f"Set user agent: {user_agent[:50]}...")
    
    def _respect_rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.config.REQUEST_DELAY:
            sleep_time = self.config.REQUEST_DELAY - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make a request with retry logic and rate limiting"""
        self._respect_rate_limit()
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                self.logger.debug(f"Making {method} request to: {url}")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=30, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=30, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.config.MAX_RETRIES}): {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY * (attempt + 1))
                    self._set_random_user_agent()  # Rotate user agent on retry
                else:
                    self.logger.error(f"All retry attempts failed for URL: {url}")
                    return None
    
    def login(self, username: str = None, password: str = None) -> bool:
        """Authenticate with the forum"""
        credentials = self.config.get_credentials()
        username = username or credentials['username']
        password = password or credentials['password']
        
        if not username or not password:
            self.logger.error("Login credentials not provided")
            return False
        
        try:
            # Get login page to extract any CSRF tokens or form data
            login_page = self._make_request(self.config.LOGIN_URL)
            if not login_page:
                return False
            
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Find login form
            login_form = soup.find('form', {'id': 'login-form'}) or soup.find('form', class_='login-form')
            if not login_form:
                # Try to find any form with username/password fields
                forms = soup.find_all('form')
                for form in forms:
                    if form.find('input', {'name': 'username'}) or form.find('input', {'name': 'email'}):
                        login_form = form
                        break
            
            if not login_form:
                self.logger.error("Could not find login form on page")
                return False
            
            # Extract form action and method
            form_action = login_form.get('action', '/login')
            form_method = login_form.get('method', 'POST').upper()
            
            # Build login URL
            login_url = urljoin(self.config.BASE_URL, form_action)
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password
            }
            
            # Extract any hidden fields (CSRF tokens, etc.)
            hidden_fields = login_form.find_all('input', {'type': 'hidden'})
            for field in hidden_fields:
                name = field.get('name')
                value = field.get('value', '')
                if name:
                    login_data[name] = value
            
            # Attempt login
            self.logger.info("Attempting to log in...")
            response = self._make_request(login_url, method=form_method, data=login_data)
            
            if not response:
                return False
            
            # Check if login was successful
            # Look for indicators of successful login
            success_indicators = [
                'dashboard', 'profile', 'logout', 'welcome',
                'my-account', 'user-menu', 'member-area'
            ]
            
            response_text = response.text.lower()
            login_successful = any(indicator in response_text for indicator in success_indicators)
            
            # Also check if we're redirected away from login page
            if response.url != login_url and 'login' not in response.url.lower():
                login_successful = True
            
            if login_successful:
                self.session_active = True
                self.logger.info("Login successful")
                return True
            else:
                self.logger.error("Login failed - no success indicators found")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def scrape_section(self, section_name: str, max_pages: int = None) -> List[Dict]:
        """Scrape a specific forum section"""
        if not self.session_active:
            self.logger.error("Not logged in. Please login first.")
            return []
        
        if section_name not in self.config.FORUM_SECTIONS:
            self.logger.error(f"Unknown section: {section_name}")
            return []
        
        section_url = urljoin(self.config.BASE_URL, self.config.FORUM_SECTIONS[section_name])
        max_pages = max_pages or self.config.MAX_PAGES_PER_SECTION
        
        self.logger.info(f"Starting to scrape section: {section_name}")
        section_data = []
        
        for page in range(1, max_pages + 1):
            page_url = f"{section_url}?page={page}"
            self.logger.info(f"Scraping page {page} of {section_name}")
            
            response = self._make_request(page_url)
            if not response:
                self.logger.warning(f"Failed to fetch page {page}")
                continue
            
            # Extract data from page
            page_data = self.data_extractor.extract_page_data(response.content, section_name)
            if not page_data:
                self.logger.info(f"No more data found on page {page}, stopping")
                break
            
            section_data.extend(page_data)
            self.logger.info(f"Extracted {len(page_data)} items from page {page}")
            
            # Check if this is the last page
            if len(page_data) < self.config.MAX_POSTS_PER_PAGE:
                self.logger.info("Reached last page")
                break
        
        self.logger.info(f"Completed scraping {section_name}: {len(section_data)} total items")
        return section_data
    
    def scrape_all_sections(self) -> Dict[str, List[Dict]]:
        """Scrape all configured forum sections"""
        if not self.session_active:
            self.logger.error("Not logged in. Please login first.")
            return {}
        
        all_data = {}
        
        for section_name in self.config.FORUM_SECTIONS.keys():
            self.logger.info(f"Starting section: {section_name}")
            section_data = self.scrape_section(section_name)
            all_data[section_name] = section_data
            
            # Add delay between sections
            time.sleep(self.config.REQUEST_DELAY * 2)
        
        return all_data
    
    def save_data(self, data: Dict[str, List[Dict]], filename_prefix: str = None):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = filename_prefix or "imamother_data"
        
        for format_type in self.config.OUTPUT_FORMATS:
            if format_type == 'json':
                filename = f"{prefix}_{timestamp}.json"
                filepath = os.path.join(self.config.OUTPUT_DIR, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.info(f"Data saved to JSON: {filepath}")
            
            elif format_type == 'csv':
                # Save each section as a separate CSV
                for section_name, section_data in data.items():
                    if section_data:
                        filename = f"{prefix}_{section_name}_{timestamp}.csv"
                        filepath = os.path.join(self.config.OUTPUT_DIR, filename)
                        
                        # Get all unique keys for CSV headers
                        all_keys = set()
                        for item in section_data:
                            all_keys.update(item.keys())
                        
                        with open(filepath, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                            writer.writeheader()
                            writer.writerows(section_data)
                        
                        self.logger.info(f"Data saved to CSV: {filepath}")
    
    def logout(self):
        """Logout and cleanup session"""
        if self.session_active:
            # Try to find and use logout URL
            try:
                logout_url = urljoin(self.config.BASE_URL, '/logout')
                self._make_request(logout_url)
            except:
                pass  # Logout might fail, but we'll cleanup anyway
            
            self.session_active = False
            self.session.close()
            self.logger.info("Logged out and session closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()