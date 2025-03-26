import scrapy
from my_scraper.items import ProductDetails
import time
import re
from urllib.parse import urlparse, parse_qs

class MySpider(scrapy.Spider):
    name = "my_spider"
    count = 0
    current_page_amazon, current_page_flipkart = 1, 1
    custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Accept-Encoding': 'gzip, deflate, br'
        }
    
    def __init__(self, query = None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.query = query
        
        self.start_urls = [
            f"https://www.flipkart.com/search?q={self.query}",
            f"https://www.amazon.in/s?k={self.query}",
        ] 
        
        
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"use_selenium": True}, callback=self.parse, headers=self.custom_headers)
    
    def parse(self, response):
        if "flipkart" in response.url:  
            yield from self.parse_flipkart(response)
        elif "amazon" in  response.url:
            yield from self.parse_amazon(response)
        else:
            print("Invalid URL!")

    def parse_flipkart(self, response):
        try:
            product_links = response.css(".CGtC98::attr(href)").getall()
            for link in product_links:
                end_index = link.find("&")
                link = response.urljoin(link[:end_index])
                time.sleep(1)
                yield response.follow(link, callback = self.parse_product_details_page)
                # break   
            if self.current_page_flipkart < 3:
                main_container = response.css(".DOjaWF .gdgoEp")
                next_page = main_container.css("a._9QVEpD:contains('Next')::attr(href)").get()
                if next_page:
                    self.current_page_flipkart += 1 
                    new_url = response.urljoin(next_page) 
                    yield scrapy.Request(url=new_url, callback=self.parse)
                else:
                    print("Next Page Not Found....")
        except Exception as e:
            print(f"Error: {e}")
    
    
    def parse_amazon(self, response):
        try:
            product_containers = response.css(".puis-card-container")
            for product_container in product_containers:
                product_link = product_container.css('a::attr(href)').get()
                end_index = product_link.find("&")
                link = response.urljoin(product_link[:end_index])
                time.sleep(1)
                yield response.follow(link, callback = self.parse_product_details_page)
                # break 
            if self.current_page_amazon < 3:
                amazon_next = response.css("a.s-pagination-next::attr(href)").get()
                if amazon_next:
                    self.current_page_amazon += 1
                    new_url = response.urljoin(amazon_next)
                    yield scrapy.Request(url=new_url, callback=self.parse)
            else:
                print("Next Page Not Found....")
        except Exception as e:
            print(f"Error: {e}")
    
    def parse_product_details_page(self, response):
        self.count += 1
        time.sleep(1)
        # print(f"-------------------------{self.count}------------------------------")
        if "flipkart" in response.url:
            item = ProductDetails()
            try:
                # -------------------------------  BASE URL -------------------------------------
                url = response.url
                item["w_url"] = url[:url.find("/", 8)]
                # print(f"Base URL: {base_url}")
                
                # -------------------------------  product ID -------------------------------------
                keyword = response.url.find("pid=") + 4
                item["p_id"] = (response.url[keyword:])
                # print(f"Product ID: {product_id}")
                
                # -------------------------------  product URL -------------------------------------
                item["p_url"] = response.url
                
                # -------------------------------  product name -------------------------------------
                title = response.css('.VU-ZEz::text').getall()
                item["p_name"] = " ".join(str(item).strip() for item in title)
                # print(f"Title: {title}")
                
                # -------------------------------  product category -------------------------------------
                category_container = response.css("._7dPnhA")
                c_name = category_container.xpath('//div[3]/a/text()').get()
                if c_name is not None:
                    item["c_name"] = c_name
                else:
                    item["c_name"] = self.query
                # print(f"Product Category: {category}")
            
                # -------------------------------  product price -------------------------------------
                price = response.css('.Nx9bqj::text').get()
                item["p_price"] = price[1:]
                item["p_currency"] = price[0:1]
                # print(f"Price: {price}")
                
                # -------------------------------  product images -------------------------------------
                images_url = response.css('._0DkuPH::attr(src)').getall()
                item["p_images"] = [img.replace("/128/128", "/416/416")for img in images_url]
                # print(f"Images: {images}")
                
                # -------------------------------  product ratings -------------------------------------
                p_rating = response.css('.Y1HWO0>.XQDdHH::text').get()
                if p_rating:
                    item["p_rating"] = p_rating
                elif p_rating is None or p_rating is "none":
                    item["p_rating"] = "0"
                else:
                    item["p_rating"] = "0"
                # print(f"Ratings: {ratings}")
                
                # -------------------------------  product availability -------------------------------------
                availability = response.css('.Z8JjpR::text').get()
                if availability == 'Sold Out':
                    item["p_available"] = 0
                    # print(f"Is_Available: No")
                else:
                    item["p_available"] = 1
                    # print(f"Is_Available: Yes")
                    
                # -------------------------------  product color varients -------------------------------------
                # varients = response.css(".E1E-3Z::text").getall()
                # print(f"Varients: {varients}")
                
                # -------------------------------  product specification -------------------------------------
                specification = response.css("._1OjC5I")
                sections = specification.css(".GNDEQ-")
                sec_data = {}
                for section in sections:
                    sec_title = section.css('[class*="_4BJ2V"]::text').get()
                    sec_table = section.css("._0ZhAN9")
                    for table in sec_table:
                        rows = table.css(".WJdYP6")
                        row_data = {}
                        for row in rows:
                            row_title = row.css('[class*="fFi1w"]::text').get()
                            row_desc = row.css('.Izz52n>ul>.HPETK2::text').get()
                            row_data.update({row_title: row_desc})
                    sec_data.update({sec_title: row_data})
                # print(f"Specification: {sec_data}")
                item["p_details"] = sec_data
                
                # -------------------------------  product star-ratings -------------------------------------
                # main_container = response.css(".umNoyb")
                # star_containers = main_container.css(".x2IWCo")
                # if star_containers:
                #     star = []
                #     for star_container in star_containers:
                #         star.append(star_container.css(".Fig8YH::text").get())
                #     # print("out",star)
                #     rating_containers = main_container.css(".BArk-j::text").getall()
                #     # print(rating_containers)
                #     star_ratings = dict(zip(star, rating_containers))
                #     # print(star_ratings)
                # else:
                #     star_ratings = "No ratings on this product..."
                # print(f"Star Ratings: {star_ratings}")
                
                item["w_name"] = "Flipkart"
                
                
                yield item
                
            except Exception as e:
                print(f"Error: {e}")
        
        elif "amazon" in response.url:
            item = ProductDetails()
            try:
                # -------------------------------  BASE URL -------------------------------------
                url = response.url
                item["w_url"] = url[:url.find("/", 8)]
                # print(f"Base URL: {base_url}")
                
                # -------------------------------  product ID -------------------------------------
                link = response.url
                parsed_link = urlparse(url)
                query_parms = parse_qs(parsed_link.query)
                p_id = query_parms.get("crid")
                if p_id:
                    item["p_id"] = p_id
                else:
                    url = response.url
                    asin = url.split("/dp/")[1].split("/")[0]
                    if asin:
                        item["p_id"] = asin
                    else:
                        item["p_id"] = None
                # print(f"Product ID: {product_id}")
                
                # -------------------------------  product URL -------------------------------------
                item["p_url"] = response.url
            
                # -------------------------------  product name -------------------------------------
                p_name = str(response.css(".product-title-word-break::text").get())
                if p_name:
                    item["p_name"] = p_name.strip()
                # print(f"Product Title: {title}")
                
                # -------------------------------  product category -------------------------------------
                if self.query == 'laptop':
                    c_name = response.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[3]/span/a/text()').get()
                    if c_name == 'laptops' or c_name == 'Laptops':
                        item['c_name'] = c_name
                    elif c_name is None or c_name == 'none' or c_name == 'None' or c_name == '':
                        item['c_name'] = 'laptops'
                else:
                    c_name = response.xpath('//*[@id="wayfinding-breadcrumbs_feature_div"]/ul/li[7]/span/a/text()').get()
                    if c_name is None or c_name == 'none':
                        item['c_name'] = self.query
                    else:
                        item['c_name'] = c_name
                # print(f"Product Category: {category}")
            
                # -------------------------------  product price -------------------------------------
                item["p_currency"] = response.css(".a-price-symbol::text").get()
                item["p_price"] = response.css(".a-price-whole::text").get()
                
                # print(f"Price: {price}")
                
                # -------------------------------  product images -------------------------------------
                main_image_container = response.css('.a-fixed-left-grid-col>.regularAltImageViewLayout')
                image_buttons = main_image_container.css('.a-button-thumbnail')
                img = []
                for image_button in image_buttons:
                    image = image_button.css("img::attr(src)").get()
                    if image and '.jpg' in image and not 'PKdp-play-icon-overlay' in image:
                        new_image = image.replace("_SX38_SY50_CR,0,0,38,50_", "_SX679_")
                        img.append(new_image)
                # print(f"Product Images: {img}")
                item["p_images"] = img
                
                # -------------------------------  product ratings -------------------------------------
                ratings_main_container = response.xpath("//div[@id='averageCustomerReviews_feature_div']")
                ratings = str(ratings_main_container.css(".a-popover-trigger>span::text").get())
                # print(f"Ratings: {ratings}")
                if ratings is not None:
                    item["p_rating"] = ratings.strip()
                elif ratings is None or ratings is "none":
                    item["p_rating"] = "0"
                else:
                    item["p_rating"] = "0"
            
                # -------------------------------  product availability -------------------------------------
                availability_container = response.xpath("//div[@id='availability']")
                availability = availability_container.css('span::text').get()
                if availability != ' In stock ':
                    item["p_available"] = 0
                    # print(f"Is_Available: No")
                else:
                    item["p_available"] = 1
                    # print(f"Is_Available: Yes")
                    
                # -------------------------------  product color varients -------------------------------------
                # color_varients = []
                # varients_color_containers = response.css(".image-swatch-button-with-slots")
                # for varients_color_container in varients_color_containers:
                #     color = varients_color_container.css("img::attr('alt')").get()
                #     varients.append(color)
                # varients_size_containers = response.css(".swatch-title-text-container")
                # for varients_size_container in varients_size_containers:
                #     size = (varients_size_container.css("span::text").get()).strip()
                #     varients.append(size)
                # print(f"Varients: {varients}")
                
                # -------------------------------  product specification -------------------------------------
                table_container = response.xpath("//table[@id='productDetails_techSpec_section_1']")
                rows = table_container.css("tr")
                specification = {}
                for row in rows:
                    title = row.css("th::text").get().strip()
                    detail = row.css("td::text").get()
                    detail = detail.replace("\u200e", "").strip() if detail else None
                    specification.update({title:detail})
                # print(f"Specificaiton: {specification}")
                item["p_details"] = specification
                
                item["w_name"] = "Amazon"
                
                yield item
                yield self.count
            except Exception as e:
                print(f"Error: {e}")