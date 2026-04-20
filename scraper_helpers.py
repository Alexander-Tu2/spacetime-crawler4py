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
