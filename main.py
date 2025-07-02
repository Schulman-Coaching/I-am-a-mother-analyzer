"""
Main application for Imamother Forum Scraper
"""
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List

from scraper import ImamotherScraper
from config import ScrapingConfig
from utils import (
    setup_logging, generate_summary_stats, validate_scraped_data,
    backup_data, create_robots_txt_checker
)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Imamother Forum Scraper')
    parser.add_argument('--sections', nargs='+', 
                       choices=list(ScrapingConfig.FORUM_SECTIONS.keys()),
                       help='Specific sections to scrape')
    parser.add_argument('--max-pages', type=int, default=None,
                       help='Maximum pages per section')
    parser.add_argument('--output-dir', default=ScrapingConfig.OUTPUT_DIR,
                       help='Output directory for scraped data')
    parser.add_argument('--config-file', help='Custom configuration file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test login and configuration without scraping')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup of existing data before scraping')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate existing scraped data')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(ScrapingConfig.LOG_LEVEL, ScrapingConfig.LOG_FILE)
    logger.info("Starting Imamother Forum Scraper")
    
    # Validate configuration
    if not ScrapingConfig.validate_config():
        logger.error("Configuration validation failed")
        print("\nPlease set the following environment variables:")
        print("IMAMOTHER_USERNAME=your_username")
        print("IMAMOTHER_PASSWORD=your_password")
        sys.exit(1)
    
    # Handle validate-only mode
    if args.validate_only:
        validate_existing_data(args.output_dir)
        return
    
    # Create backup if requested
    if args.backup and os.path.exists(args.output_dir):
        backup_data(args.output_dir)
    
    # Initialize scraper
    try:
        with ImamotherScraper() as scraper:
            # Test login
            logger.info("Attempting to log in...")
            if not scraper.login():
                logger.error("Login failed. Please check credentials.")
                sys.exit(1)
            
            logger.info("Login successful!")
            
            if args.dry_run:
                logger.info("Dry run completed successfully")
                return
            
            # Check robots.txt compliance
            robots_checker = create_robots_txt_checker(ScrapingConfig.BASE_URL)
            
            # Determine sections to scrape
            sections_to_scrape = args.sections or list(ScrapingConfig.FORUM_SECTIONS.keys())
            logger.info(f"Scraping sections: {sections_to_scrape}")
            
            # Scrape data
            all_scraped_data = {}
            
            for section in sections_to_scrape:
                logger.info(f"Starting section: {section}")
                
                # Check robots.txt for section URL
                section_url = ScrapingConfig.BASE_URL + ScrapingConfig.FORUM_SECTIONS[section]
                if not robots_checker(section_url):
                    logger.warning(f"Section {section} disallowed by robots.txt, skipping")
                    continue
                
                try:
                    section_data = scraper.scrape_section(section, args.max_pages)
                    all_scraped_data[section] = section_data
                    logger.info(f"Completed section {section}: {len(section_data)} posts")
                    
                except Exception as e:
                    logger.error(f"Error scraping section {section}: {e}")
                    continue
            
            # Save scraped data
            if all_scraped_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scraper.save_data(all_scraped_data, f"imamother_scrape_{timestamp}")
                
                # Generate and save summary statistics
                stats = generate_summary_stats(all_scraped_data)
                stats_file = os.path.join(args.output_dir, f"summary_stats_{timestamp}.json")
                
                import json
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, default=str)
                
                logger.info(f"Summary statistics saved to: {stats_file}")
                
                # Validate scraped data
                validation_results = validate_scraped_data(all_scraped_data)
                if validation_results['valid']:
                    logger.info("Data validation passed")
                else:
                    logger.warning("Data validation issues found:")
                    for issue in validation_results['issues']:
                        logger.warning(f"  - {issue}")
                
                # Print summary
                print_scraping_summary(all_scraped_data, stats)
                
            else:
                logger.warning("No data was scraped")
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def validate_existing_data(output_dir: str):
    """Validate existing scraped data"""
    logger = setup_logging()
    
    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        return
    
    # Find JSON data files
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and 'imamother_scrape' in f]
    
    if not json_files:
        logger.error("No scraped data files found")
        return
    
    # Validate most recent file
    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))
    file_path = os.path.join(output_dir, latest_file)
    
    logger.info(f"Validating data file: {latest_file}")
    
    try:
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        validation_results = validate_scraped_data(data)
        
        if validation_results['valid']:
            print("✅ Data validation passed")
        else:
            print("❌ Data validation failed")
            for issue in validation_results['issues']:
                print(f"  - {issue}")
        
        # Print stats
        stats = validation_results['stats']
        print(f"\nData Statistics:")
        print(f"  Total posts: {stats['total_posts']}")
        print(f"  Posts with content: {stats['posts_with_content']}")
        print(f"  Posts with timestamps: {stats['posts_with_timestamps']}")
        print(f"  Posts with authors: {stats['posts_with_authors']}")
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")

def print_scraping_summary(data: Dict[str, List], stats: Dict):
    """Print a summary of scraping results"""
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    
    print(f"Total posts scraped: {stats['total_posts']}")
    print(f"Sections scraped: {len(stats['sections'])}")
    
    print("\nPosts by section:")
    for section, count in stats['sections'].items():
        print(f"  {section}: {count} posts")
    
    print(f"\nEngagement Statistics:")
    eng_stats = stats['engagement_stats']
    print(f"  Average replies per post: {eng_stats['avg_replies']:.1f}")
    print(f"  Average views per post: {eng_stats['avg_views']:.1f}")
    print(f"  High engagement posts: {eng_stats['high_engagement_posts']}")
    
    print(f"\nContent Analysis:")
    content_stats = stats['content_analysis']
    print(f"  Questions identified: {content_stats['questions']}")
    print(f"  Answers identified: {content_stats['answers']}")
    print(f"  Resource mentions: {content_stats['resource_mentions']}")
    
    print(f"\nBusiness Opportunities:")
    biz_stats = stats['business_opportunities']
    for category, count in biz_stats.items():
        if count > 0:
            print(f"  {category.title()}: {count} posts")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()