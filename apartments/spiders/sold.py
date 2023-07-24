import scrapy
import urllib.parse
from datetime import datetime
import re


class SoldApartmentsScraper(scrapy.Spider):
    name = "sold"

    def __init__(self, address = 'Prinsessegade', zipcodeFrom = 1050, zipcodeTo = 1472, *args, **kwargs):
        super(SoldApartmentsScraper, self).__init__(*args, **kwargs)
        # build query params
        self.params = {
            "street": address,
            "zipcodeFrom": zipcodeFrom,
            "zipcodeTo": zipcodeTo,
            "sort": "date-d",
            "propertyType": 3,
            "searchTab": 1,
            "page": 1
        }
        self.start_urls = [
            f"https://www.boliga.dk/salg/resultater?{urllib.parse.urlencode(self.params)}"
        ]

    def parse(self, response):
        keys = [
            'type_short',
            'type',
            'address',
            'city',
            'price',
            'sales_date',
            'sales_type',
            'sqm',
            'sqm_price',
            'rooms',
            'build_year',
            'price_change',
            'actual_price',
        ]
        int_keys = { 'price', 'sqm', 'sqm_price' 'rooms', 'build_year', 'price_change' }

        for row in response.css('tbody > tr'):
            vals = sum(
                [col.css('span::text, a::text').getall() or ['0%'] for col in row.css('td')],
                []
            )
            
            def fix_val(val, key):
                val = val.strip()
                if key in int_keys:
                    # remove all non-digits but preserve the minus sign
                    return re.sub(r'[^-\d]', '', val)
                else:
                    return val.replace('.', '')
                
            vals = [fix_val(val, key) for val, key in zip(vals, keys)]
            assert len(keys) == len(vals)
            yield dict(zip(keys, vals))

        disabled_next_page = response.css('app-pagination > div > div.nav-right > a.disabled')
        if not disabled_next_page:
            # construct next url by adding 1 to the page query param
            self.params['page'] += 1
            next_page = f"https://www.boliga.dk/salg/resultater?{urllib.parse.urlencode(self.params)}"
            yield scrapy.Request(next_page, callback=self.parse)

            