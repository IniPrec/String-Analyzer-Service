import hashlib  # For hashing functions (to generate the SHA-256 hash)
from collections import Counter # for counting counter frequency.

def analyze_string(value: str):
    """
    Analyze a given string and return its computed properties
    """
    cleaned = value.strip() # removes extra spaces at start/end.
    length = len(cleaned) # gets total number of characters.
    is_palindrome = cleaned.lower() == cleaned[::-1].lower() # checks if the string reads the same backward.
    unique_characters = len(set(cleaned)) # counts how many unique characters there are.
    word_count = len(cleaned.split()) # counts words separated by spaces
    sha256_hash = hashlib.sha256(cleaned.encode()).hexdigest() # generates a unique 64-character hash
    char_frequency_map = dict(Counter(cleaned)) # Maps each character to its occurence count.

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "char_frequency_map": char_frequency_map
    }