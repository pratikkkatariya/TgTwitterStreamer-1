# Telegram - Twitter - Bot
# Github.com/New-dev0/TgTwitterStreamer
# GNU General Public License v3.0

import re, asyncio
from telethon.tl.custom import Button
from . import REPO_LINK, TRACK_WORDS, TRACK_USERS

from .tstreamer import TgStreamer, Var, Client
from tweepy.asynchronous.streaming import StreamRule
from telethon.events import NewMessage, CallbackQuery


async def start_message(event):
    await event.reply(
        Var.START_MESSAGE,
        file=Var.START_MEDIA,
        buttons=[
            [Button.inline("Hello , How Can I Help You ?", data="ok")],
            [
               # Button.url(
                 #   "Source",
                  #  url=REPO_LINK,
                #),
                Button.url("Contact Support", url="https://t.me/pratikkkatariya"),
            ],
        ],
    )


async def callback_query(event):
    await event.answer("Hi👋")


# For people, deploying multiple apps on one bot. (including "me")

if not Var.DISABLE_START:
    Client.add_event_handler(start_message, NewMessage(pattern="^/start$"))
    Client.add_event_handler(callback_query, CallbackQuery(data=re.compile("ok")))


def make_rules() -> str:
    rule = ""
    if not Var.TAKE_RETWEETS:
        rule += "-is:retweet"
    if TRACK_USERS:
        if len(TRACK_USERS) == 1:
            rule += f" from:{TRACK_USERS[0]}"
        else:
            rule += " (" + " OR ".join(f"from:{user}" for user in [TRACK_USERS]) + ") "
    if TRACK_WORDS:
        rule += " (" + " OR ".join(TRACK_WORDS) + ")"
    if Var.EXCLUDE:
        rule += " -".join(Var.EXCLUDE)
    if Var.LANGUAGES:
        rule += " (" + " OR ".join(f"lang:{lang}" for lang in Var.LANGUAGES) + ")"
    return rule


if __name__ == "__main__":
    Stream = TgStreamer(bearer_token=Var.BEARER_TOKEN, wait_on_rate_limit=True)

    async def run():
        rule = make_rules()
        add_rule = True
        old_rules = (await Stream.get_rules()).data

        if old_rules:
            del_ids = []
            for _rule in old_rules:
                if _rule.value != rule:
                    del_ids.append(_rule.id)
                else:
                    add_rule = False
            if del_ids:
                await Stream.delete_rules(del_ids)
        if add_rule:
            await Stream.add_rules(StreamRule(rule))
        Stream.filter(
            expansions=["author_id", "attachments.media_keys"],
            user_fields=["profile_image_url", "name", "username"],
            tweet_fields=["entities", "in_reply_to_user_id"],
            media_fields=["variants", "preview_image_url", "url"],
        )

    Client.loop.run_until_complete(run())

    with Client:
        Client.run_until_disconnected()  # RUN CLIENT
