'''
Runs giveaway_bot.py's flow across every account configured in config.ini, each
in its own thread, so all your entries go out around the same time instead of
one after another.

This replaces what used to be five nearly-identical account1.py..account5.py
files plus a SUPERSCRIPT.py orchestrator — that orchestrator actually called
Python 2's execfile(), which doesn't exist in Python 3, so it never really ran
in parallel. This version does.
'''

from threading import Thread
from configparser import ConfigParser

from giveaway_bot import enter_giveaway


def get_accounts(parser: ConfigParser):
    '''
    Reads every Username/Password pair from the [Required] section:
    Username/Password, Username1/Password1, Username2/Password2, and so on,
    stopping at the first gap.
    '''
    accounts = []

    username = parser.get('Required', 'Username', fallback=None)
    password = parser.get('Required', 'Password', fallback=None)
    if username and password:
        accounts.append((username, password))

    i = 1
    while True:
        username = parser.get('Required', f'Username{i}', fallback=None)
        password = parser.get('Required', f'Password{i}', fallback=None)
        if not username or not password:
            break
        accounts.append((username, password))
        i += 1

    return accounts


def run_account(username: str, password: str, post_link: str, expr: str, parser: ConfigParser):
    '''
    Thin wrapper around enter_giveaway(): the bot signals both normal completion
    and early termination by calling exit(), which raises SystemExit. That's fine
    for a single-process script, but inside a Thread it would otherwise print a
    scary (and misleading) traceback even on success — so catch it here and just
    print the message.
    '''
    try:
        enter_giveaway(username, password, post_link, expr, parser)
    except SystemExit as exc:
        if exc.code:
            print(exc.code)


def main():
    parser = ConfigParser()
    parser.read('config.ini', encoding='utf8')

    accounts = get_accounts(parser)
    if not accounts:
        exit('No accounts found in config.ini — add at least Username/Password under [Required]')

    print(f'Found {len(accounts)} account(s) in config.ini')

    post_link = input('\tPost Link: ')
    expr = input('\tExpression: ')

    threads = [
        Thread(target=run_account, args=(username, password, post_link, expr, parser))
        for username, password in accounts
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print('All accounts finished.')


if __name__ == '__main__':
    main()
