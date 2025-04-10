 ALL_FUNCTIONS = {
    "tools": [
        {
            "name": "weather_report",
            "description": "Get the current weather for a location.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "location": {"type": "STRING"}
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_stock_data",
            "description": "Fetch stock market data for an exchange.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "exchange": {"type": "STRING"}
                },
                "required": ["exchange"]
            }
        },
        {
            "name": "search_youtube",
            "description": "Search YouTube for a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "news_headlines",
            "description": "Fetch top news headlines."
        },
        {
            "name": "yt_download",
            "description": "Download a YouTube video."
        },
        {
            "name": "personal_chat_ai",
            "description": "Engage in an empathetic conversation, recalling stored personal information. Use this for questions about the user's memories, goals, feelings, or identity, such as 'What is my name?' or 'Tell me a memory.' Ensure responses are contextually relevant.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "first_query": {"type": "STRING"}
                },
                "required": ["first_query"]
            }
        },
        {
            "name": "send_to_ai",
            "description": "Handle creative prompts like jokes or stories.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "prompt": {"type": "STRING"}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "app_runner",
            "description": "Open an app if installed, otherwise open the website version. Example: 'Open Spotify' will try the app first, then the web.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "app_name": {"type": "STRING"}
                },
                "required": ["app_name"]
            }
        },
        {
            "name": "private_mode",
            "description": "Search in incognito or private mode for a specific topic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "topic": {"type": "STRING"}
                },
                "required": ["topic"]
            }
        },
        {
            "name": "make_a_call",
            "description": "Make a phone call to the provided contact name.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"}
                },
                "required": ["name"]
            }
        },
        {
            "name": "send_email",
            "description": "Send an email on Gmail."
        },
        {
            "name": "duckgo_search",
            "description": "Search the provided query on the internet for quick information.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "chat_with_rag",
            "description": "For deeper and insightful discussions on specific topic using (RAG).",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "subject": {"type": "STRING"}
                },
                "required": ["subject"]
            }
        },
        {
            "name": "data_analysis",
            "description": "Perform data analysis on the loaded CSV file using Python with pandas, numpy, and matplotlib based on the user's specific analytical request.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "user_query": {"type": "STRING", "description": "User's query for specific analysis (e.g., 'average', 'sum', 'map')."}
                },
                "required": ["user_query"]
            }
        }
    ]
}

