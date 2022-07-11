import scrapy
from datetime import date
import re

class GamesSpider(scrapy.Spider):
    name = 'boardgames'
    
    def start_requests(self):
        yield scrapy.Request('https://boardgamegeek.com/browse/boardgame/page/1')

    def parse(self, response):
        base_url = 'https://boardgamegeek.com'
        for game in response.css('#row_'):
            id = int(game.css("#row_ a::attr(href)").re("\d+")[0])
            rank = game.css(
                ".collection_rank a::attr(name)").get()
            name = game.css(".primary ::text").get()
            url = base_url + game.css("#row_ a::attr(href)").get()
            rating = game.css(
                "#row_ .collection_bggrating:nth-child(5)::text").get().split()[0]
            try:
                num_voters = int(game.css(
                    "td.collection_bggrating ::text")[2].get().replace("\n", "").replace("\t", ""))
            except:
                num_voters = 'N/A'
            try:
                year_published = int(game.css(
                    "span.smallerfont.dull ::text").get()[1:-1])
            except:
                year_published = 'N/A'
            try:
                description = game.css(
                    "p.smallefont.dull ::text").get().replace("\n", "").replace("\t", "")
            except:
                description = 'N/A'
            current_date = date.today()

            yield {
                'id': id,
                'rank': rank,
                'name': name,
                'url': url,
                'rating': rating,
                'num_voters': num_voters,
                'year_published': year_published,
                'description': description,
                'date': current_date
            }

        next_page = response.css('a[title="next page"] ::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

class GamesPricesSpider(scrapy.Spider):
    name = 'gamesprices'
    start_urls = [
        'https://www.ludonauta.es/tiendas/listar/page:1']

    def start_requests(self):
        stores = ['espacio-de-juegos', 'mathom', 'jugamos-otra', 'jugarxjugar']
        for store in stores:
            yield scrapy.Request(f'https://www.ludonauta.es/juegos-mesas-tiendas/listar-por-tienda/{store}',
                                 self.parse)

    def parse(self, response):
        players = re.compile(r"\d+-*\d*")
        base_url = 'https://www.ludonauta.es/'
        for row in response.xpath('//*[@class="table table-bordered table-striped"]//tbody/tr'):
            url = row.css(".p-t-xs.p-b-xs a::attr(href)").get()
            yield response.follow(url, callback=self.parse_games)

        next_page = response.css('a[rel="next"]').attrib["href"]
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_games(self, response):
        url = response.request.url
        store = re.search(r'(?<=https://).\w{4,}|(?<=https://www.).\w{4,}', url).group()
        current_date = date.today()
        print("Store: ", store)
        if store == 'mathom':
            name = response.css('div[id="short_description_content"] ::text').get()
            price = float(response.css('span[id="our_price_display"] ::text').get().replace(' €', '').replace(',', '.'))
            bgg_url = response.css('div.pa_content ::attr(href)').get()
            id_compile = re.compile(r'\d+')
            id = int(re.search(id_compile, bgg_url).group())
            availability = 'En stock'
            yield {
                'id': id,
                'store': store,
                'name': name,
                'price': price,
                'bgg_url': bgg_url,
                'url': url,
                'availability': availability,
                'date': current_date
            }
        if store == 'espaciodejuegos':
            name = response.css('h1.product_title.entry-title.elementor-heading-title.elementor-size-large ::text').get()
            price = float(response.css('span.woocommerce-Price-amount.amount ::text')[2].get().replace(',','.'))
            availability = response.css('span.stock.in-stock ::text').get()
            bgg_url = response.css('div.woocommerce-Tabs-panel.woocommerce-Tabs-panel--description.panel.entry-content.wc-tab ::attr(href)').get()
            id_compile = re.compile(r'\d+')
            id = int(re.search(id_compile, bgg_url).group())
            yield {
                'id': id,
                'store': store,
                'name': name,
                'price': price,
                'bgg_url': bgg_url,
                'url': url,
                'availability': availability,
                'date': current_date
            }
        if store == 'jugarxjugar':
            name = response.css('h1.page-title ::text').get().replace('\n','').replace('\t','')
            price = float(response.css('div.current-price ::text')[1].get().replace('\xa0€', '').replace(',','.'))
            availability = response.css('span[id="product-availability"] ::text').get().replace('\n', '').replace('\t','').strip()
            bgg_url = response.css('div.product-description ::attr(href)').get()
            id_compile = re.compile(r'\d+')
            id = int(re.search(id_compile, bgg_url).group())
            yield {
                'id': id,
                'store': store,
                'name': name,
                'price': price,
                'bgg_url': bgg_url,
                'url': url,
                'availability': availability,
                'date': current_date
            }
        if store == 'jugamosotra':
            name = response.css('h1.h1 ::text').get()
            price = float(response.css('div.current-price ::text')[1].get().replace('\xa0€', '').replace(',','.'))
            availability = response.css('span[id="product-availability"] ::text')[-1].get().replace('\n','').split('.')[0].strip()
            bgg_url = response.css('div.tab-content ::attr(href)').get()
            id_compile = re.compile(r'\d+')
            id = int(re.search(id_compile, bgg_url).group())
            yield {
                'id': id,
                'store': store,
                'name': name,
                'price': price,
                'bgg_url': bgg_url,
                'url': url,
                'availability': availability,
                'date': current_date
            }