import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin, urlparse
from config import *
import signal
import sys
import re
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading

class ArmyWebScraper:
    def __init__(self):
        try:
            # Install ChromeDriver if necessary
            chromedriver_autoinstaller.install()
            
            # Set up Chrome options for faster loading
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Performance optimizations
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
            
            # Initialize multiple Chrome WebDrivers for parallel processing
            self.num_workers = 4  # Number of parallel browsers
            self.drivers = []
            self.waits = []
            for _ in range(self.num_workers):
                driver = webdriver.Chrome(options=chrome_options)
                self.drivers.append(driver)
                self.waits.append(WebDriverWait(driver, 5))  # Reduced timeout to 5 seconds
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            sys.exit(1)
            
        self.results = []
        self.visited_urls = set()
        self.running = True
        self.url_queue = Queue()
        self.results_lock = threading.Lock()
        self.visited_lock = threading.Lock()
        
        # Set up signal handlers for graceful termination
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

    def handle_termination(self, signum, frame):
        print("\nReceived termination signal. Saving results and exiting...")
        self.running = False
        self.save_results()
        for driver in self.drivers:
            driver.quit()
        sys.exit(0)

    def find_keywords_in_text(self, text):
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in KEYWORDS:
            if ' ' not in keyword:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append(keyword)
            else:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
        return found_keywords

    def clean_text(self, text):
        return ' '.join(text.split())

    def is_valid_url(self, url):
        parsed = urlparse(url)
        if not parsed.netloc.endswith('army.mil'):
            return False
        if '/article/' in parsed.path:
            return False
        if parsed.path.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.ppt', '.pptx')):
            return False
        excluded_patterns = ['/search/', '/login/', '/media/', '/images/', '/resources/', '/download/', '/rss/', '/feeds/']
        return not any(pattern in parsed.path.lower() for pattern in excluded_patterns)

    def wait_for_content(self, driver, wait):
        try:
            # Wait for either main content elements with reduced timeout
            content = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main, article, body"))
            )
            return content
        except TimeoutException:
            return None

    def process_page(self, url, driver_idx=0):
        with self.visited_lock:
            if url in self.visited_urls:
                return []
            self.visited_urls.add(url)
        
        try:
            driver = self.drivers[driver_idx]
            wait = self.waits[driver_idx]
            
            # Load the page with performance optimization
            driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
            driver.get(url)
            
            # Wait for content with reduced timeout
            main_content = self.wait_for_content(driver, wait)
            if not main_content:
                return []
            
            # Get the page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract content
            content = soup.find('main') or soup.find('article') or soup.find('body')
            if not content:
                return []
                
            text_content = content.get_text(strip=True)
            found_keywords = self.find_keywords_in_text(text_content)
            
            if found_keywords:
                title = soup.find('title')
                title_text = title.get_text() if title else "No title"
                clean_content = self.clean_text(text_content)
                
                with self.results_lock:
                    self.results.append({
                        'url': url,
                        'title': title_text,
                        'keywords_found': ','.join(found_keywords),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'page_content': clean_content
                    })
                    print(f"Found keywords on: {url}")
            
            # Get new links
            elements = driver.find_elements(By.TAG_NAME, "a")
            new_links = set()
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        full_url = urljoin(url, href)
                        if self.is_valid_url(full_url):
                            new_links.add(full_url)
                except:
                    continue
            
            return list(new_links)
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
        return []

    def worker(self, worker_id):
        while self.running:
            try:
                url = self.url_queue.get(timeout=1)
                new_links = self.process_page(url, worker_id)
                
                # Add new links to queue
                for link in new_links:
                    with self.visited_lock:
                        if link not in self.visited_urls:
                            self.url_queue.put(link)
                
                self.url_queue.task_done()
                
            except Exception:
                continue

    def crawl(self):
        # Initialize with base URL
        self.url_queue.put(BASE_URL)
        
        # Create worker threads
        workers = []
        for i in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            t.start()
            workers.append(t)
        
        last_save = time.time()
        last_count = 0
        
        try:
            while self.running:
                # Check progress
                current_count = len(self.visited_urls)
                if current_count != last_count:
                    print(f"Processed {current_count} pages. Found {len(self.results)} relevant pages.")
                    last_count = current_count
                
                # Save results periodically
                if time.time() - last_save >= 300:
                    self.save_results()
                    last_save = time.time()
                
                # Check if we've hit the page limit
                if MAX_PAGES and current_count >= MAX_PAGES:
                    print(f"Reached maximum page limit of {MAX_PAGES}")
                    break
                
                # Small delay to prevent CPU overuse
                time.sleep(0.1)
                
                # Check if we're done
                if self.url_queue.empty() and all(not t.is_alive() for t in workers):
                    break
                
        finally:
            self.running = False
            for t in workers:
                t.join(timeout=1)
            self.save_results()
            for driver in self.drivers:
                driver.quit()

    def save_results(self):
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Results saved to {OUTPUT_FILE}")
        else:
            print("No results found")

if __name__ == "__main__":
    print("Starting Army.mil web scraper...")
    print("Press Ctrl+C to stop and save results")
    scraper = ArmyWebScraper()
    scraper.crawl()
