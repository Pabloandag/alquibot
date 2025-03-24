import requests
import time
from parser import ZonaPropParser, ArgenPropParser, CabaPropParser
from db_handler import FileHandler

CHAT_ID = "YourChatId"
BOT_TOKEN = "YourBotToken"

ZONAPROP_URL = ""
ARGENPROP_URL = ""
CABAPROP_URL = ""


class TelegramBot:
    def __init__(self, token: str):
        self.token = token

    def send_message_to_chat(self, chat_id: str, message: str):
        request_url = (
            "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
                self.token, chat_id, message
            )
        )
        r = requests.get(request_url)
        return r


if __name__ == "__main__":
    file_handler = FileHandler()
    bot = TelegramBot(BOT_TOKEN)
    parsers = {
        "zonaprop": ZonaPropParser(ZONAPROP_URL),
        "argenprop": ArgenPropParser(ARGENPROP_URL),
        # "cabaprop": CabaPropParser(CABAPROP_URL),
    }

    for portal, parser in parsers.items():
        ads = parser.get_ads()
        seen_ids = file_handler.get_ids(portal=portal)
        unseen_ads = [ad for ad in ads if ad.id not in seen_ids]
        ids_to_add = list()
        for ad in unseen_ads:
            print(f"PARSER {parser.__class__.__name__} found URL: {ad.url}")
            response = bot.send_message_to_chat(CHAT_ID, ad.url)
            if response.status_code == 200:
                ids_to_add.append(ad.id)
            elif response.status_code == 429:
                # Too many requests
                print(f"Too many requests, sleeping for 1 second")
                time.sleep(1)
                response = bot.send_message_to_chat(CHAT_ID, ad.url)
                if response.status_code == 200:
                    print("Request retry was successful")
                    ids_to_add.append(ad.id)
                else:
                    print("Could not send request")
            else:
                print("Failed to send message to chat with url {}".format(ad.url))
        file_handler.add_ids(ids_to_add, portal)
