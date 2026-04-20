# scraper_helpers.py




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


def record_error(resp):  # Print or write to log
    print(f'Program stopped due to fatal error code; found error code {resp.status}')
    print(f'Found at scanned URL: {resp.url} and actual URL: {resp.raw_response.url}')
    print(f'Error message: {resp.error}')


def parse_url_list(resp):
    pass

def remove_fragment(url_list):
    pass
