def word_count(text):
    """
    Counts the number of words in a given text.
    """
    if not text:
        return 0
    return len(text.split())