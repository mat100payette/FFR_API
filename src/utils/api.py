_API_URL = "https://www.flashflashrevolution.com/api/api.php"
_API_KEY = ""


def set_api_key(key: str):
    global _API_KEY
    _API_KEY = key


def api_key():
    return _API_KEY


def api_url():
    return _API_URL
