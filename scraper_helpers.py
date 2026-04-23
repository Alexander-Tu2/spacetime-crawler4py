# scraper_helpers.py
from bs4 import BeautifulSoup
import utils.response

REQUIRED_DOMAINS = {'ics.uci.edu/',
                    'cs.uci.edu/',
                    'informatics.uci.edu/',
                    'stat.uci.edu/'}


def contains_required_domains(url: str) -> bool:
    for domain in REQUIRED_DOMAINS:
        if domain in url:
            return True

    return False


def is_errorless(error_num: int) -> bool:
    return error_num == 200


def is_fatal_error(error_num: int) -> bool:  # Refers to errors stemming from code; must correct
    non_fatal_error = (error_num == 601 or error_num == 602 or error_num == 200)
    return not non_fatal_error


def record_error(resp: utils.response.Response):  # Print or write to log
    print(f'Program stopped due to fatal error code; found error code {resp.status}')
    print(f'Found at scanned URL: {resp.url} and actual URL: {resp.raw_response.url}')
    print(f'Error message: {resp.error}')
    print(f'Content: {resp.raw_response.content}')


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


def remove_fragment(url: str) -> str:
    found_fragment_index = -1
    for i in range(len(url) - 1, -1, -1):
        if url[i] == '/':
            return url
        elif url[i] == '#':
            found_fragment_index = i
            break

    if found_fragment_index == -1:
        print(f'Error: URL |{url}| does not contain a single slash? Might be malformed.')
        return url
    else:
        return url[:found_fragment_index]
