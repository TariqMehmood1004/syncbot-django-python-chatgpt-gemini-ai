import nltk
from nltk.corpus import wordnet
from functools import lru_cache

print("NLTK is RUNNING...")

@lru_cache(maxsize=None)
def get_synonyms(word):
    """
    Get synonyms for a single word using WordNet.
    Uses caching for efficient repeated lookups.
    """
    synonyms = set()
    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().replace('_', ' '))
    except Exception as e:
        print(f"Error fetching synonyms for '{word}': {e}")
    return list(synonyms)

def generate_synonyms(text):
    """
    Generate synonyms for a given text by splitting it into words
    and aggregating results.
    """
    words = text.split()  # Split the text into words
    all_synonyms = set()

    for word in words:
        synonyms = get_synonyms(word)
        all_synonyms.update(synonyms)

    return list(all_synonyms)



