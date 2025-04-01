# Army.mil Web Scraper API Documentation

## Table of Contents
- [ArmyWebScraper](#armywebscraper)
- [Analysis Tools](#analysis-tools)
- [Configuration](#configuration)
- [Data Structures](#data-structures)

## ArmyWebScraper

The main scraper class that handles web crawling and data extraction.

### Class: `ArmyWebScraper`

```python
from scraper import ArmyWebScraper

scraper = ArmyWebScraper()
```

#### Methods

##### `scrape()`
Main entry point for the scraping process.

```python
scraper.scrape()
```

- **Returns**: None
- **Effects**: 
  - Crawls army.mil website
  - Saves results to files
  - Creates backups
  - Deduplicates results
- **Raises**:
  - `WebDriverException`: If browser initialization fails
  - `IOError`: If file operations fail

##### `save_results()`
Save results to both CSV and Excel files with deduplication.

```python
scraper.save_results()  # Normal save with deduplication
```

- **Parameters**: None
- **Returns**: None
- **Effects**:
  - Deduplicates results based on URL
  - Creates timestamped Excel file (primary)
  - Creates timestamped CSV file (legacy)
  - Keeps most recent entry for each URL

##### `is_valid_url(url)`
Check if a URL should be processed based on domain and exclusion rules.

```python
if scraper.is_valid_url("https://www.army.mil/article/123"):
    # Process URL
```

- **Parameters**:
  - `url` (str): URL to validate
- **Returns**: bool
- **Effects**: None

##### `find_keywords_in_text(text, context_chars=100)`
Find keywords in text with surrounding context.

```python
keywords, contexts = scraper.find_keywords_in_text("Some text with keywords")
```

- **Parameters**:
  - `text` (str): Text to search
  - `context_chars` (int): Characters of context to capture
- **Returns**: tuple(list, list)
  - List of found keywords
  - List of context dictionaries

## Analysis Tools

### Class: `QuickAnalysis`

Quick analysis of scraping results.

```python
from quick_analysis import analyze_results

# Run quick analysis
analyze_results()
```

#### Features
- Domain distribution
- Keyword frequency
- Content type analysis
- URL path patterns
- Content age distribution

### Class: `DetailedAnalysis`

In-depth analysis of scraping results.

```python
from detailed_analysis import run_detailed_analysis

# Run detailed analysis
run_detailed_analysis()
```

#### Features
- Keyword co-occurrence analysis
- Content age trends
- URL structure analysis
- Keyword context examples
- Report generation

### Class: `KeywordAnalyzer`

Focused keyword analysis tool.

```python
from analyze_keywords import analyze_keywords

# Analyze specific keywords
analyze_keywords()
```

#### Features
- Keyword frequency analysis
- Context extraction
- Usage examples

### Class: `CleanupUtility`

Results cleanup and management tool.

```python
from cleanup import cleanup_results

# Run cleanup utility
cleanup_results()
```

#### Features
- Individual file removal
- Age-based cleanup
- File type organization
- Interactive interface

## Configuration

The scraper and analysis tools are configured through `config.py`.

### URL Filtering

```python
# Excluded paths
EXCLUDED_PATHS = [
    '/downloads/',
    '/media/',
    '/pdf/'
]

# Excluded file types
EXCLUDED_FILE_TYPES = [
    '.pdf', '.doc', '.docx',
    '.mp3', '.mp4', '.zip'
]
```

### Scraper Settings

```python
SETTINGS = {
    'NUM_BROWSERS': 4,
    'PAGE_LOAD_TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
    'CONTEXT_CHARS': 100
}
```

## Data Structures

### Results DataFrame

The scraper outputs results in both Excel and CSV formats with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| url | string | Full URL of the page |
| title | string | Page title |
| keywords_found | string | Comma-separated list of found keywords |
| page_content | string | Cleaned page content |
| timestamp | datetime | Scraping timestamp |
| last_modified | datetime | Page's last modified date |

### Analysis Output

Analysis tools generate reports with the following metrics:

1. **Quick Analysis**:
   - Domain counts
   - Keyword frequencies
   - Content type distribution
   - URL patterns
   - Age distribution

2. **Detailed Analysis**:
   - Keyword co-occurrences
   - Content trends
   - URL structure patterns
   - Context examples
   - Comprehensive statistics

## Error Handling

All tools include robust error handling:

```python
try:
    scraper.scrape()
except WebDriverException as e:
    # Handle browser errors
except IOError as e:
    # Handle file operation errors
except Exception as e:
    # Handle unexpected errors
```

## Best Practices

1. **URL Filtering**:
   - Keep `EXCLUDED_PATHS` and `EXCLUDED_FILE_TYPES` updated
   - Use domain validation for security

2. **Data Management**:
   - Run cleanup regularly
   - Monitor disk space usage
   - Keep backups of important results

3. **Analysis**:
   - Start with quick analysis
   - Use detailed analysis for specific insights
   - Export reports for documentation
