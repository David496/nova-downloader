import requests
from PIL import Image
from io import BytesIO
import customtkinter as ctk
import threading

def load_image_async(widget, url, size, callback):
    """
    Fetches an image from a URL asynchronously. 
    Downloads the data in a background thread, but creates the CTkImage 
    and executes the callback in the main thread to avoid TclErrors.
    """
    def fetch():
        if not url:
            widget.after(0, lambda: callback(None))
            return
            
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            
            # We MUST create the CTkImage in the main thread (using widget.after)
            # to avoid "_tkinter.TclError: image 'pyimageX' doesn't exist"
            def update_ui():
                try:
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
                    callback(ctk_img)
                except Exception as e:
                    print(f"Error creating CTkImage: {e}")
                    callback(None)
            
            widget.after(0, update_ui)
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            widget.after(0, lambda: callback(None))

    threading.Thread(target=fetch, daemon=True).start()
