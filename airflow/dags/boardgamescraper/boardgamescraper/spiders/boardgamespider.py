import scrapy
from datetime import date

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