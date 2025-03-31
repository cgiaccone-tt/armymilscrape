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

class ArmyWebScraper:
    def __init__(self):
        try:
            # Install ChromeDriver if necessary
            chromedriver_autoinstaller.install()
            
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')  # Use new headless mode
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Initialize Chrome WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)  # 10 second wait timeout
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            sys.exit(1)
            
        self.results = []
        self.visited_urls = set()
        self.running = True
        
        # Set up signal handlers for graceful termination
        signal.signal(signal.SIGINT, self.handle_termination)
        signal.signal(signal.SIGTERM, self.handle_termination)

    def handle_termination(self, signum, frame):
        print("\nReceived termination signal. Saving results and exiting...")
        self.running = False
        self.save_results()
        self.driver.quit()
        sys.exit(0)

    def find_keywords_in_text(self, text):
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in KEYWORDS:
            # For single words, check if they exist as whole words
            if ' ' not in keyword:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append(keyword)
            # For phrases, check if the exact phrase exists
            else:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
        return found_keywords

    def clean_text(self, text):
        # Remove extra whitespace and normalize line endings
        return ' '.join(text.split())

    def is_valid_url(self, url):
        # Parse the URL
        parsed = urlparse(url)
        
        # Check if it's an army.mil URL
        if not parsed.netloc.endswith('army.mil'):
            return False
            
        # Exclude /article/ directory
        if '/article/' in parsed.path:
            return False
            
        # Exclude certain file types
        if parsed.path.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.ppt', '.pptx')):
            return False
            
        # Exclude certain patterns
        excluded_patterns = [
            '/search/',
            '/login/',
            '/media/',
            '/images/',
            '/resources/',
            '/download/',
            '/rss/',
            '/feeds/',
        ]
        return not any(pattern in parsed.path.lower() for pattern in excluded_patterns)

    def wait_for_content(self):
        try:
            # Wait for main content to load
            main_content = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            ) or self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            ) or self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return main_content
        except TimeoutException:
            return None

    def process_page(self, url):
        if url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        try:
            # Load the page with Selenium
            self.driver.get(url)
            
            # Wait for dynamic content to load
            main_content = self.wait_for_content()
            if not main_content:
                return []
            
            # Get the page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract main content
            content = soup.find('main') or soup.find('article') or soup.find('body')
            if not content:
                return []
                
            text_content = content.get_text(strip=True)
            found_keywords = self.find_keywords_in_text(text_content)
            
            if found_keywords:
                title = soup.find('title')
                title_text = title.get_text() if title else "No title"
                
                # Clean and store the full text content
                clean_content = self.clean_text(text_content)
                
                return [{
                    'url': url,
                    'title': title_text,
                    'keywords_found': ','.join(found_keywords),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'page_content': clean_content
                }]
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
        
        return []

    def get_links(self, url):
        links = set()
        try:
            # Load the page with Selenium
            self.driver.get(url)
            
            # Wait for dynamic content to load
            self.wait_for_content()
            
            # Get all links after JavaScript execution
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        full_url = urljoin(url, href)
                        if self.is_valid_url(full_url):
                            links.add(full_url)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error getting links from {url}: {str(e)}")
        return links

    def crawl(self):
        pages_crawled = 0
        urls_to_visit = {BASE_URL}
        last_save = time.time()

        try:
            while urls_to_visit and self.running and (MAX_PAGES is None or pages_crawled < MAX_PAGES):
                current_url = urls_to_visit.pop()
                print(f"Processing: {current_url}")
                
                # Process the current page
                new_results = self.process_page(current_url)
                if new_results:
                    self.results.extend(new_results)
                    print(f"Found keywords on: {current_url}")
                
                # Get new links
                new_links = self.get_links(current_url)
                urls_to_visit.update(new_links - self.visited_urls)
                
                pages_crawled += 1
                print(f"Processed {pages_crawled} pages. Found {len(self.results)} relevant pages.")
                
                # Save results periodically (every 5 minutes)
                if time.time() - last_save >= 300:  # 300 seconds = 5 minutes
                    self.save_results()
                    last_save = time.time()
                
                # Add a small delay to be respectful to the server
                time.sleep(PAGE_LOAD_DELAY)

        finally:
            self.save_results()
            self.driver.quit()

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
