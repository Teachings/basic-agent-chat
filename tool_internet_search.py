import requests
from bs4 import BeautifulSoup
from tool_decorator import custom_tool

@custom_tool
def search_duckduckgo(query: str) -> str:
    """Search for a query on online search engine DuckDuckGo and return the first few results with page content summaries."""
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all the result titles, excluding ads
        results = soup.find_all('a', class_='result__a', limit=5)
        filtered_results = [
            (result.get_text(), result['href']) for result in results 
            if not 'ad_domain' in result['href']
        ]
        
        if not filtered_results:
            return "No results found."
        
        result_list = []
        for index, (title, link) in enumerate(filtered_results, start=1):
            # Fetch content of the page
            page_summary = fetch_page_summary(link, headers)
            result_list.append(f"{index}. {title}\nLink: {link}\nSummary: {page_summary}\n")
        
        return "\n".join(result_list)
    
    except requests.RequestException as e:
        return f"An error occurred while performing the search: {e}"

def fetch_page_summary(url: str, headers: dict) -> str:
    """Fetch the content summary of a given URL."""
    try:
        response = requests.get(url, headers=headers, timeout=10)  # 10-second timeout
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract and return the first 200 characters of text content from the page
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs[:3]])  # Get text from the first 3 paragraphs
        return text[:300] + '...' if text else "No summary available."
    
    except requests.RequestException as e:
        return "Could not retrieve content."

# Example usage
# query = "Python programming"
# search_results = search_duckduckgo(query)
# if search_results:
#     print(search_results)
