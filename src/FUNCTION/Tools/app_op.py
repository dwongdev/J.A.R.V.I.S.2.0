# from src.FUNCTION.Tools.get_env import load_app, check_os
# from os import system 

# def start_app(path:str) -> bool:
#     os_name = check_os()
#     if os_name == "Linux":
#         system(f'"{path}"')
#     elif os_name == "Darwin":
#         system(f'open "{path}"')
#     elif os_name == "Windows":
#         system(f'start "{path}"')
#     else:
#         print("Invalid Operating sytem..")
#         return False
#     return True 
        
# # app and web operations     
# def app_runner(name:str) -> bool:
#     """Open the specified application by name. For example, you can say 'open WhatsApp' or 'run Chrome'."""
#     path = load_app(name)
#     flag = start_app(path)
#     if flag:
#         return f"{name} is running now."
#     return f"oops  some error occured in opening {name}"


#.....



from src.FUNCTION.Tools.get_env import AppManager , EnvManager #load_app, check_os
from os import system

class AppRunner:
    def __init__(self, name: str):
        self.name = name
        self.os_name = EnvManager.check_os()
        self.path = AppManager().load_app(name)

    def start_app(self) -> bool:
        """Start the app based on the operating system."""
        if self.os_name == "Linux":
            system(f'"{self.path}"')
        elif self.os_name == "Darwin":
            system(f'open "{self.path}"')
        elif self.os_name == "Windows":
            system(f'start "{self.path}"')
        else:
            print("Invalid Operating system..")
            return False
        return True
    
    def run(self) -> str:
        """Runs the application and returns a message indicating success or failure."""
        if self.start_app():
            return f"{self.name} is running now."
        return f"Oops, some error occurred in opening {self.name}."


def app_runner(name:str) -> str:
    run_app = AppRunner(name)
    result = run_app.run()
    return result


# Example usage:
if __name__ == "__main__":
    app_name = input("Enter the name of the app to open: ")
    app_runner = AppRunner(app_name)
    result = app_runner.run()
    print(result)
