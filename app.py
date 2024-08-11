from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List
import requests
import json
import uuid

app = FastAPI()

# In-memory storage for session-based conversation history
session_store: Dict[str, List[Dict]] = {}

# Define the UserInput model
class UserInput(BaseModel):
    session_id: str
    message: str

# WebSocket manager to handle connections and messages
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_personal_message(self, message: str, session_id: str):
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager()

# Replace with your actual functions and imports
from tool_weather import get_weather
from tool_wikipedia import lookup_wikipedia
from tool_internet_search import search_duckduckgo
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
    try:
        message_data = llm_response.get('choices', [{}])[0].get('message', {})
        role = message_data.get('role', 'assistant')
        content = message_data.get('content', '')
        tool_calls = message_data.get('tool_calls', [])
        return AIMessage(content=content, tool_calls=tool_calls)
    except Exception as e:
        print(f"Error extracting LLM response: {e}")
        return AIMessage(content="There was an error processing the response.")

def add_tool_results(tool_calls):
    tool_messages = []
    for call in tool_calls:
        function_name = call['function']['name']
        tool_function = tool_functions.get(function_name)

        if tool_function:
            arguments_str = call['function']['arguments']
            if isinstance(arguments_str, str):
                arguments = json.loads(arguments_str)
            else:
                arguments = arguments_str

            required_args = []
            if function_name == "get_weather":
                required_args = ["location"]
            elif function_name == "lookup_wikipedia":
                required_args = ["query"]
            elif function_name == "search_duckduckgo":
                required_args = ["query"]

            missing_args = [arg for arg in required_args if arg not in arguments or not arguments[arg]]
            if missing_args:
                result = f"Error: The tool call for '{function_name}' did not include the required arguments: {', '.join(missing_args)}."
                print(result)
            else:
                result = tool_function(**arguments)
                print(f"Result from {function_name}: {result}")

            tool_message = ToolMessage(content=result, tool_call_id=call["id"])
            tool_messages.append(tool_message.to_dict())
        else:
            print(f"No tool function found for {function_name}")
    return tool_messages

async def send_request(messages, session_id: str):
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "keep_alive": "-1"
    }

    await manager.send_personal_message("Sending request to AI model...", session_id)
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        await manager.send_personal_message(f"Error: {response.status_code}, {response.text}", session_id)
        return None

@app.post("/chat/")
async def chat(input: UserInput):
    session_id = input.session_id
    user_input = input.message
    
    if session_id not in session_store:
        session_store[session_id] = [SystemMessage(SYSTEM_MESSAGE_CONTENT).to_dict()]
    
    messages = session_store[session_id]
    messages.append(UserMessage(user_input).to_dict())
    
    await manager.send_personal_message("Processing your message...", session_id)
    response_data = await send_request(messages, session_id)
    
    if response_data:
        ai_message = extract_llm_response(response_data)
        messages.append(ai_message.to_dict())
        
        tool_calls = ai_message.tool_calls
        if tool_calls:
            await manager.send_personal_message("Processing tool calls...", session_id)
            tool_messages = add_tool_results(tool_calls)
            messages.extend(tool_messages)
            final_response_data = await send_request(messages, session_id)
            if final_response_data:
                final_message = extract_llm_response(final_response_data)
                messages.append(final_message.to_dict())
                session_store[session_id] = messages  # Update session with new messages
                await manager.send_personal_message(final_message.content, session_id)
                return {"response": final_message.content}
            else:
                return {"response": "Error during final processing."}
        else:
            session_store[session_id] = messages  # Update session with new messages
            await manager.send_personal_message(ai_message.content, session_id)
            return {"response": ai_message.content}
    else:
        return {"response": "Error processing the request."}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep the connection alive, we don't need to receive messages from the client
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/session/")
async def get_session_id():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@app.get("/")
async def get_chat_page():
    with open("index.html") as file:
        return HTMLResponse(content=file.read(), status_code=200)
