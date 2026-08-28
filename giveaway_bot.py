'''
Logs into an Instagram account, works out who to tag (from records, or by
scraping the target's followers/followings), and comments on a giveaway post
mentioning them — automating the classic "tag N friends to enter" mechanic.

Run this directly for a single account. See multi_account.py to run several
accounts at once from the same config.ini.

Originally built on top of https://github.com/Fytex/Instagram-Giveaways-Winner (MIT).
'''

import signal
from datetime import datetime
from time import sleep
from re import search
from typing import List
from random import triangular
from functools import partial
from configparser import ConfigParser

from modules import Bot, Tab


def enter_giveaway(username: str, password: str, post_link: str, expr: str, parser: ConfigParser):
    '''
    Runs the full flow for a single account: log in, gather who to tag, comment.

    Args:
        - username, password : the account's Instagram credentials
        - post_link           : URL of the giveaway post to comment on
        - expr                : comment template, e.g. '@' to just mention people,
                                 or 'Entering! @' to prefix each comment
        - parser              : a ConfigParser already loaded with config.ini
    '''

    user_target = username
    from_followers = parser.getboolean('Optional', 'Followers', fallback=False)
    limit = parser.getint('Optional', 'Limit', fallback=None)
    specific_file = parser.get('Optional', 'Specific File', fallback=None)
    force_search = parser.getboolean('Optional', 'Force Search', fallback=False)
    save_only = parser.getboolean('Optional', 'Save Only', fallback=False)

    low = parser.getint('Interval', 'Min', fallback=60)
    high = parser.getint('Interval', 'Max', fallback=120)
    weight = parser.getint('Interval', 'Weight', fallback=90)  # Not specified goes for midpoint

    window = parser.getboolean('Browser', 'Window', fallback=True)
    default_lang = parser.getboolean('Browser', 'Default Lang', fallback=False)
    binary_location = parser.get('Browser', 'Location', fallback=None)
    timeout = parser.getint('Browser', 'Timeout', fallback=30)

    if not post_link:
        if not save_only:
            exit('Post Link must be provided or enable Save Only')
        if save_only and not user_target:
            exit('Must specify Post Link or User Target')

    if specific_file:
        if save_only:
            exit('Either choose a Specific File or Save Only')
        if force_search:
            exit('Either choose a Specific File or Force Search')

    does_mention = bool(search(r'(?<!\\)@', expr))

    if limit:
        if force_search:
            exit('Force Search only works if limit is disabled. Otherwise it will always force search to the limit')
        if does_mention and limit <= 0:
            exit('Limit must be > 0')

    if not save_only and not low <= weight <= high:
        exit('Weight must be a number between Min and Max')

    connections_type = "followers" if from_followers else "followings"
    records_path = f'records/{connections_type}'

    bot = Bot(window, binary_location, default_lang, timeout=timeout, records_path=records_path)

    print(f'[{username}] Logging in...')
    bot.log_in(username, password)
    print(f'[{username}] Logged in successfully!')

    connections: List[str] = []

    if specific_file:
        bot.get_user_connections_from_records(specific_file=specific_file, limit=limit)

    elif save_only or does_mention:

        if not user_target:
            print(f'[{username}] Searching for post\'s owner')
            user_target = bot.get_user_from_post(post_link)
            print(f'[{username}] Post\'s owner found!')

        print(f'[{username}] Searching for {user_target}\'s {connections_type} in records')

        success = bot.get_user_connections_from_records(user_target, limit=limit, followers=from_followers)

        if not success or force_search:

            if limit:
                print(f'[{username}] Got {len(bot.connections)}/{limit} {connections_type}. Still not enough...')

            print(f'[{username}] Searching for {user_target}\'s {connections_type} on Instagram')

            count_connections_in_record = len(bot.connections)
            to_quit = False

            try:
                user_target_url = bot.url_base + user_target

                if save_only:
                    bot.driver.get(user_target_url)
                    bot.get_user_connections_from_web(limit, from_followers, force_search)
                else:
                    with Tab(bot.driver, user_target_url):
                        bot.get_user_connections_from_web(limit, from_followers, force_search)

            except KeyboardInterrupt:  # Handle this error in case SIGINT is raised ('ctrl + c')
                to_quit = True

            original_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ignore SIGINT
            connections_added_count = len(bot.connections) - count_connections_in_record

            if connections_added_count:
                bot.save_connections(user_target, bot.connections[-connections_added_count:])

            if to_quit:
                bot.quit(f'[{username}] Early termination. Added {connections_added_count} so far. Making it a total of {len(bot.connections)} {connections_type} in records.')
            else:
                print(f'[{username}] {connections_added_count} found on Instagram. Having a total of {len(bot.connections)} {connections_type} in records.')
                signal.signal(signal.SIGINT, original_sigint)

        else:
            print(f'[{username}] {len(bot.connections)} {connections_type} found in records! No need to search for them on Instagram.')

    if not save_only:
        print(f'[{username}] Let\'s win this giveaway together! Spamming...')

        get_interval = partial(triangular, low, high, weight)

        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f'[{username}] Current time: {current_time}')

            bot.comment_post(post_link, expr, get_interval)

        except Exception:  # Handle this error in case SIGINT is raised ('ctrl + c') [can't use KeyboardInterrupt because SIGINT could lead to more errors]
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            bot.quit(f'[{username}] Early termination. Sent {bot.num_comments} comments so far!')

        else:
            print(f'[{username}] All possible comments were sent. A total of {bot.num_comments} comments!')

    bot.quit(f'[{username}] Program finished with success!')


if __name__ == '__main__':
    parser = ConfigParser()
    parser.read('config.ini', encoding='utf8')

    username = parser.get('Required', 'Username')
    password = parser.get('Required', 'Password')

    post_link = input('\tPost Link: ')
    expr = input('\tExpression: ')

    enter_giveaway(username, password, post_link, expr, parser)
