# Instagram Giveaway Bot

This automates the "tag N friends in the comments to enter" mechanic that a lot of Instagram giveaways use. It logs into your account, works out who to tag (either people you already follow, or a target account's followers/followings), and posts the comments for you, with randomized delays so it doesn't look instantly robotic.

## What it actually does

1. Logs into an account (reusing a saved session cookie if it has one, so it doesn't have to log in fresh every time).
2. Figures out who to tag — either from a target account's followers/followings (scraped once and cached locally), or from a specific list you provide.
3. Comments on the giveaway post, splitting the list of people across as many comments as needed, mentioning a few per comment.
4. Waits a randomized amount of time between comments (you set a min/max/weighted-average range) so the pacing looks more human.

## Single account vs. multiple

- `giveaway_bot.py` runs one account — this is the base case.
- `multi_account.py` reads every account (`Username`/`Password`, `Username1`/`Password1`, and so on) and runs all of them **in parallel threads**, so entries across accounts go out around the same time.


## Setup

```bash
pip install -r requirements.txt
cp config.example.ini config.ini
```

Fill in `config.ini` with your account(s) and the giveaway post link, then run either:

```bash
python giveaway_bot.py       # one account
python multi_account.py      # every account in config.ini, in parallel
```

Chromedriver is fetched automatically via `webdriver-manager` — no need to download or bundle a browser driver yourself.

### Config options worth knowing about

- `expression` is the comment template. `@` just mentions people; something like `Done! @` prefixes every comment with "Done!".
- `followers` (True/False) — whether to pull the target's followers or followings.
- `min` / `max` / `weight` — the randomized delay range (in seconds) between comments, and where in that range it's weighted toward.
- Add more `UsernameN`/`PasswordN` pairs for more accounts; `multi_account.py` picks up as many as it finds.

## What's not included

- **`config.ini`, `cookies/`, `records/`** are all gitignored. `cookies/` holds live session tokens per account, and `records/` caches the real usernames it scraped for each target — neither belongs in a public repo, and neither is needed for the code itself to work.
- I also had a version of this scraping followers for five real plant-community accounts I was running giveaways from. I (oç0bviously) didn't include the scraped data.
