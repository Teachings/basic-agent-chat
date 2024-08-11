import requests
from bs4 import BeautifulSoup
from tool_decorator import custom_tool

@custom_tool
def search_searxng(query: str) -> str:
    """
    Used to search online for a query using a SearxNG instance and return the first few results with page content summaries.

    This tool is designed to interact with a SearxNG metasearch engine, which aggregates search results from various search engines (e.g., Google, Bing, DuckDuckGo). It sends a search query to the specified SearxNG instance and retrieves the top results in JSON format. The tool then follows these links, fetches the page content, and provides a summary of the first few paragraphs.

    ### Key Features:
    - **Aggregation**: Leverages SearxNG's ability to aggregate results from multiple search engines, ensuring diverse and comprehensive search coverage.
    - **Content Summarization**: Fetches and summarizes the content from the top search results, offering quick insights without the need to visit each link manually.
    - **Customizable Engines**: Allows users to specify which search engines to query within SearxNG, offering flexibility based on the user's preferences or the nature of the query.

    ### Parameters:
    - `query` (str): The search term or query string that you want to look up using the SearxNG instance.

    ### Returns:
    - `str`: A formatted string containing the top search results, including the title, link, and a brief summary of the content of each page.

    ### Usage Scenarios:
    - **Knowledge Retrieval**: Ideal for retrieving information from multiple sources when you need a comprehensive overview on a specific topic.
    - **Content Analysis**: Useful for getting a quick summary of web pages to determine their relevance without needing to read through full articles.
    - **AI Integration**: Can be integrated into AI systems that require real-time access to diverse and up-to-date information from the web, such as virtual assistants, research bots, or automated content curators.
    """
    searxng_url = "http://192.168.1.10:4000/search"  # Replace with your SearxNG instance URL
    params = {
        'q': query,
        'format': 'json',
        'engines': 'google,bing,duckduckgo',  # Specify the engines you want to use
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(searxng_url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()['results']
        
        if not results:
            return "No results found."
        
        result_list = []
        for index, result in enumerate(results[:5], start=1):
            title = result['title']
            link = result['url']
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
        
        # Extract and return the first 300 characters of text content from the page
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs[:3]])  # Get text from the first 3 paragraphs
        return text[:300] + '...' if text else "No summary available."
    
    except requests.RequestException as e:
        return "Could not retrieve content."

# # Example usage
# query = "Python programming"
# search_results = search_searxng(query)
# if search_results:
#     print(search_results)
