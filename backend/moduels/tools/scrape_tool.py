import requests
from bs4 import BeautifulSoup
from moduels.tools import tool

@tool(name="scrape_url", description="Scrapes the text content from a given URL. Returns truncated text to avoid overflowing the context window.")
def scrape_url(url, max_chars=3000):
    """
    Scrapes the text content from a given URL.
    Returns truncated text to avoid overflowing the context window.
    """
    print(f"[TEST POINT] TOOL EXECUTED: scrape_url | URL: '{url}'")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        
        return text[:max_chars]
    except Exception as e:
        print(f"[ERROR] Scrape failed for {url}: {e}")
        return f"Failed to scrape {url}."
