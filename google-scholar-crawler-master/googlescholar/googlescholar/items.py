# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class googlescholarItem(scrapy.Item):
    # define the fields for your item here like:
    title = Field()
    url = Field()
    related_text = Field()
    related_type =Field()
    related_url =Field()
    citation_text =Field()
    citation_url =Field()
    authors =Field()
    description =Field()
    journal_year_src = Field()
