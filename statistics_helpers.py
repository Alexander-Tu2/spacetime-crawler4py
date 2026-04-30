# statistics_helpers.py

from bs4 import BeautifulSoup
import nltk
import scraper_helpers
import urllib

# nltk code taken from:
# https://www.geeksforgeeks.org/nlp/removing-stop-words-nltk-python/
nltk.download('stopwords')
nltk.download('punkt')

STOPWORDS = set(nltk.corpus.stopwords.words('english'))

# Word threshold for warning log
LOWEST_WORD_COUNT_THRESHOLD = 100

def parse_response(url: str, resp) -> 'str iterator':
    # Returns word-by-word the desirable information from the page content
    # Uses definition of token as in assignment 1 with adjustments:
    #   - Apostrophes are stripped instead of being separators for common 's endings

    # Code here taken & adapted from BeautifulSoup documentation:
    # https://beautiful-soup-4.readthedocs.io/en/latest/
    processed_content = BeautifulSoup(resp.raw_response.content, 'html.parser')
    parsed_words = parse_line(processed_content.get_text())
    yield from format_tokens(parsed_words)


def format_tokens(token_iter: 'str iterable') -> 'str iterator':
    for token in token_iter:
        token = token.lower()
        if token in STOPWORDS:
            continue
        # Remove all 's
        if "'s" in token:
            token = token[:token.find("'")]

        yield token


def parse_line(line: str) -> 'str iterator':
    # Ex: J@hn D#e
    word_start = 0
    word_end = 0
    english_chars = 'abcdefghijklmnopqrstuvwxyz1234567890\''
    for letter in line:
        if letter.lower() in english_chars:
            # Add into current word
            word_end += 1
        else:
            # Remove word & make token
            if word_start == word_end:
                # No blank tokens
                word_start += 1
                word_end += 1
                continue

            yield line[word_start:word_end].lower()
            word_end += 1
            word_start = word_end


UNIQUE_PAGE_COUNT = 0
UNIQUE_PAGE_HASH_SET = set()
LONGEST_PAGE_WORD_COUNT = 0
WORD_COUNT_DICTIONARY = dict() # For 50 most common words
SUBDOMAIN_COUNT_DICTIONARY = dict() # For subdomain unique page count
def write_count(url, resp, token_iter: 'str iterable') -> None:
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
        record_warning_to_file(f'ERROR: Found a duplicate URL: {clean_url}, travelled from '
                               f'{url}')


    # WORD_COUNT_DICTIONARY + LONGEST_PAGE_WORD_COUNT
    global LONGEST_PAGE_WORD_COUNT
    global WORD_COUNT_DICTIONARY
    current_count = compute_word_frequencies(token_iter, WORD_COUNT_DICTIONARY)
    if current_count < LOWEST_WORD_COUNT_THRESHOLD:
        warning_str = f'LOW WORD COUNT ({current_count} < {LOWEST_WORD_COUNT_THRESHOLD}): '\
                      f'At {clean_url}'
        if clean_url != url:
            warning_str += f', redirected from {url}!'
        record_warning_to_file(warning_str)
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
    subdomain = get_subdomain(clean_url)
    if subdomain in subdomain_dict:
        subdomain_dict[subdomain] += 1
    else:
        subdomain_dict[subdomain] = 1


def get_subdomain(url: str) -> str:
    url_obj = urllib.parse.urlsplit(url)
    return url_obj.hostname


def record_count_to_file() -> None:
    """
    Writes the results of the global statistics variables into a log file
    """
    # Four metrics:
    #  -> # of unique pages (UNIQUE_PAGE_COUNT)
    #  -> Longest page (LONGEST_PAGE_WORD_COUNT)
    #  -> Top 50 most common words, sorted by frequency (WORD_COUNT_DICTIONARY)
    #  -> Subdomain count, sorted alphabetically (SUBDOMAIN_COUNT_DICTIONARY)
    unique_pages_string = string_unique_pages(UNIQUE_PAGE_COUNT)
    longest_page_string = string_longest_page(LONGEST_PAGE_WORD_COUNT)
    top_common_words_string = string_top_common_words(WORD_COUNT_DICTIONARY)
    subdomain_count_string = string_subdomain_count(SUBDOMAIN_COUNT_DICTIONARY)

    write_string = (unique_pages_string + "\n" +
                    longest_page_string + "\n" +
                    top_common_words_string + "\n" +
                    subdomain_count_string)

    with open('statistics.txt', 'w') as file:
        file.write(write_string)


def record_warning_to_file(warning: str) -> None:
    with open('warning.txt', 'a') as file:
        file.write(warning + '\n')


def string_unique_pages(unique_page_count) -> str:
    return f'Unique page count: {unique_page_count}\n'


def string_longest_page(longest_page_word_count) -> str:
    return f'Longest page length: {longest_page_word_count}\n'


def string_top_common_words(top_common_words_dict) -> str:
    return f'Top 50 common words: \n{string_frequency_dict(top_common_words_dict, "freq")}'


def string_subdomain_count(subdomain_count_dict) -> str:
    return f'All subdomain counts: \n{string_frequency_dict(subdomain_count_dict, "alphabet")}'


def string_frequency_dict(frequency_dict: dict[str, int], sort_type: str) -> str:
    str_result = ''
    token_list = []
    frequency_list = []
    for (token, frequency) in frequency_dict.items():
        token_list.append(token)
        frequency_list.append(frequency)

    token_list, frequency_list = pairwiseMergeSort(token_list, frequency_list, sort_type)

    for index in range(min(len(token_list), 50)):
        str_result += f'{token_list[index]}, {frequency_list[index]}\n'

    return str_result


# O(u log u) time, where u is the number of unique tokens, since it
#  is a simple modification of merge sort, which is known to take
#  O(n log n) time, where n is the input size, u in this case.
def pairwiseMergeSort(token_list: list[str], freq_list: list[int], sort_type: str) -> tuple[list[str], list[int]]:
    """
    Sorts in decreasing order of frequency,
    sorting both the token_list and freq_list based
    on freq_list entries
    """
    if len(token_list) < 2:
        # Base Case
        return (token_list, freq_list)
    else:
        # Recurse
        halfpoint = len(token_list) // 2
        left_token, left_freq = pairwiseMergeSort(token_list[:halfpoint], freq_list[:halfpoint], sort_type)

        right_token, right_freq = pairwiseMergeSort(token_list[halfpoint:], freq_list[halfpoint:], sort_type)

        # Merge
        new_token_list = []
        new_freq_list = []
        left_index = 0
        right_index = 0

        while left_index < len(left_token) and right_index < len(right_token):
            if sort_type == 'freq':
                if left_freq[left_index] >= right_freq[right_index]:
                    new_token_list.append(left_token[left_index])
                    new_freq_list.append(left_freq[left_index])
                    left_index += 1
                else:
                    new_token_list.append(right_token[right_index])
                    new_freq_list.append(right_freq[right_index])
                    right_index += 1
            else:
                if left_token[left_index] <= right_token[right_index]:
                    new_token_list.append(left_token[left_index])
                    new_freq_list.append(left_freq[left_index])
                    left_index += 1
                else:
                    new_token_list.append(right_token[right_index])
                    new_freq_list.append(right_freq[right_index])
                    right_index += 1

        # Fill in the other incomplete half
        while left_index < len(left_token):
            new_token_list.append(left_token[left_index])
            new_freq_list.append(left_freq[left_index])
            left_index += 1

        while right_index < len(right_token):
            new_token_list.append(right_token[right_index])
            new_freq_list.append(right_freq[right_index])
            right_index += 1

        return new_token_list, new_freq_list


