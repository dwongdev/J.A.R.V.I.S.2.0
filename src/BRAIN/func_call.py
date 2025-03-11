from typing import Union 
import json 
import re
from typing import  Union
from langchain_ollama import ChatOllama
from DATA.tools import ALL_FUNCTIONS 

AVAILABLE_FUNCTION_NAMES_STRING = [func.get("name") for func in ALL_FUNCTIONS.get("tools")]

SYSTEM_MESSAGE = f"""You are an AI that determines the best function to call based on user input.

### Available Functions:
{ALL_FUNCTIONS}

### Instructions:
- Choose the function name.
- Extract necessary arguments.
- **Respond ONLY in valid JSON format** as follows:

```json
[
   {{
     "name": "function_name_here",
     "parameters": {{
         "arg1": "value1",
         "arg2": "value2"
     }}
   }}
]
```

### Examples:

User Query: What's the weather in London?  
Expected JSON Output:
```json
[
   {{
     "name": "weather_report",
     "parameters": {{"location": "London"}}
   }}
]
```

User Query: Open YouTube.  
Expected JSON Output:
```json
[
   {{
     "name": "open_youtube",
     "parameters": {{}}
   }}
]
```

User Query: Tell me a joke.  
Expected JSON Output:
```json
[
   {{
     "name": "send_to_ai",
     "parameters": {{"prompt": "Tell me a joke"}}
   }}
]
```

User Query: Let's discuss the ethical implications of AI in detail.  
Expected JSON Output:
```json
[
   {{
     "name": "chat_with_rag",
     "parameters": {{"subject": "AI"}}
   }}
]
```

User Query: Get news headlines and then let's discuss about life.  
Expected JSON Output:
```json
[
   {{
     "name": "news_headlines",
     "parameters": {{}}
   }},
   {{
     "name": "chat_with_rag",
     "parameters": {{"subject": "life"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then search YouTube for NASDAQ analysis.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "search_youtube",
     "parameters": {{"topic": "NASDAQ analysis"}}
   }}
]
```

User Query: Who will win the FIFA World Cup in 2030?  
Expected JSON Output:
```json
[
   {{
     "name": "duckgo_search",
     "parameters": {{"query": "FIFA World Cup winners in 2030?"}}
   }}
]
```

User Query: Get stock data for NASDAQ and then Open Instagram web.  
Expected JSON Output:
```json
[
   {{
     "name": "get_stock_data",
     "parameters": {{"exchange": "NASDAQ"}}
   }},
   {{
     "name": "open_instagram",
     "parameters": {{}}
   }}
]
```

User Query: Discuss the philosophical implications of quantum mechanics.  
Expected JSON Output:
```json
[
   {{
     "name": "chat_with_rag",
     "parameters": {{"subject": "quantum mechanics"}}
   }}
]
```

User Query: Who is the current president of Brazil?  
Expected JSON Output:
```json
[
   {{
     "name": "duckgo_search",
     "parameters": {{"query": "current president of Brazil?"}}
   }}
]
```
"""


def load_tools(file_path: str) -> Union[dict, list]:
    try:
        with open(file_path, "r") as file:
            tools = json.load(file)
            return tools
    except FileNotFoundError:
        print("Error: Tools configuration file not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return []

def load_tools_message(file_path: str) -> str:
    tools = load_tools(file_path)
    return json.dumps(tools, indent=2)


def parse_tool_calls(response: str) -> Union[list, None]:
    try:
        # Regex to extract content inside a list
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        if match:
            list_content = match.group(0)
            return json.loads(list_content)
    except json.JSONDecodeError as e:
        print(f"Error in formatting JSON: \n{e}")
    except Exception as e:
        print(f"Unexpected error: \n{e}")
    return None

def create_function_call(user_query:str , model="granite3.1-dense:2b")-> Union[str, None]:
    messages = [{"role":"system","content":SYSTEM_MESSAGE}, {"role": "user", "content": user_query}]
    # Example conversation
    try:
        llm = ChatOllama(model=model , temprature = 0)
        response = llm.invoke(messages)
        raw_func_response =  response.content
        functional_response = parse_tool_calls(raw_func_response)
        valid_functions = [func for func in functional_response if func.get("name").lower() in AVAILABLE_FUNCTION_NAMES_STRING]
        return valid_functions
    
                
    except Exception as e:
        print(f"Error creating function call: {e}")
    return None 

if __name__ == "__main__":
    query = "plase send email send email "
    response = create_function_call(query)