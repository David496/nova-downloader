import requests
from PIL import Image
from io import BytesIO
import customtkinter as ctk
import threading

def load_image_async(url, size, callback):
    """
    Fetches an image from a URL asynchronously and returns a CTkImage via the callback.
    """
    def fetch():
        if not url:
            callback(None)
            return
            
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            # Crop to aspect ratio 16:9 for thumbnails if needed, but standard resize is fine
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            # Use root.after to safely update the GUI thread
            callback(ctk_img)
        except Exception as e:
            print(f"Error loading image: {e}")
            callback(None)

    threading.Thread(target=fetch, daemon=True).start()
