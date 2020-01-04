import os
import re
import json
import scrapy


class TuttiSpider(scrapy.Spider):
    name = "tutti"

    def __init__(self, searchterm="", pages=1, **kwargs):
        super().__init__(**kwargs)
        self.searchterm = searchterm
        self.pages = int(pages)

    def start_requests(self):
        for page in range(1, self.pages + 1):
            yield scrapy.Request(
                callback=self.parse,
                dont_filter=True,
                url=f"https://www.tutti.ch/de/li/ganze-schweiz?o={page}&q={self.searchterm}",
            )

    def transform_raw(self, data):
        return {
            "id": data["id"],
            "subject": data.get("subject"),
            "body": data.get("body"),
            "price": data.get("price"),
            "time": data.get("epoch_time"),
            "region": data.get("location_info", {}).get("region_name"),
            "plz": data.get("location_info", {}).get("plz"),
            "link": f"https://www.tutti.ch/vi/{data['id']}",
            "thumbnail": f"https://c.tutti.ch/images/{data.get('thumb_name')}",
            "images": [
                f"https://c.tutti.ch/images/{image}"
                for image in data.get("image_names", [])
            ],
            "_meta": data,
        }

    def parse(self, response):
        pattern = re.compile(r"window.__INITIAL_STATE__=(.*)", re.MULTILINE | re.DOTALL)

        data = response.xpath('//script[contains(., "INITIAL_STATE")]/text()').re(
            pattern
        )[0]

        offers = json.loads(data)["items"]

        for _, offer in offers.items():
            yield self.transform_raw(offer)