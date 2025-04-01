import webbrowser 


def search_youtube(topic:str) -> None:
    """Search YouTube for a specific topic."""
    format_topic = "+".join(topic.split())
    link = f"https://www.youtube.com/results?search_query={format_topic}"
    webbrowser.open(link)
    return None 


def yt_trending():
    """Open Youtube trending page."""
    link = f"https://www.youtube.com/feed/trending"
    webbrowser.open(link)
    return None 


