# Instagram Giveaway Bot

This automates the "tag N friends in the comments to enter" mechanic that a lot of Instagram giveaways use. It logs into your account, works out who to tag (either people you already follow, or a target account's followers/followings), and posts the comments for you, with randomized delays so it doesn't look instantly robotic.

I didn't build this from scratch — it's on top of [Fytex/Instagram-Giveaways-Winner](https://github.com/Fytex/Instagram-Giveaways-Winner) (MIT licensed, `LICENSE` kept as-is). What I added is `multi_account.py`, so I could enter the same giveaway from several accounts at once instead of just one.

> ⚠️ This is against Instagram's Terms of Service, and running several accounts to enter the same giveaway is the kind of thing that can get accounts flagged or banned if you push it too far. I'm sharing this as a record of a project I built, not a recommendation to run it hard.

## What it actually does

1. Logs into an account (reusing a saved session cookie if it has one, so it doesn't have to log in fresh every time).
2. Figures out who to tag — either from a target account's followers/followings (scraped once and cached locally), or from a specific list you provide.
3. Comments on the giveaway post, splitting the list of people across as many comments as needed, mentioning a few per comment.
4. Waits a randomized amount of time between comments (you set a min/max/weighted-average range) so the pacing looks more human.

## Single account vs. multiple

- `giveaway_bot.py` runs one account — this is the base case.
- `multi_account.py` reads every account you've configured (`Username`/`Password`, `Username1`/`Password1`, and so on) and runs all of them **in parallel threads**, so entries across accounts go out around the same time.

Worth mentioning: the original version of the multi-account piece (`SUPERSCRIPT.py` + five nearly-identical `account1.py`..`account5.py` files) actually never ran in parallel — it called Python 2's `execfile()`, which doesn't exist in Python 3, so it would have just crashed. I rewrote it as the single `multi_account.py` above using real threads, which is what I was going for in the first place.

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
- I also had a version of this scraping followers for five real plant-community accounts I was running giveaways from — none of that account-specific data made it in here, just the tool.

## Security note

If you ever find a leaked password in an old project like this one, treat it as compromised — and if you reused it across other accounts (I did), change it everywhere, not just here.
