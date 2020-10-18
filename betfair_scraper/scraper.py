import time

from .parser import BetfairParser
from .browser import BetfairBrowser


class BetfairScraper(BetfairBrowser):

    parser = BetfairParser()

    sport_mapping = {
        'SOCCER': 1, 'TENNIS': 2, 'BASKETBALL': 7522, 'GOLF': 3, 'CRICKET': 4,
        'ICE_HOCKEY': 7524, 'VOLLEYBALL': 998917, 'RUGBY': 1477, 'HANDBALL': 468328,
        'BEACH_VOLLEYBALL': 2872194, 'E_SPORTS': 27454571, 'TABLE_TENNIS': 2593174
    }

    market_types = (
        'MATCH_ODDS', 'HALF_TIME', 'BOTH_TEAMS_TO_SCORE', 'DOUBLE_CHANCE',
        'OVER_UNDER_05', 'OVER_UNDER_15', 'OVER_UNDER_25', 'OVER_UNDER_35', 'OVER_UNDER_45',
        'OVER_UNDER_HALF_TIME_05', 'OVER_UNDER_HALF_TIME_15'
    )

    headers_generic = {
        'Origin': 'https://www.betfair.com',
        'Referer': 'https://www.betfair.com/',
        'Content-Type': 'application/json'
    }

    def get_balance(self, name='main'):
        self.logger.debug('API - query balance')

        resp = self.browser.session.get(
            url='https://was.betfair.com/wallet-service/v3.0/wallets',
            headers={
                **self.browser.session.headers,
                **self.headers_generic
            },
            params={
                'walletNames': '[MAIN,SPORTSBOOK_BONUS,BOOST_TOKENS]',
                'alt': 'json'
            }
        )

        wallets = self.parser.api.parse_wallet_service(resp.json())
        return wallets[name]

    def get_bet_activity(self, page_size=25, status='open'):
        self.logger.debug('API - query %s bets', status)

        if status.upper() not in ['OPEN', 'SETTLED']:
            raise ValueError(f'invalid status - {status}')

        resp = self.browser.session.post(
            url='https://myactivity.betfair.com/activity/sportsbook',
            headers={
                **self.browser.session.headers,
                **self.headers_generic
            },
            json={
                'status': status.upper(),
                'dateFilter': 90,
                'fromRecord': 0,
                'pageSize': page_size,
                'oddsType': 'decimal',
                'firstView': False
            }
        )

        return self.parser.api.parse_bet_activity_sportsbook(resp.json())

    def get_inplay_markets(self, sport='soccer', market_type='match_odds', live_stats=True, **kwargs):
        self.logger.debug('API - query market selections')
        self.navigate_url('sport/inplay')

        if sport.upper() not in self.sport_mapping:
            raise ValueError('invalid sport value - {}'.format(sport))

        if market_type.upper() not in self.market_types:
            raise ValueError('invalid market type - {}'.format(market_type))

        resp = self.browser.session.get(
            url='https://www.betfair.com/sport/inplay',
            headers={
                **self.browser.session.headers,
                **self.headers_generic
            },
            params={
                'sportId': self.sport_mapping[sport.upper()],
                'marketType': market_type.upper(),
                'action': 'changeMarketType',
                'modules': 'inplaysports@1002',
                'isAjax': 'true',
                'ts': int(round(time.time() * 1000)),
                'alt': 'json',
                'xsrftoken': self.browser.session.cookies['xsrftoken']
            }
        )

        data = resp.json()
        html = data['page']['config']['instructions'][2]['arguments']['html']

        e = self.parser.parse_html(html)
        return self.parser.html.parse_markets(e, live_stats=live_stats, **kwargs)
