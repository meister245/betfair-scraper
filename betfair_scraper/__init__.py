import os
import getpass

from .scraper import BetfairScraper as Betfair

__version__ = '1.0'

SECRETS_DIR = os.path.expanduser('~') + '/.betfair/'
SECRETS_FILE = SECRETS_DIR + 'secrets'


if not os.path.isdir(SECRETS_DIR):
    os.mkdir(SECRETS_DIR)


if not os.path.isfile(SECRETS_FILE):
    with open(SECRETS_FILE, 'w'):
        pass


def get_secrets(name: str) -> tuple:
    with open(SECRETS_FILE, 'r') as f:
        for row in (x for x in f.read().split('\n') if len(x.strip()) > 0):
            username, password = row.split()

            if username == name:
                return username, password

    username, password = '', ''

    while not password:
        password = getpass.getpass(f'{name} - password: ')

    with open(SECRETS_FILE, 'a') as f:
        f.write(f'{name} {password}\n')

    return username, password
