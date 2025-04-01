import sys
import os

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
        for attempt in range(SETTINGS['RETRY_ATTEMPTS']):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == SETTINGS['RETRY_ATTEMPTS'] - 1:
                    raise
                wait_time = SETTINGS['RETRY_DELAY'] * (2 ** attempt)
                print(f"Operation failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    def save_results(self, is_backup=False):
        """Save results to both CSV and Excel files with proper encoding and formatting."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(RESULTS_DIR_ABS, f'army_results_{timestamp}.csv')
        excel_file = os.path.join(RESULTS_DIR_ABS, f'army_results_{timestamp}.xlsx')
        
        # Deduplicate results based on URL
        seen_urls = set()
        cleaned_results = []
        for result in self.results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                cleaned_result = {
                    'url': self.clean_text_for_save(result['url']),
                    'title': self.clean_text_for_save(result['title']),
                    'keywords_found': self.clean_text_for_save(result['keywords_found']),
                    'keyword_contexts': self.clean_text_for_save(result['keyword_contexts']),
                    'last_modified': self.clean_text_for_save(result.get('last_modified', 'Not available')),
                    'timestamp': self.clean_text_for_save(result['timestamp']),
                    'page_content': self.clean_text_for_save(result['page_content'])
                }
                cleaned_results.append(cleaned_result)
        
        if len(cleaned_results) != len(self.results):
            print(f"Removed {len(self.results) - len(cleaned_results)} duplicate URLs from results")
            self.results = cleaned_results

        if not self.results:
            print("No results to save.")
            return

        if not is_backup:
            print(f"\nSaving results to:")
            print(f"- CSV: {csv_file}")
            print(f"- Excel: {excel_file}")

        # Save to CSV
        try:
            with open(csv_file, 'w', newline='', encoding='ascii') as f:
                writer = csv.DictWriter(f, fieldnames=['url', 'title', 'keywords_found', 'keyword_contexts', 'last_modified', 'timestamp', 'page_content'])
                writer.writeheader()
                writer.writerows(cleaned_results)
            if not is_backup:
                print("[OK] CSV file saved successfully")
        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")

        # Save to Excel
        try:
            df = pd.DataFrame(cleaned_results)
            df.to_excel(excel_file, index=False, engine='openpyxl')
            if not is_backup:
                print("[OK] Excel file saved successfully")
        except Exception as e:
            print(f"Error saving Excel file: {str(e)}")
        
        self.last_save_time = time.time()
        
        if not is_backup:
            print(f"\nSummary:")
            print(f"Total pages processed: {len(self.visited_urls)}")
            print(f"Relevant pages found: {len(self.results)}")

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
                    self._retry_operation(self.driver.get, current_url)
                    self.visited_urls.add(current_url)
                except Exception as e:
                    print(f"Error visiting {current_url}: {str(e)}")
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
                    print(f"Memory usage: {len(self.results)} results")
                    print("=== Auto-saving... ===")
                    
                    self.save_results(is_backup=True)
                    self.last_save_time = current_time
                
                # Check if we've hit the page limit
                if MAX_PAGES and len(self.visited_urls) >= MAX_PAGES:
                    print(f"\nReached maximum page limit ({MAX_PAGES})")
                    break
                
                # Process current page and extract new URLs
                self._process_page()
                
                # Check for no progress timeout
                if current_time - self.last_save_time >= SETTINGS['NO_PROGRESS_TIMEOUT']:
                    print("\nNo new results found for a while, saving and exiting...")
                    break
                
                # Wait between page loads
                time.sleep(SETTINGS['PAGE_LOAD_DELAY'])
                
        except KeyboardInterrupt:
            print("\nScraping interrupted by user. Saving results...")
        except Exception as e:
            print(f"\nError during scraping: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Print final statistics
            elapsed = int(time.time() - self.start_time)
            pages_per_min = (self.total_pages / elapsed) * 60 if elapsed > 0 else 0
            
            print("\n=== Final Statistics ===")
            print(f"Total pages processed: {self.total_pages}")
            print(f"Pages with keywords: {self.pages_with_keywords}")
            print(f"Total time: {elapsed//60}m {elapsed%60}s")
            print(f"Average speed: {pages_per_min:.1f} pages/min")
            print(f"Total results: {len(self.results)}")
            print("=====================")
            
            # Save final results
            self.save_results()
            
            # Clean up
            if hasattr(self, 'driver'):
                self.driver.quit()

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
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Additional performance optimizations for WSL/bash
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-smooth-scrolling')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--memory-pressure-off')
        
        # Process model optimizations
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--process-per-tab')
        chrome_options.add_argument('--disable-hang-monitor')
        
        # Cache and disk optimizations
        chrome_options.add_argument('--disk-cache-size=1')
        chrome_options.add_argument('--media-cache-size=1')
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument('--disable-offline-load-stale-cache')
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
        
        # Initialize Chrome WebDriver with error handling
        try:
            driver = webdriver.Chrome(options=chrome_options)
            # Set page load timeout
            driver.set_page_load_timeout(SETTINGS['PAGE_LOAD_TIMEOUT'])
            return driver
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            raise

    def _process_page(self):
        try:
            # Get the page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract new URLs before processing content
            new_urls = len(self.urls_to_visit)
            self.extract_and_queue_urls(soup, self.driver.current_url)
            added_urls = len(self.urls_to_visit) - new_urls
            if added_urls > 0:
                print(f"Found {added_urls} new URLs to crawl")
            
            # Get last modified date
            last_modified = self.get_last_modified_date(soup)
            
            # Extract content
            content = soup.find('main') or soup.find('article') or soup.find('body')
            if content:
                text_content = content.get_text(strip=True)
                found_keywords, keyword_contexts = self.find_keywords_in_text(text_content)
                
                if found_keywords:
                    self.pages_with_keywords += 1
                    title = soup.find('title')
                    title_text = title.get_text() if title else "No title"
                    clean_content = self.clean_text(text_content)
                    
                    self.results.append({
                        'url': self.driver.current_url,
                        'title': title_text,
                        'keywords_found': ','.join(found_keywords),
                        'keyword_contexts': json.dumps(keyword_contexts),
                        'last_modified': last_modified,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'page_content': clean_content
                    })
                    print(f"[+] Found keywords: {', '.join(found_keywords)}")
                    self.last_save_time = time.time()  # Reset timeout on finding keywords
        except Exception as e:
            print(f"Error processing page {self.driver.current_url}: {str(e)}")

    def find_keywords_in_text(self, text, context_chars=100):
        """Find keywords in text and capture surrounding context."""
        found_keywords = set()
        keyword_contexts = []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        for keyword in KEYWORDS:
            if keyword.lower() in text_lower:
                found_keywords.add(keyword)
                
                # Find all occurrences of the keyword
                start_pos = 0
                while True:
                    pos = text_lower.find(keyword.lower(), start_pos)
                    if pos == -1:
                        break
                        
                    # Get context around keyword
                    context_start = max(0, pos - context_chars)
                    context_end = min(len(text), pos + len(keyword) + context_chars)
                    context = text[context_start:context_end]
                    
                    # Add ellipsis if context is truncated
                    if context_start > 0:
                        context = "..." + context
                    if context_end < len(text):
                        context = context + "..."
                    
                    keyword_contexts.append({
                        'keyword': keyword,
                        'context': context.strip()
                    })
                    
                    start_pos = pos + 1
        
        return found_keywords, keyword_contexts

    def clean_text(self, text):
        return ' '.join(text.split())

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

    def get_last_modified_date(self, soup):
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

    def extract_and_queue_urls(self, soup, base_url):
        elements = soup.find_all('a', href=True)
        for element in elements:
            try:
                href = element.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                        self.urls_to_visit.add(full_url)
            except:
                continue

    def clean_text_for_csv(self, text):
        if pd.isna(text):
            return ""
        # Remove problematic characters and normalize newlines
        text = str(text).replace('\r\n', ' ').replace('\n', ' ')
        # Remove any double quotes that might interfere with CSV formatting
        text = text.replace('"', "'")
        # Remove null bytes and other problematic characters
        text = ''.join(char for char in text if ord(char) >= 32)
        return text.strip()

if __name__ == "__main__":
    print("Starting Army.mil web scraper...")
    print("Press Ctrl+C to stop and save results")
    scraper = ArmyWebScraper()
    scraper.scrape()
