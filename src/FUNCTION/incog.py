import os
from src.FUNCTION.get_env import check_os
from subprocess import run, DEVNULL


def open_chrome_incognito(topic: str) -> None:
    """Open Chrome in Incognito mode (Windows)."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    # ✅ Check for the correct path
    chrome_path = next((path for path in possible_paths if os.path.exists(path)), None)
    
    if chrome_path:
        search_url = f"https://www.google.com/search?q={topic}"
        run([chrome_path, "--incognito", search_url], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print("❌ Chrome not found. Please install Chrome or use another browser.")
    

def open_firefox_private(topic: str) -> None:
    """Open Firefox in Private mode (Windows)."""
    possible_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    
    firefox_path = next((path for path in possible_paths if os.path.exists(path)), None)

    if firefox_path:
        search_url = f"https://www.google.com/search?q={topic}"
        run([firefox_path, "-private-window", search_url], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print("❌ Firefox not found. Trying Edge...")
        open_edge_private(topic)


def open_edge_private(topic: str) -> None:
    """Open Microsoft Edge in InPrivate mode (Windows)."""
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    if os.path.exists(edge_path):
        search_url = f"https://www.google.com/search?q={topic}"
        run([edge_path, "--inprivate", search_url], stdout=DEVNULL, stderr=DEVNULL)
    else:
        print("❌ Edge not found. Please install a supported browser.")


def linux_firefox(topic: str) -> None:
    """Open Firefox in Private mode on Linux."""
    search_url = f"https://www.google.com/search?q={topic}"
    run(["firefox", "--private-window", search_url], stdout=DEVNULL, stderr=DEVNULL)

def incog_mode(topic:str) -> None:
    """"Search in the incognito or private mode for specific topic"""
    # Construct the URL for Google search with the topic
    search_url = f"https://www.google.com/search?q={topic}"
    applescript_code = f'''
    tell application "Google Chrome"
    activate
        tell (make new window with properties {{mode:"incognito"}})
            set URL of active tab to "{search_url}"
        end tell
    end tell'''
    run(['osascript', '-e', applescript_code])
    return  

def incog_mode_mac(topic: str) -> None:
    """Open Safari in Private mode on macOS using AppleScript."""
    search_url = f"https://www.google.com/search?q={topic}"
    # ✅ Corrected AppleScript for macOS Safari
    applescript_code = f'''
    tell application "Safari"
        activate
        tell application "System Events"
            keystroke "n" using {{command down, shift down}} -- Open Private Window
        end tell
        delay 1 -- Give time to open Private Window
        tell window 1
            set current tab to (make new tab with properties {{URL:"{search_url}"}})
        end tell
    end tell
    '''
    run(['osascript', '-e', applescript_code], stdout=DEVNULL, stderr=DEVNULL)


def private_mode(topic: str) -> None:
    """Open the specified topic in private/incognito mode."""
    os_name = check_os()

    if os_name == "Linux":
        linux_firefox(topic)

    elif os_name == "Darwin":  # macOS
        incog_mode_mac(topic)

    elif os_name == "Windows":
        # ✅ Try Chrome first, fallback to Firefox, then Edge
        try:
            open_chrome_incognito(topic)
        except Exception:
            try:
                open_firefox_private(topic)
            except Exception:
                open_edge_private(topic)
    else:
        print("❌ Unsupported Operating System.")
