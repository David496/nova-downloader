import requests
from PIL import Image
from io import BytesIO

def fetch_image_bytes(url, timeout=5):
    """Fetches image bytes synchronously with error handling."""
    if not url:
        return None
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching image bytes: {e}")
        return None
