import os

def apply_auto_cookies(ydl_opts):
    """
    Applies cookies.txt if present in app root or database directory.
    Does NOT auto-probe browser databases to prevent 'Failed to load cookies' lock errors.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check for cookies.txt in app root or database/
    for cfile in ['cookies.txt', os.path.join('database', 'cookies.txt')]:
        cpath = os.path.join(root_dir, cfile) if not os.path.isabs(cfile) else cfile
        if os.path.exists(cpath) and os.path.getsize(cpath) > 10:
            ydl_opts['cookiefile'] = cpath
            break

    return ydl_opts
