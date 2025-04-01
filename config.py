import os

# Base URL for the Army website
BASE_URL = "https://www.army.mil"

# Keywords and phrases to search for
KEYWORDS = [
    "diversity",
    "equity",
    "inclusion",
    "equal opportunity",
    "discrimination",
    "harassment",
    "bias",
    "prejudice",
    "minority",
    "minorities",
    "underrepresented",
    "gender",
    "race",
    "ethnicity",
    "cultural",
    "disability",
    "disabilities",
    "accessibility",
    "inclusive",
    "diverse",
    "equitable",
    "fair treatment",
    "equal access",
    "workplace culture",
    "representation",
    "demographic",
    "demographics",
    "affirmative action",
    "equal employment",
    "workplace diversity",
    "cultural competency",
    "unconscious bias",
    "implicit bias",
    "systemic",
    "marginalized",
    "underserved",
    "equality",
    "indigenous",
    "native american",
    "asian american",
    "pacific islander",
    "hispanic",
    "latino",
    "latina",
    "african american",
    "black",
    "lgbtq",
    "lgbtq+",
    "transgender",
    "veteran",
    "veterans",
    "military family",
    "military families",
    "service member",
    "service members",
    "active duty",
    "reserve",
    "national guard",
]

# Maximum number of pages to crawl (set to None for unlimited)
MAX_PAGES = 200

# Excluded paths and file types
EXCLUDED_PATHS = [
    '/article/',
    '/articles/',
    '/media/',
    '/images/',
    '/photos/',
    '/videos/',
    '/audio/',
    '/docs/',
    '/pdf/',
    '/downloads/',
    '/resources/',
    '/files/',
    '/attachments/'
]

EXCLUDED_FILE_TYPES = [
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx',
    '.ppt',
    '.pptx',
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.svg',
    '.mp3',
    '.mp4',
    '.wav',
    '.zip',
    '.rar',
    '.7z',
    '.tar',
    '.gz'
]

# Output directory for results (relative to script location)
RESULTS_DIR = "results"

# Get absolute path to results directory
RESULTS_DIR_ABS = os.path.join(os.path.dirname(os.path.abspath(__file__)), RESULTS_DIR)

# Output file name for results
OUTPUT_FILE = "army_results.csv"

# Scraper settings
SETTINGS = {
    # Browser settings
    'NUM_BROWSERS': 4,  # Number of parallel browser instances
    'PAGE_LOAD_TIMEOUT': 30,  # Seconds to wait for page load
    'ELEMENT_TIMEOUT': 10,  # Seconds to wait for elements
    'RETRY_ATTEMPTS': 3,  # Number of times to retry failed requests
    'RETRY_DELAY': 2,  # Seconds to wait between retries
    
    # Rate limiting
    'PAGE_LOAD_DELAY': 2,  # Seconds to wait between page loads
    'SAVE_INTERVAL': 30,  # Seconds between auto-saves
    'NO_PROGRESS_TIMEOUT': 60,  # Seconds to wait with no progress before taking action
    
    # Content extraction
    'CONTEXT_CHARS': 100,  # Number of characters to capture around keyword matches
    'MAX_CONTENT_LENGTH': 100000,  # Maximum characters to store per page
    
    # File handling
    'BACKUP_FILES': True,  # Whether to keep backup files
    'COMPRESS_BACKUPS': True,  # Whether to compress backup files
    'MAX_BACKUPS': 5,  # Maximum number of backup files to keep
}

# File patterns for cleanup
CLEANUP_PATTERNS = [
    'army_results_*.csv',
    'army_results_*.xlsx',
    'army_results.csv',
    'army_results.xlsx',
    'army_results_clean.csv',
    'army_results_alt.csv',
    'army_results_alt.xlsx',
    '*.bak'
]
