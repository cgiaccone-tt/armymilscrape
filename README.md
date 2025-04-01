# Army.mil Web Scraper

A Python-based web scraper for Army.mil that focuses on diversity, equity, and inclusion content.

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

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
# From PowerShell/CMD:
python scraper.py

# From Bash:
python -u scraper.py
# or
PYTHONUNBUFFERED=1 python scraper.py
```

The scraper will:
- Start crawling from www.army.mil
- Search for configured keywords
- Save results in CSV and Excel formats
- Show real-time progress

To stop the scraper:
- Press Ctrl+C
- Results will be saved automatically

Note: When running from bash, always use the `-u` flag or set `PYTHONUNBUFFERED=1` to ensure:
- Real-time progress updates
- Proper handling of special characters
- Immediate error messages

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

## Running the Scraper

There are several ways to run the scraper:

1. From PowerShell or Command Prompt:
```powershell
python scraper.py
```

2. From Bash (to ensure proper output):
```bash
# Method 1: Use Python's unbuffered mode
python -u scraper.py

# Method 2: Set PYTHONUNBUFFERED environment variable
PYTHONUNBUFFERED=1 python scraper.py
```

The `-u` flag or `PYTHONUNBUFFERED=1` ensures that you see real-time output when running from bash or when redirecting output to a file. This is particularly important for monitoring the scraper's progress.

You should see output like this:
```
Initializing Army.mil web scraper...
Python version: 3.11.x
Operating system: posix
Terminal type: Interactive
Setting up Chrome WebDriver...

[1/inf] Processing: https://www.army.mil
Found 6 new URLs to crawl
[+] Found keywords: veteran, veterans
...
```

If you don't see any output, try running with the `-u` flag as shown above.

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

Several tools are provided to analyze the scraped data:

1. Quick Analysis (`quick_analysis.py`):
```bash
# From PowerShell/CMD:
python quick_analysis.py

# From Bash:
python -u quick_analysis.py
```
Provides a quick overview of the scraped data, including:
- Total pages scraped
- Unique keywords found
- Time range of scraping
- Top URLs by keyword matches

2. Detailed Analysis (`detailed_analysis.py`):
```bash
# From PowerShell/CMD:
python detailed_analysis.py

# From Bash:
python -u detailed_analysis.py
```
Performs in-depth analysis of:
- Temporal patterns
- Content patterns
- Keyword relationships
- URL structure

3. Keyword Analysis (`analyze_keywords.py`):
```bash
# From PowerShell/CMD:
python analyze_keywords.py

# From Bash:
python -u analyze_keywords.py
```
Focuses on keyword frequency and context:
- Keyword occurrence counts
- Sample contexts for each keyword
- Keyword co-occurrence patterns

4. Results Cleanup (`cleanup.py`):
```bash
# From PowerShell/CMD:
python cleanup.py

# From Bash:
python -u cleanup.py
```
Manages the results directory:
- Archives old result files
- Maintains the most recent results
- Optionally removes old files

Note: When running from bash, use the `-u` flag (e.g., `python -u script.py`) to ensure proper output handling. This ensures that:
- Output is displayed in real-time
- Special characters are handled correctly
- Progress indicators work as expected

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
