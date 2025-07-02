"""
Data extraction module for parsing Imamother forum content
"""
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse

class DataExtractor:
    """Handles extraction of structured data from forum pages"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for data extraction
        self.patterns = {
            'question_indicators': [
                r'\?', r'how to', r'what is', r'where can', r'when should',
                r'why does', r'help', r'advice', r'suggestions', r'recommendations'
            ],
            'answer_indicators': [
                r'try this', r'i suggest', r'in my experience', r'you should',
                r'i recommend', r'what worked for me', r'here\'s what'
            ],
            'resource_mentions': [
                r'book', r'website', r'article', r'doctor', r'specialist',
                r'product', r'service', r'app', r'tool', r'resource'
            ],
            'emotional_indicators': [
                r'worried', r'scared', r'excited', r'frustrated', r'happy',
                r'sad', r'anxious', r'grateful', r'confused', r'hopeful'
            ]
        }
    
    def extract_page_data(self, html_content: str, section_name: str) -> List[Dict]:
        """Extract structured data from a forum page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        posts_data = []
        
        # Try different selectors for forum posts
        post_selectors = [
            '.post', '.message', '.forum-post', '.topic-post',
            '[class*="post"]', '[class*="message"]', '.thread-item'
        ]
        
        posts = []
        for selector in post_selectors:
            posts = soup.select(selector)
            if posts:
                self.logger.debug(f"Found {len(posts)} posts using selector: {selector}")
                break
        
        if not posts:
            # Fallback: look for common forum structures
            posts = self._find_posts_fallback(soup)
        
        for post in posts:
            try:
                post_data = self._extract_post_data(post, section_name)
                if post_data:
                    posts_data.append(post_data)
            except Exception as e:
                self.logger.warning(f"Error extracting post data: {e}")
                continue
        
        return posts_data
    
    def _find_posts_fallback(self, soup: BeautifulSoup) -> List[Tag]:
        """Fallback method to find posts when standard selectors fail"""
        posts = []
        
        # Look for elements with post-like characteristics
        potential_posts = soup.find_all(['div', 'article', 'section'])
        
        for element in potential_posts:
            # Check if element contains typical post content
            if self._looks_like_post(element):
                posts.append(element)
        
        return posts
    
    def _looks_like_post(self, element: Tag) -> bool:
        """Determine if an element looks like a forum post"""
        text = element.get_text().strip()
        
        # Must have substantial text content
        if len(text) < 50:
            return False
        
        # Look for post indicators
        indicators = [
            element.find(class_=re.compile(r'author|user|poster')),
            element.find(class_=re.compile(r'date|time|timestamp')),
            element.find(class_=re.compile(r'content|body|message')),
            len(text.split()) > 10  # Has multiple words
        ]
        
        return sum(bool(indicator) for indicator in indicators) >= 2
    
    def _extract_post_data(self, post_element: Tag, section_name: str) -> Optional[Dict]:
        """Extract structured data from a single post"""
        try:
            # Extract basic post information
            post_data = {
                'section': section_name,
                'extracted_at': datetime.now().isoformat(),
                'post_id': self._extract_post_id(post_element),
                'author': self._extract_author(post_element),
                'timestamp': self._extract_timestamp(post_element),
                'content': self._extract_content(post_element),
                'title': self._extract_title(post_element),
                'replies_count': self._extract_replies_count(post_element),
                'views_count': self._extract_views_count(post_element),
                'tags': self._extract_tags(post_element),
                'links': self._extract_links(post_element),
                'is_question': False,
                'is_answer': False,
                'sentiment_indicators': [],
                'resource_mentions': [],
                'keywords': []
            }
            
            # Analyze content for business intelligence
            if post_data['content']:
                post_data.update(self._analyze_content(post_data['content']))
            
            # Only return posts with meaningful content
            if post_data['content'] and len(post_data['content'].strip()) > 20:
                return post_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting post data: {e}")
        
        return None
    
    def _extract_post_id(self, element: Tag) -> Optional[str]:
        """Extract post ID"""
        # Try common ID attributes
        for attr in ['id', 'data-post-id', 'data-id', 'data-message-id']:
            if element.get(attr):
                return str(element.get(attr))
        
        # Try to find ID in child elements
        id_element = element.find(attrs={'id': re.compile(r'post|message')})
        if id_element:
            return id_element.get('id')
        
        return None
    
    def _extract_author(self, element: Tag) -> Optional[str]:
        """Extract post author"""
        # Try common author selectors
        author_selectors = [
            '.author', '.username', '.poster', '.user-name',
            '[class*="author"]', '[class*="user"]', '[class*="poster"]'
        ]
        
        for selector in author_selectors:
            author_element = element.select_one(selector)
            if author_element:
                author = author_element.get_text().strip()
                if author:
                    return self._anonymize_username(author)
        
        return None
    
    def _anonymize_username(self, username: str) -> str:
        """Anonymize username for privacy"""
        if len(username) <= 2:
            return "User_" + "X" * len(username)
        
        # Keep first and last character, replace middle with X's
        return username[0] + "X" * (len(username) - 2) + username[-1]
    
    def _extract_timestamp(self, element: Tag) -> Optional[str]:
        """Extract post timestamp"""
        # Try common timestamp selectors
        time_selectors = [
            '.timestamp', '.date', '.time', '.posted-date',
            '[class*="time"]', '[class*="date"]', 'time'
        ]
        
        for selector in time_selectors:
            time_element = element.select_one(selector)
            if time_element:
                # Try datetime attribute first
                datetime_attr = time_element.get('datetime')
                if datetime_attr:
                    return datetime_attr
                
                # Try title attribute
                title_attr = time_element.get('title')
                if title_attr:
                    return title_attr
                
                # Use text content
                time_text = time_element.get_text().strip()
                if time_text:
                    return self._parse_relative_time(time_text)
        
        return None
    
    def _parse_relative_time(self, time_text: str) -> str:
        """Parse relative time expressions"""
        time_text = time_text.lower()
        now = datetime.now()
        
        if 'ago' in time_text:
            if 'minute' in time_text:
                minutes = re.search(r'(\d+)', time_text)
                if minutes:
                    return (now - timedelta(minutes=int(minutes.group(1)))).isoformat()
            elif 'hour' in time_text:
                hours = re.search(r'(\d+)', time_text)
                if hours:
                    return (now - timedelta(hours=int(hours.group(1)))).isoformat()
            elif 'day' in time_text:
                days = re.search(r'(\d+)', time_text)
                if days:
                    return (now - timedelta(days=int(days.group(1)))).isoformat()
        
        return time_text
    
    def _extract_content(self, element: Tag) -> Optional[str]:
        """Extract post content"""
        # Try common content selectors
        content_selectors = [
            '.content', '.message-content', '.post-content', '.body',
            '[class*="content"]', '[class*="message"]', '[class*="body"]'
        ]
        
        for selector in content_selectors:
            content_element = element.select_one(selector)
            if content_element:
                # Remove quoted text and signatures
                self._clean_content_element(content_element)
                content = content_element.get_text().strip()
                if content and len(content) > 10:
                    return content
        
        # Fallback: use all text content
        content = element.get_text().strip()
        return content if len(content) > 10 else None
    
    def _clean_content_element(self, element: Tag):
        """Remove quotes, signatures, and other noise from content"""
        # Remove quote blocks
        for quote in element.find_all(class_=re.compile(r'quote|quoted')):
            quote.decompose()
        
        # Remove signatures
        for sig in element.find_all(class_=re.compile(r'signature|sig')):
            sig.decompose()
        
        # Remove edit notices
        for edit in element.find_all(class_=re.compile(r'edit|modified')):
            edit.decompose()
    
    def _extract_title(self, element: Tag) -> Optional[str]:
        """Extract post or thread title"""
        # Try common title selectors
        title_selectors = [
            '.title', '.subject', '.topic-title', 'h1', 'h2', 'h3',
            '[class*="title"]', '[class*="subject"]'
        ]
        
        for selector in title_selectors:
            title_element = element.select_one(selector)
            if title_element:
                title = title_element.get_text().strip()
                if title:
                    return title
        
        return None
    
    def _extract_replies_count(self, element: Tag) -> int:
        """Extract number of replies"""
        reply_selectors = [
            '.replies', '.reply-count', '[class*="replies"]'
        ]
        
        for selector in reply_selectors:
            reply_element = element.select_one(selector)
            if reply_element:
                reply_text = reply_element.get_text()
                numbers = re.findall(r'\d+', reply_text)
                if numbers:
                    return int(numbers[0])
        
        return 0
    
    def _extract_views_count(self, element: Tag) -> int:
        """Extract number of views"""
        view_selectors = [
            '.views', '.view-count', '[class*="views"]'
        ]
        
        for selector in view_selectors:
            view_element = element.select_one(selector)
            if view_element:
                view_text = view_element.get_text()
                numbers = re.findall(r'\d+', view_text)
                if numbers:
                    return int(numbers[0])
        
        return 0
    
    def _extract_tags(self, element: Tag) -> List[str]:
        """Extract tags or categories"""
        tags = []
        
        tag_selectors = [
            '.tag', '.category', '.label', '[class*="tag"]'
        ]
        
        for selector in tag_selectors:
            tag_elements = element.select(selector)
            for tag_element in tag_elements:
                tag_text = tag_element.get_text().strip()
                if tag_text:
                    tags.append(tag_text)
        
        return tags
    
    def _extract_links(self, element: Tag) -> List[Dict[str, str]]:
        """Extract links from post content"""
        links = []
        
        for link in element.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            if href and text:
                links.append({
                    'url': href,
                    'text': text,
                    'type': self._classify_link(href)
                })
        
        return links
    
    def _classify_link(self, url: str) -> str:
        """Classify link type"""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ['amazon', 'ebay', 'shop']):
            return 'product'
        elif any(ext in url_lower for ext in ['.pdf', '.doc', '.docx']):
            return 'document'
        elif any(domain in url_lower for domain in ['youtube', 'vimeo']):
            return 'video'
        elif url_lower.startswith('mailto:'):
            return 'email'
        else:
            return 'external'
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for business intelligence"""
        content_lower = content.lower()
        
        analysis = {
            'is_question': self._is_question(content_lower),
            'is_answer': self._is_answer(content_lower),
            'sentiment_indicators': self._extract_sentiment_indicators(content_lower),
            'resource_mentions': self._extract_resource_mentions(content_lower),
            'keywords': self._extract_keywords(content)
        }
        
        return analysis
    
    def _is_question(self, content: str) -> bool:
        """Determine if content is a question"""
        question_patterns = self.patterns['question_indicators']
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in question_patterns)
    
    def _is_answer(self, content: str) -> bool:
        """Determine if content is an answer"""
        answer_patterns = self.patterns['answer_indicators']
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in answer_patterns)
    
    def _extract_sentiment_indicators(self, content: str) -> List[str]:
        """Extract emotional/sentiment indicators"""
        indicators = []
        emotion_patterns = self.patterns['emotional_indicators']
        
        for pattern in emotion_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                indicators.append(pattern)
        
        return indicators
    
    def _extract_resource_mentions(self, content: str) -> List[str]:
        """Extract mentions of resources, products, services"""
        mentions = []
        resource_patterns = self.patterns['resource_mentions']
        
        for pattern in resource_patterns:
            matches = re.finditer(rf'\b\w*{pattern}\w*\b', content, re.IGNORECASE)
            for match in matches:
                mentions.append(match.group())
        
        return list(set(mentions))  # Remove duplicates
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""
        # Simple keyword extraction - can be enhanced with NLP libraries
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
            'did', 'she', 'use', 'way', 'who', 'oil', 'sit', 'set', 'run', 'eat'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return most frequent keywords
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]