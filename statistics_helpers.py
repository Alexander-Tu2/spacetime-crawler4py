# statistics_helpers.py
import scraper_helpers
import urllib


def parse_response(url: str, resp) -> 'str iterator':
    # Returns word-by-word the desirable information from the page content
    # Uses definition of token as in assignment 1
    pass


UNIQUE_PAGE_COUNT = 0
UNIQUE_PAGE_HASH_SET = set()
LONGEST_PAGE_WORD_COUNT = 0
WORD_COUNT_DICTIONARY = dict() # For 50 most common words
SUBDOMAIN_COUNT_DICTIONARY = dict() # For subdomain unique page count
def write_count(resp, token_iter: 'str iterator') -> None:
    # UNIQUE_PAGE_COUNT
    global UNIQUE_PAGE_COUNT
    global UNIQUE_PAGE_HASH_SET
    clean_url = scraper_helpers.remove_fragment(resp.url)
    clean_hash = hash(clean_url)
    if clean_hash not in UNIQUE_PAGE_HASH_SET:
        UNIQUE_PAGE_HASH_SET.add(clean_hash)
        UNIQUE_PAGE_COUNT += 1
    else:
        # Should not happen during regular operation, assuming
        #  base code filters out duplicates and is_valid removes
        #  URL fragments
        print(f'ERROR: Found a duplicate URL: {clean_url}')


    # WORD_COUNT_DICTIONARY + LONGEST_PAGE_WORD_COUNT
    global LONGEST_PAGE_WORD_COUNT
    global WORD_COUNT_DICTIONARY
    current_count = compute_word_frequencies(token_iter, WORD_COUNT_DICTIONARY)
    LONGEST_PAGE_WORD_COUNT = max(current_count, LONGEST_PAGE_WORD_COUNT)

    # SUBDOMAIN_COUNT_DICTIONARY
    global SUBDOMAIN_COUNT_DICTIONARY
    increment_subdomain_dictionary(clean_url, SUBDOMAIN_COUNT_DICTIONARY)


# Taken & modified from Assignment 1, Part A
def compute_word_frequencies(token_iter: 'str iterator', word_count_dictionary: dict) -> int:
    """
    Given a token iterator, updates the global word count
    dictionary and returns the amount of tokens in the iterator.
    :param token_iter:
    :param word_count_dictionary:
    :return int:
    """
    token_count = 0
    for token in token_iter:
        token_count += 1
        if token not in word_count_dictionary:
            word_count_dictionary[token] = 1
        else:
            word_count_dictionary[token] += 1

    return token_count

def increment_subdomain_dictionary(clean_url: str, subdomain_dict: dict) -> None:
    url_obj = urllib.parse.urlsplit(clean_url)
    subdomain = url_obj.hostname
    if subdomain in subdomain_dict:
        subdomain_dict[subdomain] += 1
    else:
        subdomain_dict[subdomain] = 1





def record_count_to_file() -> None:
    """
    Writes the results of the global statistics variables into a log file
    """
    # Four metrics:
    #  -> # of unique pages (UNIQUE_PAGE_COUNT)
    #  -> Longest page (LONGEST_PAGE_WORD_COUNT)
    #  -> Top 50 most common words, sorted by frequency (WORD_COUNT_DICTIONARY)
    #  -> Subdomain count, sorted alphabetically (SUBDOMAIN_COUNT_DICTIONARY)
    unique_pages_string = string_unique_pages()
    longest_page_string = string_longest_page()
    top_common_words_string = string_top_common_words()
    subdomain_count_string = string_subdomain_count()

    write_string = (unique_pages_string + "\n" +
                    longest_page_string + "\n" +
                    top_common_words_string + "\n" +
                    subdomain_count_string)

    with open('statistics.txt', 'w') as file:
        file.write(write_string)


def string_unique_pages():
    pass

def string_longest_page():
    pass

def string_top_common_words():
    pass

def string_subdomain_count():
    pass