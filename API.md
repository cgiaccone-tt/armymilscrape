# Army.mil Web Scraper API Documentation

## Table of Contents
- [ArmyWebScraper](#armywebscraper)
- [BackupManager](#backupmanager)
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
- **Raises**:
  - `WebDriverException`: If browser initialization fails
  - `IOError`: If file operations fail

##### `save_results(is_backup=False)`
Save results to both CSV and Excel files.

```python
scraper.save_results()  # Normal save
scraper.save_results(is_backup=True)  # Backup save
```

- **Parameters**:
  - `is_backup` (bool): Whether this is a backup save
- **Returns**: None
- **Effects**:
  - Creates timestamped files
  - Attempts multiple encodings if needed
  - Creates compressed backups

##### `clean_text_for_csv(text)`
Clean text for CSV output.

```python
cleaned = scraper.clean_text_for_csv("Some text\nwith newlines")
```

- **Parameters**:
  - `text` (str): Text to clean
- **Returns**: str
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

## BackupManager

Handles file backups and restoration.

### Class: `BackupManager`

```python
from backup_manager import BackupManager

manager = BackupManager()
```

#### Methods

##### `create_backup(file_path)`
Create a backup of a file.

```python
manager.create_backup("/path/to/file.csv")
```

- **Parameters**:
  - `file_path` (str): Path to file to backup
- **Returns**: None
- **Effects**:
  - Creates compressed backup
  - Manages backup rotation

##### `restore_backup(backup_file)`
Restore a file from backup.

```python
manager.restore_backup("army_results_20250331_120000.csv.gz")
```

- **Parameters**:
  - `backup_file` (str): Name of backup file to restore
- **Returns**: bool
  - True if restoration successful
  - False if failed
- **Effects**:
  - Decompresses backup
  - Restores to original location

##### `list_backups()`
List all available backups.

```python
backups = manager.list_backups()
```

- **Returns**: list
  - List of backup file paths
- **Effects**:
  - Prints backup information to console

## Configuration

### Settings Dictionary

```python
from config import SETTINGS

# Browser settings
num_browsers = SETTINGS['NUM_BROWSERS']
page_timeout = SETTINGS['PAGE_LOAD_TIMEOUT']

# Rate limiting
delay = SETTINGS['PAGE_LOAD_DELAY']
save_interval = SETTINGS['SAVE_INTERVAL']

# Content settings
context_chars = SETTINGS['CONTEXT_CHARS']
max_length = SETTINGS['MAX_CONTENT_LENGTH']

# Backup settings
backup_enabled = SETTINGS['BACKUP_FILES']
compress = SETTINGS['COMPRESS_BACKUPS']
max_backups = SETTINGS['MAX_BACKUPS']
```

### Constants

```python
from config import (
    BASE_URL,
    KEYWORDS,
    MAX_PAGES,
    RESULTS_DIR,
    RESULTS_DIR_ABS
)
```

## Data Structures

### Result Dictionary

Each scraped page produces a result dictionary:

```python
result = {
    'url': str,          # Full URL of the page
    'title': str,        # Page title
    'keywords_found': str,  # Comma-separated keywords
    'keyword_contexts': str,  # JSON string of context objects
    'last_modified': str,    # Last modified date
    'timestamp': str,        # Scrape timestamp
    'page_content': str      # Cleaned page content
}
```

### Context Object

Keyword context is stored as JSON:

```python
context = {
    'keyword': str,      # Found keyword
    'context': str,      # Surrounding text
    'position': int      # Position in content
}
```

## Error Handling

### Retry Mechanism

```python
# Example of retry operation
result = scraper._retry_operation(
    operation,
    *args,
    max_attempts=SETTINGS['RETRY_ATTEMPTS'],
    delay=SETTINGS['RETRY_DELAY']
)
```

### File Operations

```python
try:
    # Try UTF-8 with BOM
    with open(file, 'w', encoding='utf-8-sig') as f:
        # Write operations
except UnicodeEncodeError:
    # Try alternate encodings
    for encoding in ['utf-8', 'cp1252']:
        try:
            with open(file, 'w', encoding=encoding) as f:
                # Write operations
        except UnicodeEncodeError:
            continue
```

## Examples

### Basic Usage

```python
# Initialize and run scraper
scraper = ArmyWebScraper()
scraper.scrape()

# List backups
manager = BackupManager()
manager.list_backups()

# Restore specific backup
manager.restore_backup("army_results_20250331_120000.csv.gz")
```

### Custom Configuration

```python
# Modify settings before running
from config import SETTINGS

SETTINGS.update({
    'NUM_BROWSERS': 2,
    'PAGE_LOAD_DELAY': 5,
    'SAVE_INTERVAL': 60,
    'MAX_BACKUPS': 10
})

scraper = ArmyWebScraper()
scraper.scrape()
```
