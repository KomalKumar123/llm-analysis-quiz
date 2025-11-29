import requests

def download_file(url: str) -> bytes:
    """
    Downloads any file (CSV, PDF, JSON, etc.) and returns raw bytes.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content
