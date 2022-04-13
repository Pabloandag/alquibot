import cloudscraper, requests
from bs4 import BeautifulSoup
from hashlib import sha1
from urllib.parse import urlparse
from dataclasses import dataclass

BOT_ID = "Aqui va tu bot token"
ROOM_ID = "ID del chat al que el bot va a publicar"
urls = [
    "https://www.argenprop.com/departamento-alquiler-sub-barrio-recoleta-barrio-palermo-barrio-belgrano-barrio-almagro-barrio-villa-crespo-hasta-60000-pesos-desde-45-m2-cubiertos",
    "https://www.zonaprop.com.ar/departamentos-alquiler-palermo-belgrano-recoleta-almagro-villa-crespo-mas-45-m2-cubiertos-menos-60000-pesos-orden-antiguedad-ascendente.html",
]


@dataclass
class Parser:
    website: str
    link_regex: str
    href : str
    _id: str
    def extract_links(self, contents: str):
        soup = BeautifulSoup(contents, "lxml")
        ads = soup.select(self.link_regex)#soup.find_all("div",class_="postingCard")
        for ad in ads:
            href = ad[self.href]
            _id = ad[self._id]
            yield {"id": _id, "url": "{}{}".format(self.website, href)}


parsers = [
    Parser(website="https://www.zonaprop.com.ar", link_regex="div.postingCard",href="data-to-posting",_id="data-id"),
    Parser(website="https://www.argenprop.com", link_regex="div.listing__items div.listing__item a.card",href="href",_id="data-item-card"),
    #Parser(website="https://inmuebles.mercadolibre.com.ar", link_regex="li.results-item .rowItem.item a"),
]


def _main():
    scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False},delay=10)
    for url in urls:
        res = scraper.get(url)
        if res.status_code != 200:
            print("Error de respuesta")
            return
        ads = list(extract_ads(url, res.text))
        seen, unseen = split_seen_and_unseen(ads)
        parse = urlparse(url)

        print("{} has {} seen, {} unseen".format(parse.netloc,len(seen), len(unseen)))

        for u in unseen:
            notify(u)

        mark_as_seen(unseen)


def extract_ads(url, text):
    uri = urlparse(url)
    parser = next(p for p in parsers if uri.hostname in p.website)
    return parser.extract_links(text)


def split_seen_and_unseen(ads):
    history = get_history()
    seen = [a for a in ads if a["id"] in history]
    unseen = [a for a in ads if a["id"] not in history]
    return seen, unseen


def get_history():
    try:
        with open("seen.txt", "r") as f:
            return {l.rstrip() for l in f.readlines()}
    except:
        return set()


def notify(ad):
    bot = BOT_ID
    room = ROOM_ID
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(bot, room, ad["url"])
    r = requests.get(url)


def mark_as_seen(unseen):
    with open("seen.txt", "a+") as f:
        ids = ["{}\n".format(u["id"]) for u in unseen]
        f.writelines(ids)


if __name__ == "__main__":
    _main()