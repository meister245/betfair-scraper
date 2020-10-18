import time

from bs4 import BeautifulSoup


class BetfairAPIParser:

    @staticmethod
    def parse_wallet_service(resp):
        return {
            wallet['walletName'].lower(): float(wallet['details']['amount'])
            for wallet in resp if wallet['status'].lower() == 'success'
        }

    @staticmethod
    def parse_bet_activity_sportsbook(resp):
        return [
            {
                'market_id': bet['marketId'],
                'bet_id': bet['betId'],
                'result': bet['status'].lower(),
                'stake': bet['stakeCash'],
                'return': bet['returnCash'],
                'market_name': bet['marketName'],
                'event': bet['eventDescription'],
                'type': bet['selection'].upper()
            }
            for bet in resp['bets']
        ]


class BetfairHTMLParser:

    @classmethod
    def parse_event_information(cls, e):
        return {
            'competition': e.find(attrs={'data-competition': True})['data-competition'],
            'event_id': e['data-eventid'],
            'event': e.find(attrs={'data-event': True})['data-event'],
            'market_id': e.find(attrs={'data-marketid': True})['data-marketid'],
            'market': e.find(attrs={'data-market': True})['data-market'],
            'sport_id': e.find(attrs={'data-sport-id': True})['data-sport-id'],
            'sport': e.find(attrs={'data-sport': True})['data-sport'],
            'state': cls.parse_event_details(e),
            'bets': cls.parse_bets(e),
            'ts': int(time.time())
        }

    @classmethod
    def parse_bets(cls, e):
        bets = None

        if status_text := e.find(attrs={'class': 'status-text'}):
            value = getattr(status_text, 'text', '').strip()

            if value.lower() == 'suspended':
                bets = False

        try:
            if bets is None:
                bets = [cls.parse_bet_selection(x) for x in e.find_all(
                    attrs={'class': 'com-bet-button'})]

                bets = tuple(bets)

        except (KeyError, ValueError):
            bets = None

        return bets

    @staticmethod
    def parse_bet_selection(e):
        odds = getattr(
            e.find(attrs={'class': 'ui-runner-price'}), 'text', '').strip()

        return {
            'href': e['href'],
            'uuid': e['data-uuid'],
            'selection_id': e['data-selectionid'],
            'odds': float(odds)
        }

    @classmethod
    def parse_event_details(cls, e):
        details = e.find(attrs={'details-event'})

        live_stats = False
        game_time = cls.parse_game_time(details)
        scores, sets, games = cls.parse_game_state(details)

        if game_time:
            if scores or sets or games:
                live_stats = True

        return {
            'live_stats': live_stats, 'game_time': game_time,
            'scores': scores, 'sets': sets, 'games': games
        }

    @staticmethod
    def parse_game_state(e):

        score_home = getattr(
            e.find(attrs={'class': 'ui-score-home'}), 'text', '').strip()
        score_away = getattr(
            e.find(attrs={'class': 'ui-score-away'}), 'text', '').strip()

        try:
            scores = (int(score_home), int(score_away))

        except (TypeError, ValueError):
            scores = None

        games_home = getattr(
            e.find(attrs={'class': 'ui-games-home'}), 'text', '').strip()
        games_away = getattr(
            e.find(attrs={'class': 'ui-games-away'}), 'text', '').strip()

        try:
            games = (int(games_home), int(games_away))

        except (TypeError, ValueError):
            games = None

        sets_home = getattr(
            e.find(attrs={'class': 'ui-sets-home'}), 'text', '').strip()
        sets_away = getattr(
            e.find(attrs={'class': 'ui-sets-away'}), 'text', '').strip()

        try:
            sets = (int(sets_home), int(sets_away))

        except (TypeError, ValueError):
            sets = None

        return scores, sets, games

    @staticmethod
    def parse_game_time(e):
        if et_anim_container := e.find(attrs={'class': 'et-anim-container'}):
            if score_container := et_anim_container.find(attrs={'class': 'ui-score-container'}):
                inplay_state = score_container.find(
                    attrs={'class': 'event-inplay-state'})

                value = getattr(inplay_state, 'text',
                                '').strip().replace('′', '')

                if value.isdigit():
                    return int(value)

                if len(value) != 0:
                    return value

        return None

    def parse_markets(self, e, **kwargs):
        for event in e.find_all('div', attrs={'class': 'event-information'}):
            parsed = self.parse_event_information(event)

            if kwargs.get('live_stats', False) and not parsed['state']['live_stats']:
                continue

            if not kwargs.get('suspended', False) and not parsed['bets']:
                continue

            yield parsed


class BetfairParser:
    api = BetfairAPIParser()
    html = BetfairHTMLParser()

    @staticmethod
    def parse_html(html: str):
        return BeautifulSoup(html, 'html5lib')
