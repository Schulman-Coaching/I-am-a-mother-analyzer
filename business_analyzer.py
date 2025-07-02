"""
Business Intelligence Analyzer for Imamother Forum Data
"""
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import re
import os

class BusinessIntelligenceAnalyzer:
    """Advanced analytics for scraped forum data"""
    
    def __init__(self):
        self.data = None
        self.df = None
        
    def load_data(self, data_path: str) -> bool:
        """Load scraped data from JSON file"""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Convert to DataFrame for easier analysis
            all_posts = []
            for section, posts in self.data.items():
                for post in posts:
                    post['section'] = section
                    all_posts.append(post)
            
            self.df = pd.DataFrame(all_posts)
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_market_opportunities(self) -> Dict[str, Any]:
        """Identify and analyze market opportunities"""
        if self.df is None or self.df.empty:
            return {}
        
        opportunities = {
            'product_opportunities': self._analyze_product_opportunities(),
            'service_opportunities': self._analyze_service_opportunities(),
            'content_opportunities': self._analyze_content_opportunities(),
            'community_opportunities': self._analyze_community_opportunities(),
            'seasonal_trends': self._analyze_seasonal_trends(),
            'pain_points': self._identify_pain_points(),
            'resource_gaps': self._identify_resource_gaps()
        }
        
        return opportunities
    
    def _analyze_product_opportunities(self) -> Dict[str, Any]:
        """Analyze product-related opportunities"""
        product_keywords = [
            'product', 'buy', 'purchase', 'recommend', 'brand', 'quality',
            'where to find', 'best', 'review', 'comparison', 'price', 'cost',
            'store', 'online', 'amazon', 'target', 'walmart'
        ]
        
        product_posts = self.df[
            self.df['content'].str.contains('|'.join(product_keywords), case=False, na=False)
        ]
        
        # Extract mentioned products/brands
        product_mentions = []
        for content in product_posts['content']:
            # Look for capitalized words that might be brand names
            brands = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', str(content))
            product_mentions.extend(brands)
        
        product_counter = Counter(product_mentions)
        
        return {
            'total_product_posts': len(product_posts),
            'top_mentioned_products': dict(product_counter.most_common(20)),
            'avg_engagement': product_posts['replies_count'].mean() if not product_posts.empty else 0,
            'high_engagement_products': self._get_high_engagement_posts(product_posts, 'product'),
            'sections_with_most_product_discussions': product_posts['section'].value_counts().to_dict()
        }
    
    def _analyze_service_opportunities(self) -> Dict[str, Any]:
        """Analyze service-related opportunities"""
        service_keywords = [
            'service', 'help', 'professional', 'expert', 'consultation',
            'advice', 'guidance', 'support', 'therapy', 'counseling',
            'doctor', 'specialist', 'coach', 'trainer', 'tutor'
        ]
        
        service_posts = self.df[
            self.df['content'].str.contains('|'.join(service_keywords), case=False, na=False)
        ]
        
        # Categorize service types
        service_categories = {
            'medical': ['doctor', 'specialist', 'medical', 'health', 'therapy'],
            'educational': ['tutor', 'teacher', 'education', 'learn', 'class'],
            'counseling': ['counseling', 'therapy', 'support', 'guidance'],
            'professional': ['consultant', 'expert', 'professional', 'service']
        }
        
        category_counts = {}
        for category, keywords in service_categories.items():
            category_posts = service_posts[
                service_posts['content'].str.contains('|'.join(keywords), case=False, na=False)
            ]
            category_counts[category] = len(category_posts)
        
        return {
            'total_service_posts': len(service_posts),
            'service_categories': category_counts,
            'avg_engagement': service_posts['replies_count'].mean() if not service_posts.empty else 0,
            'high_engagement_services': self._get_high_engagement_posts(service_posts, 'service'),
            'unmet_service_needs': self._identify_unmet_needs(service_posts)
        }
    
    def _analyze_content_opportunities(self) -> Dict[str, Any]:
        """Analyze content and information opportunities"""
        content_keywords = [
            'information', 'learn', 'understand', 'explain', 'guide',
            'tutorial', 'how to', 'what is', 'resource', 'book',
            'article', 'website', 'blog', 'video', 'course'
        ]
        
        content_posts = self.df[
            self.df['content'].str.contains('|'.join(content_keywords), case=False, na=False)
        ]
        
        # Extract topics people want to learn about
        learning_topics = []
        for content in content_posts['content']:
            # Look for "how to" patterns
            how_to_matches = re.findall(r'how to ([^.!?]+)', str(content), re.IGNORECASE)
            learning_topics.extend(how_to_matches)
            
            # Look for "what is" patterns
            what_is_matches = re.findall(r'what is ([^.!?]+)', str(content), re.IGNORECASE)
            learning_topics.extend(what_is_matches)
        
        topic_counter = Counter([topic.strip()[:50] for topic in learning_topics])
        
        return {
            'total_content_posts': len(content_posts),
            'top_learning_topics': dict(topic_counter.most_common(15)),
            'content_format_preferences': self._analyze_content_formats(content_posts),
            'knowledge_gaps': self._identify_knowledge_gaps(content_posts)
        }
    
    def _analyze_community_opportunities(self) -> Dict[str, Any]:
        """Analyze community and social opportunities"""
        community_keywords = [
            'group', 'community', 'support', 'meet', 'connect',
            'share', 'experience', 'similar', 'together', 'local',
            'meetup', 'event', 'gathering', 'club'
        ]
        
        community_posts = self.df[
            self.df['content'].str.contains('|'.join(community_keywords), case=False, na=False)
        ]
        
        return {
            'total_community_posts': len(community_posts),
            'community_needs': self._identify_community_needs(community_posts),
            'geographic_patterns': self._analyze_geographic_patterns(community_posts),
            'support_group_opportunities': self._identify_support_groups(community_posts)
        }
    
    def _analyze_seasonal_trends(self) -> Dict[str, Any]:
        """Analyze seasonal and temporal trends"""
        if 'timestamp' not in self.df.columns:
            return {'error': 'No timestamp data available'}
        
        # Convert timestamps
        self.df['datetime'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
        self.df['month'] = self.df['datetime'].dt.month
        self.df['day_of_week'] = self.df['datetime'].dt.day_name()
        self.df['hour'] = self.df['datetime'].dt.hour
        
        return {
            'posts_by_month': self.df['month'].value_counts().to_dict(),
            'posts_by_day': self.df['day_of_week'].value_counts().to_dict(),
            'posts_by_hour': self.df['hour'].value_counts().to_dict(),
            'seasonal_topics': self._identify_seasonal_topics()
        }
    
    def _identify_pain_points(self) -> List[Dict[str, Any]]:
        """Identify common pain points and frustrations"""
        pain_keywords = [
            'frustrated', 'annoyed', 'difficult', 'hard', 'struggle',
            'problem', 'issue', 'trouble', 'worry', 'stress',
            'help', 'desperate', 'confused', 'lost'
        ]
        
        pain_posts = self.df[
            self.df['content'].str.contains('|'.join(pain_keywords), case=False, na=False)
        ]
        
        # Extract pain point themes
        pain_points = []
        for _, post in pain_posts.iterrows():
            content = str(post['content'])
            section = post['section']
            
            # Simple pain point extraction
            sentences = content.split('.')
            pain_sentences = [
                s.strip() for s in sentences 
                if any(keyword in s.lower() for keyword in pain_keywords)
            ]
            
            for sentence in pain_sentences[:2]:  # Limit to first 2 relevant sentences
                if len(sentence) > 20:
                    pain_points.append({
                        'text': sentence[:200],
                        'section': section,
                        'engagement': post.get('replies_count', 0)
                    })
        
        # Sort by engagement
        pain_points.sort(key=lambda x: x['engagement'], reverse=True)
        return pain_points[:20]
    
    def _identify_resource_gaps(self) -> Dict[str, List[str]]:
        """Identify gaps in available resources"""
        question_posts = self.df[self.df['is_question'] == True]
        
        gaps_by_section = {}
        for section in question_posts['section'].unique():
            section_questions = question_posts[question_posts['section'] == section]
            
            # Look for unanswered or low-engagement questions
            low_engagement = section_questions[section_questions['replies_count'] <= 2]
            
            gaps = []
            for _, post in low_engagement.iterrows():
                title = post.get('title', '')
                content = str(post.get('content', ''))[:150]
                
                if title or content:
                    gaps.append(title or content)
            
            gaps_by_section[section] = gaps[:10]  # Top 10 gaps per section
        
        return gaps_by_section
    
    def _get_high_engagement_posts(self, posts_df: pd.DataFrame, category: str) -> List[Dict]:
        """Get high engagement posts for a category"""
        if posts_df.empty:
            return []
        
        # Sort by engagement (replies + views)
        posts_df['total_engagement'] = posts_df['replies_count'] + (posts_df['views_count'] * 0.1)
        top_posts = posts_df.nlargest(5, 'total_engagement')
        
        results = []
        for _, post in top_posts.iterrows():
            results.append({
                'title': post.get('title', 'No title'),
                'content_preview': str(post.get('content', ''))[:200],
                'replies': post.get('replies_count', 0),
                'views': post.get('views_count', 0),
                'section': post.get('section', '')
            })
        
        return results
    
    def _identify_unmet_needs(self, service_posts: pd.DataFrame) -> List[str]:
        """Identify unmet service needs"""
        if service_posts.empty:
            return []
        
        # Look for posts with questions but few replies
        unmet_needs = service_posts[
            (service_posts['is_question'] == True) & 
            (service_posts['replies_count'] <= 3)
        ]
        
        needs = []
        for _, post in unmet_needs.iterrows():
            content = str(post.get('content', ''))
            if len(content) > 50:
                needs.append(content[:150])
        
        return needs[:10]
    
    def _analyze_content_formats(self, content_posts: pd.DataFrame) -> Dict[str, int]:
        """Analyze preferred content formats"""
        formats = {
            'video': ['video', 'youtube', 'watch', 'tutorial video'],
            'article': ['article', 'blog', 'read', 'written'],
            'book': ['book', 'ebook', 'read', 'author'],
            'course': ['course', 'class', 'learn', 'training'],
            'podcast': ['podcast', 'listen', 'audio']
        }
        
        format_counts = {}
        for format_name, keywords in formats.items():
            count = 0
            for content in content_posts['content']:
                if any(keyword in str(content).lower() for keyword in keywords):
                    count += 1
            format_counts[format_name] = count
        
        return format_counts
    
    def _identify_knowledge_gaps(self, content_posts: pd.DataFrame) -> List[str]:
        """Identify knowledge gaps"""
        gaps = []
        for content in content_posts['content']:
            content_str = str(content).lower()
            if 'don\'t know' in content_str or 'not sure' in content_str or 'confused' in content_str:
                # Extract the topic they're confused about
                sentences = content_str.split('.')
                for sentence in sentences:
                    if any(phrase in sentence for phrase in ['don\'t know', 'not sure', 'confused']):
                        gaps.append(sentence.strip()[:100])
                        break
        
        return gaps[:15]
    
    def _identify_community_needs(self, community_posts: pd.DataFrame) -> List[str]:
        """Identify community needs"""
        needs = []
        for content in community_posts['content']:
            content_str = str(content).lower()
            if 'looking for' in content_str or 'need' in content_str or 'want to connect' in content_str:
                sentences = content_str.split('.')
                for sentence in sentences:
                    if any(phrase in sentence for phrase in ['looking for', 'need', 'want to connect']):
                        needs.append(sentence.strip()[:100])
                        break
        
        return needs[:10]
    
    def _analyze_geographic_patterns(self, community_posts: pd.DataFrame) -> Dict[str, int]:
        """Analyze geographic patterns in community posts"""
        # Common location indicators
        locations = ['local', 'area', 'city', 'state', 'brooklyn', 'manhattan', 'queens', 
                    'lakewood', 'monsey', 'baltimore', 'chicago', 'detroit', 'cleveland']
        
        location_counts = {}
        for location in locations:
            count = sum(1 for content in community_posts['content'] 
                       if location in str(content).lower())
            if count > 0:
                location_counts[location] = count
        
        return location_counts
    
    def _identify_support_groups(self, community_posts: pd.DataFrame) -> List[str]:
        """Identify potential support group opportunities"""
        support_keywords = ['support group', 'support', 'group', 'meet others', 'similar situation']
        
        support_opportunities = []
        for content in community_posts['content']:
            content_str = str(content).lower()
            if any(keyword in content_str for keyword in support_keywords):
                # Extract the type of support needed
                sentences = content_str.split('.')
                for sentence in sentences:
                    if any(keyword in sentence for keyword in support_keywords):
                        support_opportunities.append(sentence.strip()[:100])
                        break
        
        return support_opportunities[:10]
    
    def _identify_seasonal_topics(self) -> Dict[str, List[str]]:
        """Identify topics that vary by season"""
        seasonal_keywords = {
            'spring': ['passover', 'pesach', 'spring cleaning', 'allergy'],
            'summer': ['camp', 'vacation', 'summer', 'heat'],
            'fall': ['school', 'rosh hashana', 'yom kippur', 'sukkos'],
            'winter': ['chanukah', 'cold', 'winter', 'flu']
        }
        
        seasonal_topics = {}
        for season, keywords in seasonal_keywords.items():
            topics = []
            for keyword in keywords:
                posts_with_keyword = self.df[
                    self.df['content'].str.contains(keyword, case=False, na=False)
                ]
                if not posts_with_keyword.empty:
                    topics.append(f"{keyword}: {len(posts_with_keyword)} posts")
            seasonal_topics[season] = topics
        
        return seasonal_topics
    
    def generate_business_report(self, output_path: str = None) -> str:
        """Generate comprehensive business intelligence report"""
        if self.df is None or self.df.empty:
            return "No data available for analysis"
        
        opportunities = self.analyze_market_opportunities()
        
        report = []
        report.append("# IMAMOTHER FORUM BUSINESS INTELLIGENCE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Posts Analyzed: {len(self.df)}")
        report.append("")
        
        # Product Opportunities
        product_ops = opportunities.get('product_opportunities', {})
        report.append("## PRODUCT OPPORTUNITIES")
        report.append(f"Total product-related posts: {product_ops.get('total_product_posts', 0)}")
        report.append("Top mentioned products:")
        for product, count in list(product_ops.get('top_mentioned_products', {}).items())[:10]:
            report.append(f"  - {product}: {count} mentions")
        report.append("")
        
        # Service Opportunities
        service_ops = opportunities.get('service_opportunities', {})
        report.append("## SERVICE OPPORTUNITIES")
        report.append(f"Total service-related posts: {service_ops.get('total_service_posts', 0)}")
        report.append("Service categories:")
        for category, count in service_ops.get('service_categories', {}).items():
            report.append(f"  - {category.title()}: {count} posts")
        report.append("")
        
        # Pain Points
        pain_points = opportunities.get('pain_points', [])
        report.append("## TOP PAIN POINTS")
        for i, pain in enumerate(pain_points[:10], 1):
            report.append(f"{i}. {pain['text']} (Section: {pain['section']}, Engagement: {pain['engagement']})")
        report.append("")
        
        # Resource Gaps
        gaps = opportunities.get('resource_gaps', {})
        report.append("## RESOURCE GAPS BY SECTION")
        for section, section_gaps in gaps.items():
            if section_gaps:
                report.append(f"### {section.title()}")
                for gap in section_gaps[:5]:
                    report.append(f"  - {gap}")
                report.append("")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Business intelligence report saved to: {output_path}")
        
        return report_text

def main():
    """Example usage of BusinessIntelligenceAnalyzer"""
    analyzer = BusinessIntelligenceAnalyzer()
    
    # Look for the most recent data file
    data_dir = "scraped_data"
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and 'imamother_scrape' in f]
        if json_files:
            latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))
            data_path = os.path.join(data_dir, latest_file)
            
            print(f"Analyzing data from: {latest_file}")
            
            if analyzer.load_data(data_path):
                # Generate business intelligence report
                report_path = os.path.join(data_dir, f"business_intelligence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                report = analyzer.generate_business_report(report_path)
                print("\nBusiness Intelligence Analysis Complete!")
                print(f"Report saved to: {report_path}")
            else:
                print("Failed to load data")
        else:
            print("No scraped data files found")
    else:
        print("Scraped data directory not found")

if __name__ == "__main__":
    main()