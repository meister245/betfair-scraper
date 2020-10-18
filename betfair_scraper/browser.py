import logging
import time

try:
    import robobrowser

except ImportError:
    import werkzeug
    werkzeug.cached_property = werkzeug.utils.cached_property
    import robobrowser


class BetfairBrowser:
    base_url = 'https://betfair.com/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'

    def __init__(self):
        self.logger = logging.getLogger('betfair')
        self.browser = self.get_browser()

    @classmethod
    def get_browser(cls):
        return robobrowser.RoboBrowser(
            user_agent=cls.user_agent,
            parser='html5lib'
        )

    def navigate_url(self, url=''):
        self.logger.debug('browser - navigation')
        self.browser.open(self.base_url + url.strip('/'))

    def login(self, secrets: tuple):
        self.logger.debug('browser - login')

        self.navigate_url()

        f = self.browser.get_form()
        f['username'], f['password'] = secrets

        self.browser.submit_form(f)
        f = self.browser.get_form()

        if 'loginStatus=SUCCESS' not in str(f):
            raise Exception('invalid login credentials')

    def submit_bet(self, href: str, uuid: dict, stake: float):
        self.logger.debug('browser - edit betslip')
        self.navigate_url(href)

        f = self.browser.get_form(class_='betslip-form-edit')
        f['bet-{}-stake'.format(uuid)] = stake
        f['bonus'], f['odds-movement'] = [], []

        self.logger.debug('browser - submit bet')
        self.browser.submit_form(f)

        time.sleep(5)

        if result := bool(self.browser.parsed.find(
                'div', attrs={'class': 'confirmed-bets-container'})):
            self.logger.debug('browser - bet placed')

        else:
            self.logger.error('browser - failed to place bet')

        if e := self.browser.parsed.find('a', attrs={'class': 'remove-all-bets'}):
            self.logger.debug('browser - reset bet form')
            self.navigate_url(e['href'])

        return result
