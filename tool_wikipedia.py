import wikipediaapi
from tool_decorator import custom_tool

@custom_tool
def lookup_wikipedia(query: str) -> str:
    """Look up information on Wikipedia.
    
    Args:
        query (str): The search term to look up on Wikipedia.
        
    Returns:
        str: A summary of the information found on Wikipedia.
    """
    # Set the custom user agent
    user_agent = 'WeatherChatAgent/1.0 (mukul@example.com)'
    
    # Initialize the Wikipedia API with custom User-Agent
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent=user_agent
    )
    
    # Look up the page
    page = wiki_wiki.page(query)

    if not page.exists():
        return f"No Wikipedia page found for '{query}'."

    # Get a summary of the page content
    summary = page.summary[:500]  # Limit the summary length
    return f"Wikipedia summary for '{query}':\n\n{summary}"

# Example usage
# query = 'Artificial Intelligence'
# summary_info = lookup_wikipedia(query)
# if summary_info:
#     print(summary_info)
