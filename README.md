# Imamother Forum Scraper

A comprehensive, ethical web scraping tool designed specifically for extracting structured data from the Imamother.com forum. This tool focuses on high-value forum sections to identify business opportunities and analyze community discussions while respecting privacy and community guidelines.

## 🎯 Purpose

This scraper is designed to extract valuable business intelligence from Imamother forum discussions, focusing on:

- **Question-answer pairs** from community discussions
- **User interaction patterns** and engagement metrics
- **Temporal patterns** to identify seasonal trends
- **Resource recommendations** mentioned in posts
- **Business opportunity identification** across different categories

## 🚀 Features

### Core Functionality
- **Authenticated Access**: Secure login system for accessing forum content
- **Rate Limiting**: Respectful scraping with configurable delays (1-2 requests/second)
- **Session Management**: Maintains login state throughout scraping sessions
- **Error Handling**: Robust retry mechanisms and anti-scraping countermeasures

### Data Extraction
- **Multi-Section Support**: Targets high-value forum sections:
  - Pregnancy & Childbirth discussions
  - Married Life advice threads
  - Religious guidance (Taharas Hamishpacha)
  - Infertility support discussions
- **Structured Output**: JSON and CSV formats for easy analysis
- **Content Analysis**: Automatic categorization of questions, answers, and resources

### Ethical Compliance
- **Privacy Protection**: Username anonymization and sensitive content filtering
- **Robots.txt Compliance**: Respects website crawling policies
- **User-Agent Rotation**: Prevents detection through varied request headers
- **Community Guidelines**: Focuses on public discussions only

### Business Intelligence
- **Opportunity Categorization**: Classifies posts by business potential
- **Engagement Scoring**: Identifies high-value discussions
- **Trend Analysis**: Temporal patterns and seasonal insights
- **Resource Extraction**: Product and service mentions for market analysis

## 📋 Requirements

- Python 3.8+
- Valid Imamother.com account credentials
- Internet connection
- 500MB+ free disk space (depending on scraping scope)

## 🛠️ Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your Imamother credentials:
   ```
   IMAMOTHER_USERNAME=your_username
   IMAMOTHER_PASSWORD=your_password
   ```

## 🚀 Usage

### Basic Usage

**Scrape all sections**:
```bash
python main.py
```

**Scrape specific sections**:
```bash
python main.py --sections pregnancy_childbirth married_life
```

**Limit pages per section**:
```bash
python main.py --max-pages 10
```

### Advanced Options

**Test configuration (dry run)**:
```bash
python main.py --dry-run
```

**Create backup before scraping**:
```bash
python main.py --backup
```

**Validate existing data**:
```bash
python main.py --validate-only
```

**Custom output directory**:
```bash
python main.py --output-dir custom_data_folder
```

### Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--sections` | Specific sections to scrape | `--sections pregnancy_childbirth married_life` |
| `--max-pages` | Maximum pages per section | `--max-pages 25` |
| `--output-dir` | Custom output directory | `--output-dir my_data` |
| `--dry-run` | Test without scraping | `--dry-run` |
| `--backup` | Backup existing data | `--backup` |
| `--validate-only` | Validate existing data | `--validate-only` |

## 📊 Output Structure

### Data Files
```
scraped_data/
├── imamother_scrape_20240102_143022.json    # Complete dataset
├── imamother_scrape_pregnancy_childbirth_20240102_143022.csv
├── imamother_scrape_married_life_20240102_143022.csv
├── summary_stats_20240102_143022.json       # Analytics summary
└── scraper.log                              # Execution logs
```

### Data Schema

Each scraped post contains:

```json
{
  "section": "pregnancy_childbirth",
  "post_id": "12345",
  "author": "UxxxxxxxX",
  "timestamp": "2024-01-02T14:30:22",
  "title": "Question about...",
  "content": "Post content here...",
  "replies_count": 15,
  "views_count": 234,
  "tags": ["pregnancy", "advice"],
  "links": [{"url": "...", "text": "...", "type": "external"}],
  "is_question": true,
  "is_answer": false,
  "sentiment_indicators": ["worried", "hopeful"],
  "resource_mentions": ["book", "doctor"],
  "keywords": ["pregnancy", "symptoms", "advice"]
}
```

### Summary Statistics

The tool generates comprehensive analytics:

- **Engagement Metrics**: Average replies, views, high-engagement posts
- **Content Analysis**: Questions vs answers, resource mentions
- **Business Opportunities**: Categorized by type (product, service, information, community)
- **Temporal Patterns**: Posts by hour/day for trend analysis
- **Section Breakdown**: Post counts and engagement by forum section

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IMAMOTHER_USERNAME` | Forum username | Required |
| `IMAMOTHER_PASSWORD` | Forum password | Required |
| `REQUEST_DELAY` | Seconds between requests | 1.5 |
| `MAX_PAGES_PER_SECTION` | Pages to scrape per section | 50 |
| `OUTPUT_DIR` | Data output directory | scraped_data |
| `LOG_LEVEL` | Logging verbosity | INFO |

### Customization

Edit [`config.py`](config.py) to modify:
- Forum sections to scrape
- Rate limiting parameters
- Output formats
- User agent rotation
- Business intelligence keywords

## 🔒 Privacy & Ethics

### Privacy Protection
- **Username Anonymization**: Usernames are masked (e.g., "Username" → "UxxxxxxxX")
- **Content Filtering**: Excludes personal/sensitive information
- **Public Content Only**: Focuses on publicly accessible discussions

### Ethical Guidelines
- **Rate Limiting**: Prevents server overload with configurable delays
- **Robots.txt Compliance**: Respects website crawling policies
- **Community Respect**: Avoids disrupting normal forum operations
- **Data Minimization**: Extracts only necessary information for analysis

### Legal Compliance
- Designed for research and business intelligence purposes
- Users responsible for compliance with local laws and website terms
- Recommends reviewing Imamother.com terms of service before use

## 🐛 Troubleshooting

### Common Issues

**Login Failed**:
- Verify credentials in `.env` file
- Check if account is active and not suspended
- Ensure 2FA is disabled or properly configured

**No Data Extracted**:
- Run with `--dry-run` to test login
- Check logs in `scraper.log` for detailed errors
- Verify forum sections are accessible

**Rate Limiting Errors**:
- Increase `REQUEST_DELAY` in config
- Check if IP is temporarily blocked
- Try again after waiting period

**Memory Issues**:
- Reduce `MAX_PAGES_PER_SECTION`
- Process sections individually
- Clear output directory of old files

### Debug Mode

Enable detailed logging:
```bash
# Edit config.py
LOG_LEVEL = "DEBUG"
```

## 📈 Business Intelligence Features

### Opportunity Categories

The tool automatically categorizes posts into business opportunities:

1. **Product Opportunities**: Product recommendations, reviews, comparisons
2. **Service Opportunities**: Professional services, consultations, support
3. **Information Opportunities**: Educational content, guides, resources
4. **Community Opportunities**: Support groups, meetups, connections

### Engagement Scoring

Posts are scored based on:
- Reply-to-view ratio
- Question/answer classification
- Resource mention frequency
- Community interaction patterns

### Market Analysis

Extract insights for:
- **Product Demand**: What products are frequently discussed/recommended
- **Service Gaps**: Unmet needs expressed in questions
- **Seasonal Trends**: Temporal patterns in discussions
- **Community Pain Points**: Recurring problems and frustrations

## 🤝 Contributing

This tool is designed for research and business intelligence purposes. When contributing:

1. Maintain ethical scraping practices
2. Respect privacy and anonymization features
3. Follow rate limiting guidelines
4. Test thoroughly before submitting changes

## ⚠️ Disclaimer

This tool is provided for research and business intelligence purposes. Users are responsible for:

- Complying with Imamother.com terms of service
- Respecting community guidelines and privacy
- Following applicable laws and regulations
- Using scraped data ethically and responsibly

The authors are not responsible for misuse of this tool or any consequences arising from its use.

## 📝 License

This project is provided as-is for educational and research purposes. Please ensure compliance with all applicable laws and website terms of service before use.

---

**Last Updated**: January 2024
**Version**: 1.0.0