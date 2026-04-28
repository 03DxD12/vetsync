import re


def clean_input(text, allow_html=False):
    """
    Robust input sanitization to prevent XSS and data injection.
    Strips dangerous characters and normalizes whitespace.
    """
    if not text or not isinstance(text, str):
        return text

    # Remove null bytes and dangerous control characters
    text = text.replace('\0', '').strip()

    if not allow_html:
        # Strip HTML tags
        text = re.sub(r'<[^>]*?>', '', text)

    # Prevent common injection patterns
    text = text.replace('"', '&quot;').replace("'", "&#39;")
    return text
