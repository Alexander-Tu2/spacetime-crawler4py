import re
import scraper_helpers
import statistics_helpers
import sys
from urllib.parse import urlparse


# url_hash_set = set()
def scraper(url: str, resp) -> list:
    record_link_information(url, resp)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url: str, resp) -> list:
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if not scraper_helpers.is_errorless(resp.status):
        if scraper_helpers.is_fatal_error(resp.status):
            scraper_helpers.record_error(resp)  # Print or write to log
            sys.exit(-1)
        else:
            statistics_helpers.record_warning_to_file(f'ERROR({resp.status}): Occurred on {resp.url},'
                                                      f' travelled from {url}')
            return list()

    url_list = scraper_helpers.parse_html_to_url_list(resp.raw_response.content)
    scraper_helpers.remove_fragment_from_list(url_list)
    return url_list


def is_valid(url: str) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    parsed = None
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        #elif hash(url) in url_hash_set:
        #    return False
        elif not scraper_helpers.contains_required_domains(url):
            return False
        elif re.match(
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
                  r"|sql|cpp|c|hpp|h|py|java)$", parsed.path.lower()):
            return False
        else:
            #url_hash_set.add(hash(url))
            return True

    except TypeError:
        print("TypeError for ", parsed)
        raise
    except ValueError:
        # May be raised from invalid URLs that are unable to be parsed
        # Example: https://[YOUR_IP]:8443/manager/html
        return False


def record_link_information(url: str, resp) -> None:
    if resp is None or resp.raw_response is None or resp.raw_response.content is None:
        return
    parsed_info_iter = statistics_helpers.parse_response(url, resp)
    statistics_helpers.write_count(url, resp, parsed_info_iter)
    statistics_helpers.record_count_to_file()
