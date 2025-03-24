import re
import requests
import cloudscraper
from bs4 import BeautifulSoup, Tag
from urllib.request import urlopen
from abc import ABC, abstractmethod
from dataclasses import dataclass


class ParseException(Exception):
    pass


class LinkNotFound(ParseException):
    pass


class PriceNotFound(ParseException):
    pass


class IdNotFound(ParseException):
    pass


@dataclass
class AptAd:
    id: str
    url: str
    price: str
    img_url: str = None
    description: str = None


class Parser(ABC):
    BASE_URL: str = None
    POST_CONTAINER_TAG: str = "div"
    POST_CONTAINER_CLASS: str = None
    PRICE_CONTAINER_TAG: str = "div"
    PRICE_CONTAINER_CLASS: str = None

    def __init__(self, filter_href: str):
        self.filter_href = filter_href

    @classmethod
    @abstractmethod
    def _get_post_id(cls, post: Tag) -> str:
        pass

    @classmethod
    @abstractmethod
    def _get_post_url(cls, post: Tag) -> str:
        pass

    @classmethod
    @abstractmethod
    def _get_post_img_url(cls, post: Tag) -> str:
        pass

    @classmethod
    @abstractmethod
    def _get_post_price(cls, post: Tag) -> str:
        pass

    def _get_html(self):
        endpoint = f"{self.BASE_URL}{self.filter_href}"
        scraper = cloudscraper.create_scraper(
            browser={"browser": "firefox", "platform": "windows", "mobile": False}
        )
        html = scraper.get(endpoint).text
        return html

    def get_post_cards(self) -> list[Tag]:
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        return soup.find_all(
            self.POST_CONTAINER_TAG, {"class": self.POST_CONTAINER_CLASS}
        )

    @classmethod
    def _get_ad_info_from_post(cls, post: Tag) -> AptAd:
        ad_url = cls._get_post_url(post)
        ad_price = cls._get_post_price(post)
        ad_img_url = cls._get_post_img_url(post)
        ad_id = cls._get_post_id(post)
        return AptAd(id=ad_id, url=ad_url, price=ad_price, img_url=ad_img_url)

    def get_ads(self):
        post_cards = self.get_post_cards()
        ads = []
        for card in post_cards:
            ads.append(self._get_ad_info_from_post(card))
        return ads


class CabaPropParser(Parser):
    BASE_URL = "https://cabaprop.com.ar"
    POST_CONTAINER_TAG = "div"
    POST_CONTAINER_CLASS = "card-shadow"
    PRICE_CONTAINER_TAG = "div"
    PRICE_CONTAINER_CLASS = "lc-price-normal"

    def _get_html(self):
        endpoint = f"{self.BASE_URL}{self.filter_href}"
        # scraper = cloudscraper.create_scraper(
        #    interpreter="nodejs",
        #    browser={"browser": "firefox", "platform": "windows", "mobile": False},
        # )
        # html = scraper.get(endpoint).text
        response = requests.get(endpoint)
        html = response.content.decode("utf-8")
        return html

    @classmethod
    def _get_post_id(cls, post: Tag) -> str:
        post_url = cls._get_post_url(post)
        match = re.search(r"propiedad/(\w+)/", post_url)
        if match is None:
            raise IdNotFound("ID not found for post {}".format(post_url))
        return match.group(1)

    @classmethod
    def _get_post_img_url(cls, post: Tag) -> str:
        img_tag = post.find_all("img")[0]
        return img_tag.get("src")

    @classmethod
    def _get_post_url(cls, post: Tag) -> str:
        anchor_object = post.find("a")
        if anchor_object is None:
            raise LinkNotFound("Can't find href from post card")
        ad_url = cls.BASE_URL + anchor_object.get("href")
        return ad_url

    @classmethod
    def _get_post_price(cls, post: Tag) -> str:
        footer_object = post.find("div", {"class": "fp_footer"})
        if footer_object is None:
            raise PriceNotFound("Can't find price from post card")
        price_tag = footer_object.find("span", {"class": "lc-price-normal"})
        price_unwanted_chars = ["\n", " ", "expensas"]
        price_value = price_tag.get_text()
        for char in price_unwanted_chars:
            price_value = price_value.replace(char, "")
        return price_value


class ArgenPropParser(Parser):
    BASE_URL = "https://www.argenprop.com"
    POST_CONTAINER_TAG = "div"
    POST_CONTAINER_CLASS = "listing__item"
    PRICE_CONTAINER_TAG = "p"
    PRICE_CONTAINER_CLASS = "card__price"

    @classmethod
    def _get_post_id(cls, post: Tag) -> str:
        return post["id"]

    @classmethod
    def _get_post_img_url(cls, post: Tag) -> str:
        img_tag = post.find_all("img")[0]
        return img_tag.get("src")

    @classmethod
    def _get_post_url(cls, post: Tag) -> str:
        anchor_object = post.find("a")
        if anchor_object is None:
            raise LinkNotFound("Can't find href from post card")
        ad_url = cls.BASE_URL + anchor_object.get("href")
        return ad_url

    @classmethod
    def _get_post_price(cls, post: Tag) -> str:
        price_div = post.find(
            cls.PRICE_CONTAINER_TAG, {"class": cls.PRICE_CONTAINER_CLASS}
        )
        price_unwanted_chars = ["\n", " ", "expensas"]
        price_value = price_div.get_text()
        for char in price_unwanted_chars:
            price_value = price_value.replace(char, "")
        return price_value


class ZonaPropParser(Parser):
    BASE_URL = "https://www.zonaprop.com.ar"
    POST_CONTAINER_TAG = "div"
    POST_CONTAINER_CLASS = "postingsList-module__card-container"
    PRICE_CONTAINER_TAG = "div"
    PRICE_CONTAINER_CLASS = "postingPrices-module__price"

    @classmethod
    def _get_post_id(cls, post: Tag) -> str:
        post_url = cls._get_post_url(post)
        search = re.search(r"-(\w+).html", post_url)
        if search is None:
            raise IdNotFound("ID not found for post {}".format(post_url))
        return search.group(1)

    @classmethod
    def _get_post_img_url(cls, post: Tag) -> str:
        img_tag = post.find_all("img")[0]
        return img_tag.get("src")

    @classmethod
    def _get_post_url(cls, post: Tag) -> str:
        anchor_object = post.find("a")
        if anchor_object is None:
            raise LinkNotFound("Can't find href from post card")
        ad_url = cls.BASE_URL + anchor_object.get("href")
        return ad_url

    @classmethod
    def _get_post_price(cls, post: Tag) -> str:
        price_div = post.find("div", {"class": cls.PRICE_CONTAINER_CLASS})
        price_unwanted_chars = ["\n", " "]
        price_value = price_div.get_text()
        for char in price_unwanted_chars:
            price_value = price_value.replace(char, "")
        return price_value
