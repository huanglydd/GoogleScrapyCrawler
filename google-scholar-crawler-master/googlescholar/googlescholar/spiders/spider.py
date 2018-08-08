import re
import ast
import json
from urlparse import urlparse
import urllib
import pdb
import scrapy


from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from scrapy.http import Request
from scrapy.utils.project import get_project_settings

from googlescholar.items import *
from misc.log import *
from misc.spider import CommonSpider


def _monkey_patching_HTTPClientParser_statusReceived():
    """
    monkey patching for scrapy.xlib.tx._newclient.HTTPClientParser.statusReceived
    """
    from twisted.web._newclient import HTTPClientParser, ParseError
    old_sr = HTTPClientParser.statusReceived

    def statusReceived(self, status):
        try:
            return old_sr(self, status)
        except ParseError, e:
            if e.args[0] == 'wrong number of parts':
                return old_sr(self, status + ' OK')
            raise
    statusReceived.__doc__ == old_sr.__doc__
    HTTPClientParser.statusReceived = statusReceived


class googlescholarSpider(CommonSpider):
    name = "googlescholar"
    allowed_domains = ["google.com"]
    start_urls = [
        "https://scholar.google.com/scholar?hl=en&as_sdt=1%2C5&as_vis=1&q=intitle%3Ainfomation+intitle%3Apharmacovigilance&btnG="
        #"http://scholar.google.com/scholar?as_ylo=2011&q=machine+learning&hl=en&as_sdt=0,5",
        #"http://scholar.google.com/scholar?q=estimate+ctr&btnG=&hl=en&as_sdt=0%2C5&as_ylo=2011",
        #"http://scholar.google.com",
    ]
    #rules = [
    #    Rule(sle(allow=("scholar\?.*")), callback='parse_1', follow=False),
    #    Rule(sle(allow=(".*\.pdf"))),
    #]
    page_start = 0

    def __init__(self, start_url='', *args, **kwargs):
        _monkey_patching_HTTPClientParser_statusReceived()
        #if start_url:
        #    self.start_urls = [start_url]
        super(googlescholarSpider, self).__init__(*args, **kwargs)

    #.gs_ri: content besides related html/pdf
    list_css_rules = {
        ".gs_r": {
            "title": ".gs_rt a *::text",
            "url": ".gs_rt a::attr(href)",
            "related-text": ".gs_ggsS::text",
            "related-type": ".gs_ggsS .gs_ctg2::text",
            "related-url": ".gs_ggs a::attr(href)",
            "citation-text": ".gs_fl > a:nth-child(1)::text",
            "citation-url": ".gs_fl > a:nth-child(1)::attr(href)",
            "authors": ".gs_a a::text",
            "description": ".gs_rs *::text",
            "journal-year-src": ".gs_a::text",
        }
    }

    def start_requests(self):
        print(self.start_urls)
        for url in self.start_urls:
            _monkey_patching_HTTPClientParser_statusReceived()
            yield Request(url, callback=self.parse_1, dont_filter=True)

    def save_pdf(self, response):
        path = self.get_path(response.url)
        info(path)
        with open(path, "wb") as f:
            f.write(response.body)

    def parse_paper(self, item):
        local_item = googlescholarItem()
        #print(item)
        content = item
        #print("content")
        local_item['title'] = content['title']
        local_item['url'] = content['url']
        local_item['related_text'] = content['related-text']
        local_item['related_type'] = content['related-type']
        local_item['related_url'] = content['related-url']
        local_item['citation_text'] = content['citation-text']
        local_item['citation_url'] = content['citation-url']
        local_item['authors'] = content['authors']
        local_item['description'] = content['description']
        local_item['journal_year_src'] = content['journal-year-src']
        return local_item

    def parse_1(self, response):
        #return
        info('Parse '+response.url)
        #sel = Selector(response)
        #v = sel.css('.gs_ggs a::attr(href)').extract()
        #import pdb; pdb.set_trace()
        x = self.parse_with_rules(response, self.list_css_rules, dict)
        items = []
        print("******************************************** x[0]['.gs_r']:\n {}\n".format(x[0]['.gs_r']))
        if x[0]['.gs_r']:
            items = x[0]['.gs_r']
            #print(items)
            #pp.pprint(items)
        elif not x[0]['.gs_r']:
            print("Condition Return")
            return
        #import pdb; pdb.set_trace()
        # return self.parse_with_rules(response, self.css_rules, googlescholarItem)
        """
        for item in items:
            if item['related-url'] == '' or item['related-type'] != '[PDF]':
                continue
            url = item['related-url']
            info('pdf-url: ' + url)
            yield Request(url, callback=self.save_pdf)
        """
        # Return value to pipeline.
        for item in items:
            yield self.parse_paper(item)

        self.page_start = self.page_start + 10
        url = "https://scholar.google.com/scholar?start={}&hl=en&as_sdt=1%2C5&as_vis=1&q=intitle%3Atwitter+intitle%3Apharmacovigilance&btnG=".format(str(self.page_start))
        #url = "https://scholar.google.com/scholar?start=10&hl=en&as_sdt=1%2C5&as_vis=1&q=intitle%3Atwitter+intitle%3Apharmacovigilance&btnG="

        time.sleep(5)

        #return

        yield Request(url, callback=self.parse_1, dont_filter=True)



