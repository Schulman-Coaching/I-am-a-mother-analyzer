"""
Utility functions for the Imamother scraper
"""
import os
import logging
import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO", log_file: str = "scraper.log") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def create_output_directory(output_dir: str):
    """Create output directory if it doesn't exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Trim and remove leading/trailing underscores
    filename = filename.strip('_')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def save_json(data: Any, filepath: str, indent: int = 2):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        print(f"Data saved to JSON: {filepath}")
    except Exception as e:
        print(f"Error saving JSON file {filepath}: {e}")

def load_json(filepath: str) -> Optional[Any]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return None

def save_csv(data: List[Dict], filepath: str):
    """Save list of dictionaries to CSV file"""
    if not data:
        print("No data to save to CSV")
        return
    
    try:
        # Get all unique keys for headers
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(data)
        
        print(f"Data saved to CSV: {filepath}")
    except Exception as e:
        print(f"Error saving CSV file {filepath}: {e}")

def load_csv(filepath: str) -> List[Dict]:
    """Load data from CSV file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error loading CSV file {filepath}: {e}")
        return []

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""

def format_timestamp(timestamp: str) -> str:
    """Format timestamp to standard ISO format"""
    try:
        # Try to parse various timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # If no format matches, return original
        return timestamp
    except:
        return timestamp

def calculate_engagement_score(post_data: Dict) -> float:
    """Calculate engagement score for a post"""
    try:
        replies = post_data.get('replies_count', 0)
        views = post_data.get('views_count', 0)
        
        # Simple engagement calculation
        if views > 0:
            engagement = (replies / views) * 100
        else:
            engagement = 0
        
        # Bonus for questions and answers
        if post_data.get('is_question'):
            engagement += 10
        if post_data.get('is_answer'):
            engagement += 5
        
        # Bonus for resource mentions
        resource_count = len(post_data.get('resource_mentions', []))
        engagement += resource_count * 2
        
        return min(engagement, 100)  # Cap at 100
    except:
        return 0

def categorize_business_opportunity(post_data: Dict) -> str:
    """Categorize post by business opportunity type"""
    content = post_data.get('content', '').lower()
    title = post_data.get('title', '').lower()
    section = post_data.get('section', '')
    
    # Product opportunity keywords
    product_keywords = [
        'product', 'buy', 'purchase', 'recommend', 'brand', 'quality',
        'where to find', 'best', 'review', 'comparison'
    ]
    
    # Service opportunity keywords
    service_keywords = [
        'service', 'help', 'professional', 'expert', 'consultation',
        'advice', 'guidance', 'support', 'therapy', 'counseling'
    ]
    
    # Information opportunity keywords
    info_keywords = [
        'information', 'learn', 'understand', 'explain', 'guide',
        'tutorial', 'how to', 'what is', 'resource', 'book'
    ]
    
    # Community opportunity keywords
    community_keywords = [
        'group', 'community', 'support', 'meet', 'connect',
        'share', 'experience', 'similar', 'together'
    ]
    
    text_to_check = f"{content} {title}"
    
    # Count keyword matches
    product_score = sum(1 for keyword in product_keywords if keyword in text_to_check)
    service_score = sum(1 for keyword in service_keywords if keyword in text_to_check)
    info_score = sum(1 for keyword in info_keywords if keyword in text_to_check)
    community_score = sum(1 for keyword in community_keywords if keyword in text_to_check)
    
    # Determine category based on highest score
    scores = {
        'product': product_score,
        'service': service_score,
        'information': info_score,
        'community': community_score
    }
    
    max_category = max(scores, key=scores.get)
    
    # If no clear winner, use section-based categorization
    if scores[max_category] == 0:
        if 'pregnancy' in section or 'childbirth' in section:
            return 'health_service'
        elif 'married' in section:
            return 'relationship_service'
        elif 'infertility' in section:
            return 'medical_service'
        else:
            return 'general'
    
    return max_category

def generate_summary_stats(data: Dict[str, List[Dict]]) -> Dict:
    """Generate summary statistics for scraped data"""
    stats = {
        'total_posts': 0,
        'sections': {},
        'engagement_stats': {
            'avg_replies': 0,
            'avg_views': 0,
            'high_engagement_posts': 0
        },
        'content_analysis': {
            'questions': 0,
            'answers': 0,
            'resource_mentions': 0
        },
        'business_opportunities': {
            'product': 0,
            'service': 0,
            'information': 0,
            'community': 0
        },
        'temporal_analysis': {
            'posts_by_hour': {},
            'posts_by_day': {}
        }
    }
    
    all_posts = []
    for section_name, posts in data.items():
        stats['sections'][section_name] = len(posts)
        stats['total_posts'] += len(posts)
        all_posts.extend(posts)
    
    if not all_posts:
        return stats
    
    # Calculate engagement stats
    total_replies = sum(post.get('replies_count', 0) for post in all_posts)
    total_views = sum(post.get('views_count', 0) for post in all_posts)
    
    stats['engagement_stats']['avg_replies'] = total_replies / len(all_posts)
    stats['engagement_stats']['avg_views'] = total_views / len(all_posts)
    
    # Analyze content
    for post in all_posts:
        if post.get('is_question'):
            stats['content_analysis']['questions'] += 1
        if post.get('is_answer'):
            stats['content_analysis']['answers'] += 1
        
        resource_count = len(post.get('resource_mentions', []))
        stats['content_analysis']['resource_mentions'] += resource_count
        
        # Calculate engagement score
        engagement = calculate_engagement_score(post)
        if engagement > 50:  # High engagement threshold
            stats['engagement_stats']['high_engagement_posts'] += 1
        
        # Categorize business opportunity
        opportunity = categorize_business_opportunity(post)
        if opportunity in stats['business_opportunities']:
            stats['business_opportunities'][opportunity] += 1
        
        # Temporal analysis
        timestamp = post.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                day = dt.strftime('%A')
                
                stats['temporal_analysis']['posts_by_hour'][hour] = \
                    stats['temporal_analysis']['posts_by_hour'].get(hour, 0) + 1
                stats['temporal_analysis']['posts_by_day'][day] = \
                    stats['temporal_analysis']['posts_by_day'].get(day, 0) + 1
            except:
                pass
    
    return stats

def create_robots_txt_checker(base_url: str) -> callable:
    """Create a function to check robots.txt compliance"""
    def check_robots_compliance(url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            import urllib.robotparser
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            rp.read()
            return rp.can_fetch('*', url)
        except:
            # If robots.txt can't be read, assume allowed
            return True
    
    return check_robots_compliance

def backup_data(source_dir: str, backup_dir: str = None):
    """Create backup of scraped data"""
    if not backup_dir:
        backup_dir = f"{source_dir}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copytree(source_dir, backup_dir)
        print(f"Data backed up to: {backup_dir}")
    except Exception as e:
        print(f"Error creating backup: {e}")

def validate_scraped_data(data: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Validate scraped data quality"""
    validation_results = {
        'valid': True,
        'issues': [],
        'stats': {
            'total_posts': 0,
            'posts_with_content': 0,
            'posts_with_timestamps': 0,
            'posts_with_authors': 0
        }
    }
    
    for section_name, posts in data.items():
        validation_results['stats']['total_posts'] += len(posts)
        
        for post in posts:
            if post.get('content'):
                validation_results['stats']['posts_with_content'] += 1
            else:
                validation_results['issues'].append(f"Post missing content in {section_name}")
            
            if post.get('timestamp'):
                validation_results['stats']['posts_with_timestamps'] += 1
            
            if post.get('author'):
                validation_results['stats']['posts_with_authors'] += 1
    
    # Check data quality thresholds
    total_posts = validation_results['stats']['total_posts']
    if total_posts > 0:
        content_ratio = validation_results['stats']['posts_with_content'] / total_posts
        if content_ratio < 0.8:  # Less than 80% have content
            validation_results['valid'] = False
            validation_results['issues'].append("Low content extraction rate")
    
    return validation_results