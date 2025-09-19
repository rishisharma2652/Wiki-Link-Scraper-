import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Set, List

class WikipediaScraper:
    def __init__(self):
        self.base_url = "https://en.wikipedia.org"
        self.visited_links: Set[str] = set()
        self.all_links: Set[str] = set()
    
    def is_valid_wikipedia_link(self, url: str) -> bool:
        """Check if the URL is a valid Wikipedia link"""
        parsed = urlparse(url)
        # Check if it's a Wikipedia domain and has a path
        if not (parsed.netloc.endswith('wikipedia.org') and parsed.path):
            return False
        
        # Check if it's a proper article (not a special page)
        if any(parsed.path.startswith(prefix) for prefix in ['/wiki/Special:', '/wiki/Help:', '/wiki/File:', '/wiki/Template:']):
            return False
        
        return True
    
    def get_wiki_links(self, url: str, max_links: int = 10) -> List[str]:
        """Scrape Wikipedia page for unique links"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find('div', {'id': 'bodyContent'})
            
            if not content_div:
                return []
            
            links = []
            for link in content_div.find_all('a', href=True):
                href = link['href']
                
                # Filter only wiki article links
                if href.startswith('/wiki/') and ':' not in href.split('/wiki/')[1]:
                    full_url = urljoin(self.base_url, href)
                    
                    # Add if it's a valid Wikipedia link and not visited
                    if (self.is_valid_wikipedia_link(full_url) and 
                        full_url not in self.visited_links and 
                        full_url not in self.all_links):
                        links.append(full_url)
                        
                        # Stop when we have enough links
                        if len(links) >= max_links:
                            break
            
            return links
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []
    
    def scrape_wikipedia(self, start_url: str, n: int):
        """Main scraping function"""
        if not self.is_valid_wikipedia_link(start_url):
            raise ValueError("Invalid Wikipedia link provided")
        
        if not (1 <= n <= 3):
            raise ValueError("n must be between 1 and 3")
        
        print(f"Starting scrape from: {start_url}")
        print(f"Cycles to run: {n}")
        print("-" * 50)
        
        # Start with the initial URL
        current_level_links = {start_url}
        self.all_links.add(start_url)
        
        for cycle in range(n):
            print(f"\nCycle {cycle + 1}:")
            print(f"Processing {len(current_level_links)} links...")
            
            next_level_links = set()
            
            for url in current_level_links:
                if url not in self.visited_links:
                    print(f"  Scraping: {url}")
                    new_links = self.get_wiki_links(url)
                    
                    # Add new links to next level and all links
                    for link in new_links:
                        next_level_links.add(link)
                        self.all_links.add(link)
                    
                    self.visited_links.add(url)
            
            current_level_links = next_level_links
            
            print(f"Found {len(next_level_links)} new links in this cycle")
            print(f"Total unique links collected: {len(self.all_links)}")
        
        return self.all_links

def main():
    scraper = WikipediaScraper()
    
    try:
        # Step 1: Get Wikipedia link
        wiki_link = input("Enter a Wikipedia link: ").strip()
        
        # Step 2: Get integer n between 1-3
        try:
            n = int(input("Enter number of cycles (1-3): ").strip())
            if not 1 <= n <= 3:
                raise ValueError("n must be between 1 and 3")
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        # Steps 3-5: Scrape
        result = scraper.scrape_wikipedia(wiki_link, n)
        
        # Display results
        print("\n" + "="*50)
        print("SCRAPING COMPLETED!")
        print("="*50)
        print(f"Total unique Wikipedia links found: {len(result)}")
        print("\nFirst 20 links:")
        for i, link in enumerate(list(result)[:20], 1):
            print(f"{i:2d}. {link}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()