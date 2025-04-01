# Army.mil Web Scraper

A robust Python web scraper designed to crawl www.army.mil and search for specified keywords and phrases. Features automatic file saving, backup management, and comprehensive error handling.

## Features

- **Smart Crawling**
  - Intelligent URL filtering with configurable exclusions
  - Automatic retry on failures
  - Progress tracking and auto-saving
  - Duplicate URL detection and removal

- **Data Collection**
  - Keyword matching with context
  - Last modified date extraction
  - Clean text processing
  - Structured data output
  - Deduplication of results

- **Analysis Tools**
  - Quick analysis script for basic insights
  - Detailed analysis for in-depth metrics
  - Keyword frequency and co-occurrence analysis
  - Content age distribution analysis
  - URL structure analysis

- **File Management**
  - Organized results directory
  - Timestamped Excel and CSV files
  - Automatic backups
  - Cleanup utilities with age-based filtering
  - Deduplication of historical results

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome browser installed (latest version recommended)

3. Configure settings in `config.py`:
   - Modify `KEYWORDS` list
   - Adjust URL exclusion patterns if needed
   - Customize scraper settings

4. Run the scraper:
```bash
python scraper.py
```

## Configuration

The `config.py` file contains all configurable settings:

```python
# URL filtering
EXCLUDED_PATHS = [
    '/downloads/',
    '/media/',
    '/pdf/',
    # Add more exclusions as needed
]

EXCLUDED_FILE_TYPES = [
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.zip', '.rar', '.mp3',
    '.mp4', '.avi', '.mov'
]

# Scraper settings
SETTINGS = {
    # Browser settings
    'NUM_BROWSERS': 4,          # Number of parallel browser instances
    'PAGE_LOAD_TIMEOUT': 30,    # Seconds to wait for page load
    'ELEMENT_TIMEOUT': 10,      # Seconds to wait for elements
    'RETRY_ATTEMPTS': 3,        # Number of times to retry failed requests
    'RETRY_DELAY': 2,          # Seconds to wait between retries
    
    # Rate limiting
    'PAGE_LOAD_DELAY': 2,      # Seconds between page loads
    'SAVE_INTERVAL': 30,       # Seconds between auto-saves
    'NO_PROGRESS_TIMEOUT': 60, # Seconds to wait with no progress
    
    # Content extraction
    'CONTEXT_CHARS': 100,      # Characters to capture around keywords
    'MAX_CONTENT_LENGTH': 100000,  # Maximum characters per page
    
    # File handling
    'BACKUP_FILES': True,      # Whether to keep backup files
    'COMPRESS_BACKUPS': True,  # Whether to compress backup files
    'MAX_BACKUPS': 5,         # Maximum number of backup files
}
```

## Directory Structure

```
armymilscrape/
├── config.py             # Configuration settings
├── scraper.py           # Main scraper implementation
├── analyze_keywords.py  # Keyword analysis tool
├── quick_analysis.py   # Quick statistics and insights
├── detailed_analysis.py # In-depth analysis tool
├── cleanup.py          # Results cleanup utility
├── requirements.txt     # Python dependencies
├── results/            # Output directory
│   ├── army_results_*.xlsx  # Excel output files (primary)
│   ├── army_results_*.csv   # CSV output files (legacy)
│   └── backups/            # Compressed backups
├── README.md            # This documentation
└── API.md              # API documentation
```

## Analysis Tools

The project includes several analysis tools:

1. **Quick Analysis** (`quick_analysis.py`):
   - Domain distribution
   - Keyword frequency
   - Content type analysis
   - URL path patterns
   - Content age distribution

2. **Detailed Analysis** (`detailed_analysis.py`):
   - Keyword co-occurrence analysis
   - Content age trends
   - URL structure analysis
   - Keyword context examples
   - Comprehensive report generation

3. **Keyword Analysis** (`analyze_keywords.py`):
   - Specific keyword frequency
   - Keyword context extraction
   - Detailed examples of keyword usage

4. **Cleanup Utility** (`cleanup.py`):
   - Remove individual files
   - Age-based cleanup
   - File type organization
   - Backup management

## Output Files

The scraper generates two types of output files:

1. **Excel Files** (Primary):
   - Format: `army_results_YYYYMMDD_HHMMSS.xlsx`
   - Contains all scraped data
   - Includes metadata and timestamps
   - Deduplication applied

2. **CSV Files** (Legacy):
   - Format: `army_results_YYYYMMDD_HHMMSS.csv`
   - Basic data format
   - Compatible with older tools

## License

This project is proprietary and confidential. All rights reserved.
