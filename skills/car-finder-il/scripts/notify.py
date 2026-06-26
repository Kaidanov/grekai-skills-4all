"""
notify.py — the "pops up on your phone" leg.

Picks whichever channel you've configured, in this order:
  WAAI_WEBHOOK_URL   -> POST {text} to your own wa-ai agent (WhatsApp)   [best]
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID -> Telegram message
  NTFY_TOPIC         -> ntfy.sh push (zero setup, public topic)
  (none)             -> just print to stdout

wa-ai is the natural fit — you already built it and it's the most phone-native
popup you own. Everything here is stdlib urllib.
"""
import json
import os
import urllib.request
import urllib.parse


def send(text):
    """Returns the channel name actually used."""
    if os.environ.get("WAAI_WEBHOOK_URL"):
        _waai(text)
        return "wa-ai"
    if os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"):
        _telegram(text)
        return "telegram"
    if os.environ.get("NTFY_TOPIC"):
        _ntfy(text)
        return "ntfy"
    print(text)
    return "stdout"


def _post(url, data, headers=None, raw=False):
    body = data if raw else json.dumps(data).encode("utf-8")
    h = headers or {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    urllib.request.urlopen(req, timeout=30).read()


def _waai(text):
    _post(os.environ["WAAI_WEBHOOK_URL"], {"text": text, "source": "car-finder-il"})


def _telegram(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = "https://api.telegram.org/bot%s/sendMessage" % token
    _post(url, {"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text,
                "disable_web_page_preview": False})


def _ntfy(text):
    topic = os.environ["NTFY_TOPIC"]
    url = "https://ntfy.sh/" + urllib.parse.quote(topic)
    _post(url, text.encode("utf-8"),
          headers={"Title": "car-finder-il", "Content-Type": "text/plain; charset=utf-8"},
          raw=True)
