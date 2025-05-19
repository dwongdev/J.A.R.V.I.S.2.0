# from google import genai
# from google.genai import types
# from DATA.tools import ALL_FUNCTIONS , UI_ALL_FUNCTIONS
# from src.FUNCTION.Tools.get_env import load_variable

# # #from DATA.tools import ALL_FUNCTIONS
# genai_key = load_variable("genai_key")
# UI_ON = load_variable("UI")

# # #genai.configure(api_key=genai_key)
# client = genai.Client(api_key=genai_key)

# def function_call_gem(query:str) -> list:
#     client = genai.Client(api_key=genai_key)
    
#     # conversion to tools so model can understand it better.
#     config = types.GenerateContentConfig(
#         temperature=0,
#         tools = [types.Tool(function_declarations=ALL_FUNCTIONS["tools"] if UI_ON == "NO" else UI_ALL_FUNCTIONS["tools"])],
#         tool_config = types.ToolConfig(function_calling_config=types.FunctionCallingConfig(mode="ANY"))
#     )   
    
#     try:
#     #config = types.GenerateContentConfig(tools=tools , automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))
#         response = client.models.generate_content(
#             model='gemini-2.0-flash',
#             contents=query,
#             config = config
#         )
#         return response.function_calls 
#     except Exception as e:
#         print(f"Error: {e}")
#         return []



# def gem_generate_fuction_calls(user_query:str) -> dict:
#     response_list = []
#     function_call_response = function_call_gem(user_query)
#     if function_call_response:
#         for fn in function_call_response:
#             temp = {
#                 "name":fn.name,
#                 "parameters":fn.args
#             }
#             response_list.append(temp)
            
#     return response_list

#...
from google import genai
from google.genai import types
from DATA.tools import ALL_FUNCTIONS, UI_ALL_FUNCTIONS
from src.FUNCTION.Tools.get_env import EnvManager


class GeminiFunctionCaller:
    def __init__(self):
        self.genai_key = EnvManager.load_variable("genai_key")
        self.UI_ON = EnvManager.load_variable("UI")
        self.client = genai.Client(api_key=self.genai_key)
        self.tools_config = self._get_tools_config()

    def _get_tools_config(self) -> types.GenerateContentConfig:
        tools = UI_ALL_FUNCTIONS["tools"] if self.UI_ON == "YES" else ALL_FUNCTIONS["tools"]
        return types.GenerateContentConfig(
            temperature=0,
            tools=[types.Tool(function_declarations=tools)],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            )
        )

    def _call_gemini(self, query: str):
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=query,
                config=self.tools_config
            )
            return response.function_calls
        except Exception as e:
            print(f"[Gemini Error] {e}")
            return []

    def generate_function_calls(self, user_query: str) -> list[dict]:
        results = []
        function_calls = self._call_gemini(user_query)

        for fn in function_calls:
            results.append({
                "name": fn.name,
                "parameters": fn.args
            })

        return results
