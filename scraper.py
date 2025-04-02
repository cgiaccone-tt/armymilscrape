import sys
import os
import random

# Force unbuffered output
if sys.stdout.isatty():
    # Running in interactive terminal
    sys.stdout.reconfigure(encoding='utf-8')
else:
    # Running in non-interactive mode (e.g., redirected to file)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
import os
import json
from datetime import datetime
import re
import chromedriver_autoinstaller
from config import BASE_URL, KEYWORDS, MAX_PAGES, RESULTS_DIR_ABS, SETTINGS, EXCLUDED_PATHS, EXCLUDED_FILE_TYPES
from backup_manager import BackupManager
from urllib.parse import urljoin
from urllib.parse import urlparse

class ArmyWebScraper:
    def __init__(self):
        """Initialize the scraper."""
        print("Initializing Army.mil web scraper...")
        print(f"Python version: {sys.version}")
        print(f"Operating system: {os.name}")
        print(f"Terminal type: {'Interactive' if sys.stdout.isatty() else 'Non-interactive'}")
        print("Setting up Chrome WebDriver...")
        
        self.results = []
        self.visited_urls = set()
        self.start_time = None
        self.last_save_time = None
        self.backup_manager = BackupManager()
        
        # Create results directory if it doesn't exist
        os.makedirs(RESULTS_DIR_ABS, exist_ok=True)

    def _wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present on the page."""
        timeout = timeout or SETTINGS['ELEMENT_TIMEOUT']
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None

    def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff."""
        max_retries = SETTINGS['MAX_RETRIES']
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Clear any stale error dialogs that might be present
                try:
                    alert = self.driver.switch_to.alert
                    alert.dismiss()
                except:
                    pass
                
                # Switch back to default content
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass
                
                # Execute the operation
                result = operation(*args, **kwargs)
                
                # If we get here, the operation was successful
                return result
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                # Check if we need to reinitialize the driver
                if "invalid session id" in str(e).lower():
                    print("Session expired during retry, reinitializing Chrome WebDriver...")
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = self._initialize_driver()
                    # Reset retry count to give the new session a fresh start
                    retry_count = 0
                    continue
                
                # Calculate delay with exponential backoff and jitter
                delay = min(300, (2 ** retry_count) + random.uniform(0, 1))  # Cap at 5 minutes
                if retry_count < max_retries:
                    print(f"Operation failed, retrying in {int(delay)} seconds...")
                    time.sleep(delay)
                
        # If we get here, all retries failed
        print(f"Operation failed after {max_retries} attempts")
        raise last_error

    def save_results(self, is_backup=False):
        """Save results to both CSV and Excel files with proper encoding and formatting."""
        if not self.results:
            print("No results to save.")
            return
            
        # Create results directory if it doesn't exist
        os.makedirs(RESULTS_DIR_ABS, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"army_results_{timestamp}" if is_backup else "army_results"
        
        # Save to CSV
        csv_path = os.path.join(RESULTS_DIR_ABS, f"{base_filename}.csv")
        try:
            with open(csv_path, 'w', newline='', encoding='ascii', errors='replace') as f:
                writer = csv.DictWriter(f, fieldnames=['url', 'title', 'keywords', 'last_modified'])
                writer.writeheader()
                for result in self.results:
                    writer.writerow({
                        'url': result['url'],
                        'title': result['title'],
                        'keywords': ','.join(result['keywords']),
                        'last_modified': result['last_modified']
                    })
            print(f"[OK] CSV file saved successfully: {csv_path}")
        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")
            
        # Save to Excel
        excel_path = os.path.join(RESULTS_DIR_ABS, f"{base_filename}.xlsx")
        try:
            df = pd.DataFrame(self.results)
            df['keywords'] = df['keywords'].apply(lambda x: ','.join(x))
            df.to_excel(excel_path, index=False)
            print(f"[OK] Excel file saved successfully: {excel_path}")
        except Exception as e:
            print(f"Error saving Excel file: {str(e)}")

    def clean_text_for_save(self, text):
        """Clean text for saving to file, replacing problematic characters."""
        if not isinstance(text, str):
            return str(text)
            
        # Replace problematic Unicode characters with ASCII equivalents
        replacements = {
            '\u2713': 'check',  # 
            '\u2714': 'check',  # 
            '\u2715': 'x',      # 
            '\u2716': 'x',      # 
            '\u2717': 'x',      # 
            '\u2718': 'x',      # 
            '\u0101': 'a',      # 
            '\u0113': 'e',      # 
            '\u012B': 'i',      # 
            '\u014D': 'o',      # 
            '\u016B': 'u',      # 
            '\u2019': "'",      # '
            '\u2018': "'",      # '
            '\u201C': '"',      # "
            '\u201D': '"',      # "
            '\u2026': '...',    # …
            '\u2013': '-',      # –
            '\u2014': '--',     # —
            '\u00A0': ' ',      # non-breaking space
            '\r': ' ',
            '\n': ' ',
            '\t': ' '
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Remove any remaining non-ASCII characters
        text = text.encode('ascii', 'replace').decode('ascii')
        return text

    def scrape(self):
        """Main scraping function."""
        self.start_time = time.time()
        self.last_save_time = self.start_time
        self.urls_to_visit = set([BASE_URL])
        self.total_pages = 0
        self.pages_with_keywords = 0
        self.consecutive_errors = 0
        self.last_success_time = time.time()
        
        print("\nStarting Army.mil web scraper...")
        print("Press Ctrl+C to stop and save results")
        print(f"Maximum pages to crawl: {MAX_PAGES or 'Unlimited'}")
        print(f"Keywords: {', '.join(KEYWORDS)}\n")
        
        try:
            # Initialize the web driver
            print("Initializing Chrome WebDriver...")
            self.driver = self._retry_operation(self._initialize_driver)
            
            while self.urls_to_visit:
                # Get next URL to visit
                current_url = self.urls_to_visit.pop()
                if current_url in self.visited_urls:
                    continue
                
                # Visit the URL
                try:
                    self.total_pages += 1
                    print(f"\n[{self.total_pages}/{MAX_PAGES or 'inf'}] Processing: {current_url}")
                    
                    # Check if we need to reinitialize the driver
                    try:
                        # Test if session is still valid
                        self.driver.current_url
                    except Exception as e:
                        if "invalid session id" in str(e).lower():
                            print("Session expired, reinitializing Chrome WebDriver...")
                            try:
                                self.driver.quit()
                            except:
                                pass
                            self.driver = self._retry_operation(self._initialize_driver)
                    
                    # Check if we need to restart Chrome due to too many errors
                    current_time = time.time()
                    if self.consecutive_errors >= 3 or (current_time - self.last_success_time > 300):  # 5 minutes
                        print("Too many errors or no progress, restarting Chrome...")
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = self._retry_operation(self._initialize_driver)
                        self.consecutive_errors = 0
                        self.last_success_time = current_time
                    
                    # Add delay between requests to prevent overloading
                    time.sleep(1)
                    
                    # Visit the page with retry
                    def visit_page():
                        self.driver.get(current_url)
                        # Wait for page load
                        WebDriverWait(self.driver, 10).until(
                            lambda driver: driver.execute_script('return document.readyState') == 'complete'
                        )
                    
                    self._retry_operation(visit_page)
                    self.visited_urls.add(current_url)
                    
                    # Process the page
                    self._process_page()
                    
                    # Reset error counter on success
                    self.consecutive_errors = 0
                    self.last_success_time = time.time()
                    
                except Exception as e:
                    print(f"Error visiting {current_url}: {str(e)}")
                    self.consecutive_errors += 1
                    # If session invalid or too many errors, add URL back to queue
                    if "invalid session id" in str(e).lower() or self.consecutive_errors >= 3:
                        self.urls_to_visit.add(current_url)
                    continue
                
                # Check if we should save progress
                current_time = time.time()
                if current_time - self.last_save_time >= SETTINGS['SAVE_INTERVAL']:
                    elapsed = int(current_time - self.start_time)
                    pages_per_min = (self.total_pages / elapsed) * 60 if elapsed > 0 else 0
                    
                    print("\n=== Progress Update ===")
                    print(f"Pages processed: {self.total_pages}")
                    print(f"Pages with keywords: {self.pages_with_keywords}")
                    print(f"Queue size: {len(self.urls_to_visit)}")
                    print(f"Elapsed time: {elapsed//60}m {elapsed%60}s")
                    print(f"Speed: {pages_per_min:.1f} pages/min")
                    
                    # Save progress
                    self.save_results(is_backup=True)
                    self.last_save_time = current_time
                
                # Check if we've reached the maximum pages
                if MAX_PAGES and self.total_pages >= MAX_PAGES:
                    print(f"\nReached maximum pages limit ({MAX_PAGES})")
                    break
                
        except KeyboardInterrupt:
            print("\nStopping scraper (Ctrl+C pressed)")
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
        finally:
            # Save final results
            print("\nSaving final results...")
            self.save_results()
            
            # Clean up
            try:
                self.driver.quit()
            except:
                pass
            
            # Print summary
            print("\nSummary:")
            print(f"Total pages processed: {self.total_pages}")
            print(f"Relevant pages found: {self.pages_with_keywords}")

    def _initialize_driver(self):
        """Initialize Chrome WebDriver with optimized settings."""
        # Install ChromeDriver if necessary
        chromedriver_autoinstaller.install()
        
        # Set up Chrome options for faster loading and error suppression
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Memory and performance optimizations
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        
        # JavaScript and timeout settings
        chrome_options.add_argument('--disable-javascript')  # Try without JavaScript first
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Additional performance optimizations
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Process model optimizations
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--process-per-tab')
        chrome_options.add_argument('--disable-hang-monitor')
        
        # Cache and disk optimizations
        chrome_options.add_argument('--disk-cache-size=1')
        chrome_options.add_argument('--media-cache-size=1')
        chrome_options.add_argument('--disable-application-cache')
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
        
        # Initialize Chrome WebDriver with error handling and retry
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(10)  # Reduced timeout to fail faster
                driver.set_script_timeout(5)  # Set script timeout
                # Test the session
                driver.get('about:blank')
                return driver
            except Exception as e:
                last_error = e
                retry_count += 1
                print(f"Error initializing Chrome WebDriver (attempt {retry_count}/{max_retries}): {str(e)}")
                try:
                    driver.quit()
                except:
                    pass
                time.sleep(2 ** retry_count)  # Exponential backoff
        
        print(f"Failed to initialize Chrome WebDriver after {max_retries} attempts")
        raise last_error

    def _process_page(self):
        """Process the current page and extract relevant information."""
        try:
            # Wait for dynamic content to load with a shorter timeout
            time.sleep(0.5)  # Brief pause
            
            # Get page content with retry and timeout
            def get_page_content():
                try:
                    # First try without JavaScript
                    content = self.driver.page_source
                    if not content or len(content) < 100:  # If content is too small
                        # Re-enable JavaScript and try again
                        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                        self.driver.execute_script("return document.readyState")
                        content = self.driver.page_source
                    
                    # Basic check for valid content
                    if not content or len(content) < 100:
                        raise Exception("Invalid or empty page content")
                        
                    return {
                        'url': self.driver.current_url,
                        'title': self.driver.title or "No title",
                        'content': content
                    }
                except Exception as e:
                    print(f"Error getting page content: {str(e)}")
                    raise
            
            page_data = self._retry_operation(get_page_content)
            
            # Extract and process links
            soup = BeautifulSoup(page_data['content'], 'html.parser')
            self._extract_links(soup)
            
            # Check for keywords
            found_keywords = self._find_keywords(soup)
            if found_keywords:
                self.pages_with_keywords += 1
                print(f"[+] Found keywords: {', '.join(found_keywords)}")
                
                # Save the result
                result = {
                    'url': page_data['url'],
                    'title': page_data['title'],
                    'keywords': found_keywords,
                    'last_modified': self._get_last_modified_date(soup)
                }
                self.results.append(result)
            
        except Exception as e:
            print(f"Error processing page: {str(e)}")
            raise  # Re-raise to trigger retry mechanism

    def _find_keywords(self, soup):
        """Find keywords in the page content."""
        found_keywords = set()
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = soup.get_text().lower()
        
        for keyword in KEYWORDS:
            if keyword.lower() in text_lower:
                found_keywords.add(keyword)
        
        return found_keywords

    def _get_last_modified_date(self, soup):
        """Get the last modified date from the page."""
        last_modified = None
        
        # Try to get from meta tags
        meta_modified = soup.find('meta', {'property': 'article:modified_time'}) or \
                       soup.find('meta', {'name': 'last-modified'}) or \
                       soup.find('meta', {'name': 'date'}) or \
                       soup.find('meta', {'name': 'lastmod'})
        
        if meta_modified:
            last_modified = meta_modified.get('content')
        
        # Try to get from schema.org metadata
        if not last_modified:
            schema_data = soup.find('script', {'type': 'application/ld+json'})
            if schema_data:
                try:
                    data = json.loads(schema_data.string)
                    last_modified = data.get('dateModified')
                except:
                    pass
        
        # Try to get from HTTP headers using CDP
        if not last_modified:
            try:
                # Get response headers using CDP
                response = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': self.driver.current_url})
                headers = response.get('headers', {})
                last_modified = headers.get('last-modified')
            except:
                pass
        
        # Try to get from HTML elements
        if not last_modified:
            time_element = soup.find('time', {'datetime': True})
            if time_element:
                last_modified = time_element.get('datetime')
        
        # Format the date if found
        if last_modified:
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        parsed_date = datetime.strptime(last_modified[:19], fmt)
                        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        continue
            except:
                pass
        
        return "Not available"

    def _extract_links(self, soup):
        """Extract links from the page."""
        elements = soup.find_all('a', href=True)
        for element in elements:
            try:
                href = element.get('href')
                if href:
                    full_url = urljoin(self.driver.current_url, href)
                    if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                        self.urls_to_visit.add(full_url)
            except:
                continue

    def is_valid_url(self, url):
        """Check if URL is valid and should be processed."""
        if not url:
            return False
            
        # Parse the URL
        parsed = urlparse(url)
        
        # Check domain - strict match for www.army.mil
        if parsed.netloc != 'www.army.mil':
            return False
            
        # Skip excluded paths
        if any(path in parsed.path.lower() for path in EXCLUDED_PATHS):
            return False
            
        # Skip excluded file types
        if any(parsed.path.lower().endswith(ext) for ext in EXCLUDED_FILE_TYPES):
            return False
            
        # Skip utility pages
        excluded_patterns = [
            '/search/', 
            '/login/', 
            '/rss/', 
            '/feeds/',
            '/contact/',
            '/sitemap/',
            '/privacy/',
            '/terms/',
            '/help/',
            '/faq/'
        ]
        return not any(pattern in parsed.path.lower() for pattern in excluded_patterns)

if __name__ == "__main__":
    print("Starting Army.mil web scraper...")
    print("Press Ctrl+C to stop and save results")
    scraper = ArmyWebScraper()
    scraper.scrape()
