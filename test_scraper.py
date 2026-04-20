import unittest
import scraper
import scraper_helpers


class MyTestCase(unittest.TestCase):
    def test_contains_required_domains(self):
        test_url1 = 'https://www.google.com'
        test_url2 = 'https://ics.uci.edu/'
        test_url3 = 'https://ics.uci.edu/facts-figures/ics-mission-history/'
        test_url4 = 'https://cs.ics.uci.edu/explore/'
        test_url5 = 'https://informatics.ics.uci.edu/graduate-programs-admissions/#researchprograms'
        test_url6 = 'https://stat.ics.uci.edu/graduate-statistics-programs/#researchprograms'
        test_url7 = 'https://www.remnote.com/notes'

        test_dict = {test_url1: False,
                     test_url2: True,
                     test_url3: True,
                     test_url4: True,
                     test_url5: True,
                     test_url6: True,
                     test_url7: False}

        for (url, result) in test_dict.items():
            self.assertEqual(result, scraper_helpers.contains_required_domains(url))
            #print(f'Success: {url}')

    def test_is_valid_filters_correct_urls(self):
        test_url1 = 'https://www.google.com'
        test_url2 = 'https://ics.uci.edu/'
        test_url3 = 'https://ics.uci.edu/facts-figures/ics-mission-history/'
        test_url4 = 'https://cs.ics.uci.edu/explore/'
        test_url5 = 'https://informatics.ics.uci.edu/graduate-programs-admissions/#researchprograms'
        test_url6 = 'https://stat.ics.uci.edu/graduate-statistics-programs/#researchprograms'
        test_url7 = 'https://www.remnote.com/notes'

        correct_but_bad_extension_url = 'https://cs.ics.uci.edu/robots.mp3'
        wrong_scheme_url = 'httptroll://cs.ics.uci.edu/explore/'

        test_dict = {test_url1: False,
                     test_url2: True,
                     test_url3: True,
                     test_url4: True,
                     test_url5: True,
                     test_url6: True,
                     test_url7: False,
                     correct_but_bad_extension_url: False,
                     wrong_scheme_url: False}

        for (url, result) in test_dict.items():
            self.assertEqual(result, scraper.is_valid(url))
            # print(f'Success: {url}')


if __name__ == '__main__':
    unittest.main()
