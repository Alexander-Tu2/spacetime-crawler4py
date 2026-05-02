# scraper_helpers.py
from bs4 import BeautifulSoup
import utils.response
import urllib

REQUIRED_DOMAINS = {'.ics.uci.edu',
                    '.cs.uci.edu',
                    '.informatics.uci.edu',
                    '.stat.uci.edu'}


def contains_required_domains(url: str) -> bool:
    url = urllib.parse.urlsplit(url)
    for domain in REQUIRED_DOMAINS:
        if domain in url.netloc:
            return True

    return False


def return_potential_trap(url: str) -> str:
    potential_traps = 'calendar', 'date', 'dataset', 'login'

    # If url contains trap and anti-trap, let it through
    anti_traps = 'calendars', 'dates', 'datasets'

    contained_trap = return_word_in_list(url, potential_traps)
    contained_anti_trap = return_word_in_list(url, anti_traps)
    pre_trap_char = return_char_before_word_in_str(url, contained_trap)
    trap_is_part_of_word = pre_trap_char.lower() in 'abcdefghijklmnopqrstuvwxyz'
    if contained_trap and not contained_anti_trap and not trap_is_part_of_word:
        return contained_trap

    return ''


def return_word_in_list(url: str, word_list: list) -> str:
    for word in word_list:
        if word in url:
            return word

    return ''


def return_char_before_word_in_str(url: str, keyword: str) -> str:
    if keyword not in url or keyword == '':
        return ''

    keyword_index = url.index(keyword)
    if keyword_index > 0:
        return url[keyword_index - 1]
    else:
        return ''


def is_errorless(error_num: int) -> bool:
    return error_num == 200


def is_fatal_error(error_num: int) -> bool:  # Fatal refers to errors stemming from code
    #non_fatal_errors = 200, 404, 500, 601, 602, 608
    fatal_errors = 429, 600, 603, 604, 605, 606
    return error_num in fatal_errors


# These are all the cache server error codes:
#     600: Request Malformed
#     601: Download Exception {error}
#     602: Spacetime Server Failure
#     603: Scheme has to be either http or https
#     604: Domain must be within spec
#     605: Not an appropriate file extension
#     606: Exception in parsing url
#     607: Content too big. {resp.headers['content-length']}
#     608: Denied by domain robot rules
def get_exit_error(resp: utils.response.Response) -> str:
    status_dict = {429: 'Too many requests',
                   600: 'Request Malformed',
                   601: 'Download Exception',
                   602: 'Spacetime Server Failure',
                   603: 'Scheme has to be either http or https',
                   604: 'Domain must be within spec',
                   605: 'Not an appropriate file extension',
                   606: 'Exception in parsing url',
                   607: 'Content too big',
                   608: 'Denied by domain robot rules'}
    error_str = f'Program stopped due to fatal error code; found error code {resp.status}'
    if resp.status in status_dict:
        error_str += f' - {status_dict[resp.status]}\n'

    error_str += f'Found at scanned URL: {resp.url}\n'
    error_str += f'Error message: {resp.error}\n'

    return error_str


def parse_html_to_url_list(content: str) -> list[str]:
    # Code here taken & adapted from BeautifulSoup documentation:
    # https://beautiful-soup-4.readthedocs.io/en/latest/
    html_page = BeautifulSoup(content, 'html.parser')
    url_list = []
    for attribute_section in html_page.find_all('a'):
        href = attribute_section.get('href')
        if href:
            url_list.append(href)

    return url_list


def remove_fragment_from_list(url_list: list[str]) -> list[str]:
    for (i, url) in enumerate(url_list):
        url_list[i] = remove_fragment(url)

    return url_list


def remove_fragment(url: str) -> str:
    found_fragment_index = -1
    for i in range(len(url) - 1, -1, -1):
        if url[i] == '/':
            return url
        elif url[i] == '#':
            found_fragment_index = i
            break

    if found_fragment_index == -1:
        #print(f'Error: URL |{url}| does not contain a single slash? Might be malformed.')
        return url
    else:
        return url[:found_fragment_index]


def remove_query(url: str) -> str:
    found_fragment_index = -1
    for i in range(len(url) - 1, -1, -1):
        if url[i] == '/':
            return url
        elif url[i] == '?':
            found_fragment_index = i
            break

    if found_fragment_index == -1:
        #print(f'Error: URL |{url}| does not contain a single slash? Might be malformed.')
        return url
    else:
        return url[:found_fragment_index]
