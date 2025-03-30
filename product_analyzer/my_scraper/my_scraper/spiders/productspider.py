import scrapy
from my_scraper.items import ProductDetails
from user.models import products
from urllib.parse import urlparse, parse_qs
from asgiref.sync import sync_to_async

class ProductSpider(scrapy.Spider):
    name="productSpider"
    custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Accept-Encoding': 'gzip, deflate, br'
        }
    
    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.start_url = list(products.objects.values_list("product_url", flat=True))
    
    def start_requests(self):
        for url in self.start_url:
            print(f"Scrapping For the given URL: {url}")
            yield scrapy.Request(url, meta={"use_selenium": True}, callback=self.parse, headers=self.custom_headers)
            # break
            
    def parse(self, response):
        if "flipkart" in response.url:
            yield from self.parse_flipkart(response)
        elif "amazon" in  response.url:
            yield from self.parse_amazon(response)
        else:
            print("Invalid URL!")
    
    def parse_flipkart(self, response):
        item = ProductDetails()
        try:
            # -------------------------------  product ID -------------------------------------
            keyword = response.url.find("pid=") + 4
            item["p_id"] = (response.url[keyword:]) if keyword != 3 else "Unknown"  
            # print(f"Product ID: {product_id}")
            
            # -------------------------------  product price -------------------------------------
            price = response.css('.Nx9bqj::text').get()
            if price:
                item["p_price"] = price[1:] if len(price) > 1 else "Unknown"
                item["p_currency"] = price[0:1]
            else:
                item["p_price"] = "Unknown"
                item["p_currency"] = "Unknown"
            # print(f"Price: {price}")
            
            # -------------------------------  product availability -------------------------------------
            availability = response.css('.Z8JjpR::text').get()
            item["p_available"] = 0 if availability == "Sold Out" else 1
                # print(f"Is_Available: Yes")
                
            # -------------------------------  product ratings -------------------------------------
            p_rating = response.css('.Y1HWO0>.XQDdHH::text').get()
            item["p_rating"] = p_rating if p_rating else "0"
            # print(f"Ratings: {ratings}")
            
            yield item
        except Exception as e:
            print(f'Error: {e}')
            
    def parse_amazon(self, response):
        item = ProductDetails()
        try:
            # -------------------------------  product ID -------------------------------------
            parsed_link = urlparse(response.url)
            query_parms = parse_qs(parsed_link.query)
            p_id = query_parms.get("crid", [None])[0]
            if not p_id:
                try:
                    asin = response.url.split("/dp/")[1].split("/")[0]
                    item["p_id"] = asin if asin else None
                except IndexError:
                    item["p_id"] = None
            else:
                item["p_id"] = p_id
            # print(f"Product ID: {product_id}")
            
            # -------------------------------  product price -------------------------------------
            price = response.css(".a-price-whole::text").get()
            item["p_price"] = price if price else "Unknown"
            
            currency = response.css(".a-price-symbol::text").get()
            item["p_currency"] = currency if currency else "Unknown"
                
                # print(f"Price: {price}")
            
            # -------------------------------  product ratings -------------------------------------
            ratings_main_container = response.xpath("//div[@id='averageCustomerReviews_feature_div']")
            ratings = str(ratings_main_container.css(".a-popover-trigger>span::text").get())
            # print(f"Ratings: {ratings}")
            item["p_rating"] = ratings if ratings else "0"
            
            # -------------------------------  product availability -------------------------------------
            availability_container = response.xpath("//div[@id='availability']")
            availability = availability_container.css('span::text').get()
            if availability and "In Stock" in availability:
                item["p_available"] = 1
            else:
                item["p_available"] = 0
            
            yield item
        except Exception as e:
            print(f'Error: {e}')