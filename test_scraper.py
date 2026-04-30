import unittest
import scraper
import scraper_helpers


class MyTestCase(unittest.TestCase):
    def test_contains_required_domains(self):
        test_url1 = 'https://www.google.com'
        test_url2 = 'https://zrazy.ics.uci.edu/'
        test_url3 = 'https://thornton.ics.uci.edu/facts-figures/ics-mission-history/'
        test_url4 = 'https://klefstad.cs.ics.uci.edu/explore/'
        test_url5 = 'https://super.informatics.ics.uci.edu/graduate-programs-admissions/#researchprograms'
        test_url6 = 'https://duper.stat.ics.uci.edu/graduate-statistics-programs/#researchprograms'
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
        test_url2 = 'https://cesc.ics.uci.edu/'
        test_url3 = 'https://super.ics.uci.edu/facts-figures/ics-mission-history/'
        test_url4 = 'https://hello.cs.ics.uci.edu/explore/'
        test_url5 = 'https://awesome.informatics.ics.uci.edu/graduate-programs-admissions/#researchprograms'
        test_url6 = 'https://crazy.stat.ics.uci.edu/graduate-statistics-programs/#researchprograms'
        test_url7 = 'https://www.remnote.com/notes'

        correct_but_bad_extension_url = 'https://cs.ics.uci.edu/robots.mp3'
        wrong_scheme_url = 'httptroll://cs.ics.uci.edu/explore/'

        field_test_url1 = 'https://www.google.com/calendar?sprop=website:https://ics.uci.edu/event'
        invalid_url = 'http://your_ip:8080/TomcatFormReCaptcha'
        invalid_url2 = 'https://[YOUR_IP]:8443/manager/html'
        #repeat_url = 'https://ics.uci.edu/'

        test_dict = {test_url1: False,
                     test_url2: True,
                     test_url3: True,
                     test_url4: True,
                     test_url5: True,
                     test_url6: True,
                     test_url7: False,
                     correct_but_bad_extension_url: False,
                     wrong_scheme_url: False,
                     field_test_url1: False,
                     invalid_url: False,
                     invalid_url2: False
                     }

        for (url, result) in test_dict.items():
            #print(f'Attempt: {url}', end='')
            self.assertEqual(result, scraper.is_valid(url))
            #print(f'\rSuccess: {url}')

        #self.assertEqual(False, scraper.is_valid(repeat_url))


    def test_is_errorless(self):
        test_dict = {
            200: True,
            601: False,
            602: False,
            603: False
        }

        for (err_num, result) in test_dict.items():
            self.assertEqual(result, scraper_helpers.is_errorless(err_num))


    def test_is_fatal_error(self):
        test_dict = {
            1: False,
            200: False,
            404: False,
            429: True,
            500: False,
            600: True,
            601: False,
            602: False,
            603: True,
            604: True,
            605: True,
            606: True,
            607: True,
            608: False
        }

        for (err_num, result) in test_dict.items():
            self.assertEqual(result, scraper_helpers.is_fatal_error(err_num))


    def test_remove_fragment_from_list(self):
        test_dict = {
            'www.google.com/search': 'www.google.com/search',
            'https://stackoverflow.com/questions/543309': 'https://stackoverflow.com/questions/543309',
            'https://wiki.leagueoflegends.com/en-us/Champion#Champion_attributes':
                'https://wiki.leagueoflegends.com/en-us/Champion',
            'https://en.wikipedia.org/wiki/Guardian_Tales#Reception': 'https://en.wikipedia.org/wiki/Guardian_Tales'
        }

        for (url, result) in test_dict.items():
            self.assertEqual(result, scraper_helpers.remove_fragment(url))

        test_list = list(test_dict.keys())
        test_list_results = list(test_dict.values())

        scraper_helpers.remove_fragment_from_list(test_list)
        self.assertEqual(test_list_results, test_list)

    def test_parse_html_to_url_list(self):
        html = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
                '<meta content="width=device-width, initial-scale=1, shrink-to-fit=no" name = "viewport">'
                '<title>Fabflix - Movie</title><link rel="stylesheet" href="fabflixstyle.css"></head><body>'
                '<a href="movielist.html"><img id="fabflix_logo" src="fabflix_logo.png" width="200px" height="100px" '
                'alt="Fabflix Logo"></a>'
                '<div class="checkout_button_area"><a href="shoppingcart.html">'
                '<button id="checkout_button" type="button">Checkout</button></a></div>'
                '<h2>Movie Information</h2><p id="title"><strong>Title: </strong> </p>'
                '<p id="year"><strong>Year Released: </strong> </p><p id="director"><strong>Director: </strong> </p>'
                '<p id="genres"><strong>Genres: </strong> </p><p id="rating"><strong>Rating: </strong> </p>'
                '<form id="addtocartbutton" action="#" method="POST"><input type="submit" value="Add to Cart"></form>'
                '<p id="addtocarttext" class="addtocarttext"></p>'
                '<table id="stars_in_movie_table"><tr><th>Starring: </th></tr></table>'
                '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>'
                '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>'
                "<script src='singlemovie.js'></script></body></html>")

        url_list = scraper_helpers.parse_html_to_url_list(html)
        expected_url_list = ['movielist.html', 'shoppingcart.html']

        self.assertEqual(expected_url_list, url_list)


if __name__ == '__main__':
    unittest.main()
