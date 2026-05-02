# statistics_helpers.py

import ast
from bs4 import BeautifulSoup
import nltk
import os
import random
import scraper_helpers
import urllib



# nltk stopwords code taken from:
# https://www.geeksforgeeks.org/nlp/removing-stop-words-nltk-python/
nltk.download('stopwords')
nltk.download('punkt')

STOPWORDS = set(nltk.corpus.stopwords.words('english'))

# Word threshold for warning log
LOWEST_WORD_COUNT_THRESHOLD = 50

# Near-duplicate threshold
NEAR_DUPLICATE_THRESHOLD = 0.95

IS_DUPLICATE = False
def parse_response(url: str, resp) -> 'str iterator':
    # Returns word-by-word the desirable information from the page content
    # Uses definition of token as in assignment 1 with adjustments:
    #   - Apostrophes are stripped instead of being separators for common 's endings

    # Code here taken & adapted from BeautifulSoup documentation:
    # https://beautiful-soup-4.readthedocs.io/en/latest/
    global IS_DUPLICATE
    processed_content = BeautifulSoup(resp.raw_response.content, 'html.parser')
    IS_DUPLICATE = False
    check_exact_duplicate(processed_content, url)
    parsed_words = parse_line(processed_content.get_text())
    yield from format_tokens(parsed_words, resp)


EXACT_DUPLICATE_HASH_SET = set()
def check_exact_duplicate(content: str, url: str) -> None:
    # Implementing hashing for exact duplicate detection
    global IS_DUPLICATE
    content_hash = hash(content)
    if content_hash in EXACT_DUPLICATE_HASH_SET:
        IS_DUPLICATE = True
        record_warning_to_file(f'EXACT DUPLICATE: {url}')
    else:
        EXACT_DUPLICATE_HASH_SET.add(content_hash)


NEAR_DUPLICATE_SIMHASH_SET = set()
NEAR_DUPLICATE_SIMHASH_DICTIONARY = dict()  # To assign word to consistent 16-bit hash value
def check_near_duplicate(frequency_dict: dict[str, int], url: str) -> None:
    # Implement simhash for near duplicate detection
    # 16-bit simhash; num from 0 to 65,535
    global IS_DUPLICATE
    website_simhash_value = get_website_simhash_value(frequency_dict)
    largest_similarity_score = 0.0

    for simhash in NEAR_DUPLICATE_SIMHASH_SET:
        similarity_count = 0
        for index in range(len(website_simhash_value)):
            if website_simhash_value[index] == simhash[index]:
                similarity_count += 1

        similarity_score = similarity_count / len(website_simhash_value)
        largest_similarity_score = max(similarity_score, largest_similarity_score)

    if largest_similarity_score >= NEAR_DUPLICATE_THRESHOLD:
        IS_DUPLICATE = True
        record_warning_to_file(f'NEAR DUPLICATE ({largest_similarity_score}): {url}')


def get_website_simhash_value(frequency_dict: dict[str, int]) -> list:
    hash_value_bit_length = 16
    total_hash_value = [0 for x in range(hash_value_bit_length)]
    for word, frequency in frequency_dict.items():
        word_hash_value = tuple()
        if word in NEAR_DUPLICATE_SIMHASH_DICTIONARY:
            word_hash_value = NEAR_DUPLICATE_SIMHASH_DICTIONARY[word]
        else:
            word_hash_value = generate_word_hash(word)

        for index in range(len(total_hash_value)):
            total_hash_value[index] += word_hash_value[index] * frequency

    for index in range(len(total_hash_value)):
        if total_hash_value[index] < 0:
            total_hash_value[index] = 0
        else:
            total_hash_value[index] = 1

    return total_hash_value


def generate_word_hash(word: str) -> tuple:
    if word in NEAR_DUPLICATE_SIMHASH_DICTIONARY:
        return NEAR_DUPLICATE_SIMHASH_DICTIONARY[word]

    random_number = random.randint(0, 65535)
    word_hash_value = list()
    for bit_index in range(15, -1, -1): # From 15 to 0
        word_hash_value.append(get_bit(random_number, bit_index))

    NEAR_DUPLICATE_SIMHASH_DICTIONARY[word] = tuple(word_hash_value)
    return NEAR_DUPLICATE_SIMHASH_DICTIONARY[word]


def get_bit(value: int, bit_num: int) -> int:
    # bit_num = 0 means right bit
    return (value >> bit_num) & 1


PRINT_NEXT_WORD_COUNT = 0
def format_tokens(token_iter: 'str iterable', resp = None) -> 'str iterator':
    for token in token_iter:
        token = token.lower()
        if token in STOPWORDS:
            continue

        # Remove all 's
        if "'s" in token:
            token = token[:token.find("'")]

        # Remove all single-character letters and numbers
        if len(token) <= 1:
            continue

        yield token


def parse_line(line: str) -> 'str iterator':
    # Ex: J@hn D#e
    word_start = 0
    word_end = 0
    english_chars = 'abcdefghijklmnopqrstuvwxyz1234567890\':'
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
    unique_url = scraper_helpers.remove_query(clean_url)
    unique_hash = hash(unique_url)
    if unique_hash not in UNIQUE_PAGE_HASH_SET:
        UNIQUE_PAGE_HASH_SET.add(unique_hash)
        UNIQUE_PAGE_COUNT += 1
    else:
        # Could happen during regular operation, since unique pages uses
        #  more restrictive definition of unique
        record_warning_to_file(f'POTENTIAL DUPLICATE: Found {clean_url} which uses already recorded base '
                               f'{unique_url}')

    # SUBDOMAIN_COUNT_DICTIONARY
    global SUBDOMAIN_COUNT_DICTIONARY
    increment_subdomain_dictionary(clean_url, SUBDOMAIN_COUNT_DICTIONARY)

    # NEAR DUPLICATE DETECTION
    global WORD_COUNT_DICTIONARY
    current_count = compute_word_frequencies(token_iter, WORD_COUNT_DICTIONARY)
    check_near_duplicate(current_count, url)

    global IS_DUPLICATE
    if IS_DUPLICATE:
        IS_DUPLICATE = False
        return

    # WORD_COUNT_DICTIONARY + LONGEST_PAGE_WORD_COUNT
    global LONGEST_PAGE_WORD_COUNT


    if current_count < LOWEST_WORD_COUNT_THRESHOLD:
        warning_str = f'LOW WORD COUNT ({current_count} < {LOWEST_WORD_COUNT_THRESHOLD}): '\
                      f'At {clean_url}'
        if clean_url != url:
            warning_str += f', redirected from {url}!'
        record_warning_to_file(warning_str)
    LONGEST_PAGE_WORD_COUNT = max(current_count, LONGEST_PAGE_WORD_COUNT)



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

'''
UNIQUE_PAGE_COUNT = 0
UNIQUE_PAGE_HASH_SET = set()
LONGEST_PAGE_WORD_COUNT = 0
WORD_COUNT_DICTIONARY = dict() # For 50 most common words
SUBDOMAIN_COUNT_DICTIONARY = dict() # For subdomain unique page count
'''
def record_globals_to_file() -> None:
    with open('statistics_state.txt', 'w') as file:
        file.write(f'{UNIQUE_PAGE_COUNT}\n')
        file.write(f'{UNIQUE_PAGE_HASH_SET}\n')
        file.write(f'{LONGEST_PAGE_WORD_COUNT}\n')
        file.write(f'{WORD_COUNT_DICTIONARY}\n')
        file.write(f'{SUBDOMAIN_COUNT_DICTIONARY}\n')


def load_globals_from_file() -> None:
    global UNIQUE_PAGE_COUNT
    global UNIQUE_PAGE_HASH_SET
    global LONGEST_PAGE_WORD_COUNT
    global WORD_COUNT_DICTIONARY
    global SUBDOMAIN_COUNT_DICTIONARY
    if not os.path.exists('statistics_state.txt'):
        print(f'statistics_state.txt does not exist to load!')
        return
    else:
        print(f'Loading statistics_state.txt!')
    with open('statistics_state.txt', 'r') as file:
        count = 0
        for line in file:
            line = line.strip()
            if count == 0:
                UNIQUE_PAGE_COUNT = int(line)
                print(f'UNIQUE_PAGE_COUNT is now: {UNIQUE_PAGE_COUNT}')
            elif count == 1:
                UNIQUE_PAGE_HASH_SET = ast.literal_eval(line)
                print(f'UNIQUE_PAGE_HASH_SET is now length: {len(UNIQUE_PAGE_HASH_SET)}')
            elif count == 2:
                LONGEST_PAGE_WORD_COUNT = int(line)
                print(f'LONGEST_PAGE_WORD_COUNT is now: {LONGEST_PAGE_WORD_COUNT}')
            elif count == 3:
                WORD_COUNT_DICTIONARY = ast.literal_eval(line)
                print(f'WORD_COUNT_DICTIONARY is now length: {len(WORD_COUNT_DICTIONARY)}')
            elif count == 4:
                SUBDOMAIN_COUNT_DICTIONARY = ast.literal_eval(line)
                print(f'SUBDOMAIN_COUNT_DICTIONARY is now length: {len(SUBDOMAIN_COUNT_DICTIONARY)}')
            else:
                break

            count += 1


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

    token_list, frequency_list = pairwise_merge_sort(token_list, frequency_list, sort_type)

    for index in range(min(len(token_list), 50)):
        str_result += f'{token_list[index]}, {frequency_list[index]}\n'

    return str_result


# O(u log u) time, where u is the number of unique tokens, since it
#  is a simple modification of merge sort, which is known to take
#  O(n log n) time, where n is the input size, u in this case.
def pairwise_merge_sort(token_list: list[str], freq_list: list[int], sort_type: str) -> tuple[list[str], list[int]]:
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
        left_token, left_freq = pairwise_merge_sort(token_list[:halfpoint], freq_list[:halfpoint], sort_type)

        right_token, right_freq = pairwise_merge_sort(token_list[halfpoint:], freq_list[halfpoint:], sort_type)

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


