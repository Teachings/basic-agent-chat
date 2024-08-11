# main.py

import requests
import json
from tool_weather import get_weather
from tool_wikipedia import lookup_wikipedia
from tool_internet_search import search_duckduckgo
from termcolor import colored
from messages import AIMessage, UserMessage, ToolMessage, SystemMessage  # Import the message classes

# Define the OpenAI endpoint and API key
api_url = "http://ai.mtcl.lan:11436/v1/chat/completions"
api_key = "no_api_key_required"

# Define the model being used
model = "llama3.1:70b" #llama3.1:70b #llama3.1:8b-instruct-q8_0

# Make the request to the OpenAI API
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Collect tool definitions from decorated functions
tools = [get_weather.tool_definition,
         lookup_wikipedia.tool_definition,
         search_duckduckgo.tool_definition]

# Define a dictionary of tool functions
tool_functions = {
    "get_weather": get_weather,
    "lookup_wikipedia": lookup_wikipedia,
    "search_duckduckgo": search_duckduckgo
}

SYSTEM_MESSAGE_CONTENT = """
You are a highly capable AI assistant with the ability to handle a wide variety of topics and tasks.
Your primary responsibility is to assist users with general knowledge, reasoning, and conversational abilities.
You have access to the following tools, and you may use multiple tools to achieve the same purpose when necessary:

1. **Weather Tool**: Use this tool only when the user's query explicitly requests weather information, such as current conditions, forecasts, or climate data for a specific location. Ensure that the location is specified correctly when using this tool.

2. **Wikipedia Tool**: This tool allows you to look up general information on Wikipedia. Use this tool when the user asks for specific factual information that is likely to be found in an encyclopedia, such as historical events, biographies, definitions, or scientific facts. Format the query accurately to retrieve the most relevant information.

3. **DuckDuckGo Search Tool**: This tool enables you to perform a web search using DuckDuckGo. Use this tool when the user requests information that is more current, trending, or might not be found in a static encyclopedia, such as news, recent events, or niche queries. Ensure that the search query is specific and relevant to yield accurate results.

When using multiple tools for the same purpose, you should:
- Ensure that each query is formatted correctly and tailored to the specific tool being used.
- Combine the results from different tools to provide a comprehensive and accurate response.
- Clearly indicate to the user that multiple tools were used and summarize the combined findings.

For any other type of query, rely entirely on your own knowledge and conversational skills without invoking any tools.
Your goal is to provide helpful, relevant, and direct responses based on the user's input. Use the tools only when absolutely necessary to fulfill the user's request and when it directly enhances your ability to provide an accurate answer.
Avoid unnecessary tool usage to maintain an efficient and natural conversation.
"""

def extract_llm_response(llm_response):
    """
    Extracts the role, content, and tool_calls from the LLM response and returns an AIMessage object.
    
    Parameters:
        llm_response (dict): The LLM response in JSON format (as a Python dictionary).
        
    Returns:
        AIMessage: An instance of AIMessage with role, content, and tool_calls populated.
    """
    try:
        message_data = llm_response.get('choices', [{}])[0].get('message', {})
        role = message_data.get('role', 'assistant')
        content = message_data.get('content', '')
        tool_calls = message_data.get('tool_calls', [])

        # Ensure that we handle cases where there is only content
        return AIMessage(content=content, tool_calls=tool_calls)
    except Exception as e:
        print(f"Error extracting LLM response: {e}")
        return AIMessage(content="There was an error processing the response.")

def add_tool_results(tool_calls):
    """
    Processes and adds tool call results to the messages list.
    Handles different tools with their respective required arguments.
    """
    tool_messages = []
    for call in tool_calls:
        function_name = call['function']['name']
        tool_function = tool_functions.get(function_name)

        if tool_function:
            arguments_str = call['function']['arguments']
            # Ensure arguments are parsed into a dictionary if they are still in string form
            if isinstance(arguments_str, str):
                arguments = json.loads(arguments_str)
            else:
                arguments = arguments_str

            # Generalized argument validation based on the tool being called
            required_args = []  # List to store the required arguments for this tool
            if function_name == "get_weather":
                required_args = ["location"]
            elif function_name == "lookup_wikipedia":
                required_args = ["query"]
            elif function_name == "search_duckduckgo":
                required_args = ["query"]

            # Check if the necessary arguments are present
            missing_args = [arg for arg in required_args if arg not in arguments or not arguments[arg]]
            if missing_args:
                result = f"Error: The tool call for '{function_name}' did not include the required arguments: {', '.join(missing_args)}."
                print(colored(result, "red"))
            else:
                result = tool_function(**arguments)
                print(colored(f"Result from {function_name}: {result}", "magenta"))

            # Add tool response directly to messages
            tool_message = ToolMessage(content=result, tool_call_id=call["id"])
            tool_messages.append(tool_message.to_dict())
        else:
            print(colored(f"No tool function found for {function_name}", "red"))
    return tool_messages



def send_request(messages):
    """
    Sends a request to the OpenAI API with the current messages and returns the response.
    """
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "keep_alive": "-1"
    }

    print(colored("Request Payload:", "cyan"))
    print(colored(json.dumps(payload, indent=2), "yellow"))

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        print(colored(f"Error: {response.status_code}, {response.text}", "red"))
        return None

def get_user_input():
    """
    Prompt the user for input and return it.
    """
    return input(colored("User: ", "cyan"))

def process_conversation():
    """
    Process an entire conversation including tool calls.
    Automatically handles message addition and tool call processing.
    """
    messages = []
    
    # Add the system message only once
    messages.append(SystemMessage(SYSTEM_MESSAGE_CONTENT).to_dict())

    # Start the conversation loop
    while True:
        # Get user input
        user_input = get_user_input()
        if user_input.lower() in ["exit", "quit"]:
            print(colored("Exiting conversation.", "red"))
            break
        
        messages.append(UserMessage(user_input).to_dict())
        
        # Send request to get the assistant's response
        response_data = send_request(messages)

        if response_data:
            # Debugging: Print the response data for inspection
            print(colored("AI Response Data:", "cyan"))
            print(json.dumps(response_data, indent=2))

            # Extract the LLM response and convert it to an AIMessage
            ai_message = extract_llm_response(response_data)
            
            # Debugging: Print the extracted AIMessage
            print(colored("Extracted AIMessage:", "cyan"))
            print(ai_message.to_dict())
            
            messages.append(ai_message.to_dict())
            
            tool_calls = ai_message.tool_calls
            
            # Process tool calls if they exist
            if tool_calls:
                tool_messages = add_tool_results(tool_calls)
                messages.extend(tool_messages)
                
                # Send request with the updated messages after tool call
                final_response_data = send_request(messages)
                
                if final_response_data:
                    final_message = extract_llm_response(final_response_data)
                    messages.append(final_message.to_dict())
                    print(colored("Final Assistant Response:", "green"))
                    print(colored(final_message.content, "green"))
                else:
                    break
            else:
                print(colored("Assistant Response without tool call:", "green"))
                print(colored(ai_message.content, "green"))
        else:
            break

        # Loop continues with the next user input

# Start the conversation processing loop
process_conversation()
