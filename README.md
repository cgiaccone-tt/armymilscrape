# Army.mil Web Scraper

A robust Python web scraper designed to crawl www.army.mil and search for specified keywords and phrases. Features automatic file saving, backup management, and comprehensive error handling.

## Features

- **Smart Crawling**
  - Configurable page limit (currently set to 1000 pages)
  - Intelligent URL filtering
  - Automatic retry on failures
  - Progress tracking and auto-saving

- **Data Collection**
  - Keyword matching with context
  - Last modified date extraction
  - Clean text processing
  - Structured data output

- **File Management**
  - Organized results directory
  - Timestamped file names
  - Multiple file formats (CSV, Excel)
  - Automatic backups
  - Compressed backup storage

- **Error Handling**
  - Multiple encoding attempts
  - Retry mechanism with exponential backoff
  - Detailed error reporting
  - Auto-recovery options

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome browser installed (latest version recommended)

3. Configure settings in `config.py`:
   - Adjust `MAX_PAGES` (currently 1000)
   - Modify `KEYWORDS` list
   - Customize scraper settings if needed

4. Run the scraper:
```bash
python scraper.py
```

## Configuration

The `config.py` file contains all configurable settings:

```python
# Scraper settings
SETTINGS = {
    # Browser settings
    'NUM_BROWSERS': 4,          # Number of parallel browser instances
    'PAGE_LOAD_TIMEOUT': 30,    # Seconds to wait for page load
    'ELEMENT_TIMEOUT': 10,      # Seconds to wait for elements
    'RETRY_ATTEMPTS': 3,        # Number of times to retry failed requests
    'RETRY_DELAY': 2,          # Seconds to wait between retries
    
    # Rate limiting
    'PAGE_LOAD_DELAY': 2,      # Seconds to wait between page loads
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
├── config.py           # Configuration settings
├── scraper.py         # Main scraper implementation
├── backup_manager.py  # Backup system implementation
├── cleanup.py         # Cleanup utility
├── test_save.py       # Testing utility
├── requirements.txt   # Python dependencies
├── results/           # Output directory
│   ├── army_results_*.csv   # CSV output files
│   ├── army_results_*.xlsx  # Excel output files
│   └── backups/            # Compressed backups
└── README.md          # This documentation
```

## Output Files

The scraper generates two types of output files:

1. **CSV Files** (`army_results_[timestamp].csv`)
   - UTF-8 encoded with BOM
   - Full text content
   - Keyword contexts
   - URLs and timestamps

2. **Excel Files** (`army_results_[timestamp].xlsx`)
   - Optimized column widths
   - Same content as CSV
   - Better formatting

## Utilities

### Backup Manager

```bash
# The backup system is automatic, but you can:
python -c "from backup_manager import BackupManager; BackupManager().list_backups()"
```

### Cleanup Utility

```bash
python cleanup.py
```
Provides options to:
1. Remove individual files
2. Remove entire results directory
3. Cancel operation

### Test Utility

```bash
python test_save.py
```
Tests:
- File saving
- Backup creation
- File restoration
- Directory permissions

## Error Handling

The scraper includes robust error handling:
- Automatic retry for failed requests
- Multiple encoding attempts for file saving
- Backup creation before risky operations
- Detailed error logging

## Best Practices

1. **Regular Backups**: The system automatically creates backups, but consider copying important results elsewhere
2. **Monitor Progress**: Check the console output for progress updates
3. **Resource Usage**: Adjust `MAX_PAGES` and timeouts if needed
4. **Clean Up**: Use `cleanup.py` to manage disk space

## Troubleshooting

1. **ChromeDriver Issues**
   - The script automatically installs ChromeDriver
   - Ensure Chrome browser is up to date

2. **Encoding Problems**
   - The script attempts multiple encodings
   - Check the console for encoding-related messages

3. **Performance Issues**
   - Adjust `PAGE_LOAD_DELAY` and timeouts
   - Reduce `MAX_PAGES` if needed

4. **File Access Issues**
   - Ensure write permissions in the results directory
   - Close any open result files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is proprietary and confidential. All rights reserved.
