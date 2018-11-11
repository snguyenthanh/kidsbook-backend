from itertools import product
from typing import Set, List
from string import ascii_lowercase, digits
import os.path
import sys

## GLOBAL VARIABLES ##
censor_wordset = set()
replacement_mapping = {
    'a': ('a', '@', '*', '4', '&'),
    'i': ('i', '*', 'l', '!', '1'),
    'o': ('o', '*', '0', '@'),
    'u': ('u', '*', 'v'),
    'v': ('v', '*', 'u'),
    'l': ('l', '1'),
    'e': ('e', '*', '3'),
    's': ('s', '$')
}

allowed_characters = set(ascii_lowercase)
allowed_characters.update(set(digits))
allowed_characters.update(
    set(['@', '!', '$', '^', '*', '&', '\"', '\''])
)


def get_complete_path_of_file(filename: str) -> str:
    """Join the path of the current directory with the input filename."""
    root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(root, filename)

def load_censor_words_from_file():
    """Generate a set of words that need to be censored."""
    global censor_wordset
    if len(censor_wordset) > 0:
        return

    temp_words = read_wordlist()
    all_words = set()
    for word in temp_words:
        all_words.update(
            set(generate_patterns_from_word(word))
        )

    # The default wordlist takes ~5MB of memory
    censor_wordset = all_words

def generate_patterns_from_word(word: str) -> Set[str]:
    """Return all patterns can be generated from the word."""
    combos = [
        (char,) if char not in replacement_mapping
        else replacement_mapping[char]
        for char in iter(word)
    ]
    return (''.join(pattern) for pattern in product(*combos))

def read_wordlist() -> Set[str]:
    """Return words from file `profanity_wordlist.txt`."""

    wordlist_filename = 'profanity_wordlist.txt'
    wordlist_path = get_complete_path_of_file(wordlist_filename)
    try:
        with open(wordlist_path, encoding='utf-8') as wordlist_file:
            # All censor_wordset must be in lowercase
            for row in iter(wordlist_file):
                row = row.strip()
                if row != "":
                    yield row
    except FileNotFoundError:
        print('Unable to find profanity_wordlist.txt')
        pass

def get_replacement_for_swear_word(censor_char: str) -> str:
    return censor_char * 4

def hide_swear_words(text: str, censor_char: str) -> str:
    """Replace the swear words with censor characters."""
    censored_text = ""
    cur_word = ""
    for char in iter(text):
        if char.lower() in allowed_characters:
            cur_word += char
            continue

        if cur_word.lower() in censor_wordset:
            cur_word = get_replacement_for_swear_word(censor_char)

        censored_text += cur_word
        censored_text += char
        cur_word = ""

    if cur_word != "":
        if cur_word.lower() in censor_wordset:
            cur_word = get_replacement_for_swear_word(censor_char)
        censored_text += cur_word

    return censored_text

def censor(text: str, censor_char: str='*') -> str:
    """Replace the swear words in the text with `censor_char`."""

    if not isinstance(text, str):
        text = str(text)
    if not isinstance(censor_char, str):
        censor_char = str(censor_char)

    load_censor_words_from_file()
    print(sys.getsizeof(censor_wordset))
    return hide_swear_words(text, censor_char)


if __name__ == "__main__":
    text = "You son of a bitch, 4rseh0le."

    print(censor(text))
