from datetime import timedelta

def format_seconds_to_mmss(seconds):
    """Converts seconds (with milliseconds) to MM:SS.mmm format
    
    Args:
        seconds: Either a float (raw seconds) or a string already in MM:SS.mmm format
    """
    # If already formatted, return as-is
    if isinstance(seconds, str):
        return seconds
    
    # Separate integer seconds and milliseconds
    total_seconds = int(seconds)
    milliseconds = int((seconds - total_seconds) * 1000)
    
    # Calculate minutes and seconds
    mm, ss = divmod(total_seconds, 60)
    
    return f"{mm:02}:{ss:02}.{milliseconds:03}"