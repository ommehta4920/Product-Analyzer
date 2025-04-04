from celery import shared_task
import subprocess
import os
from .models import categories

@shared_task(bind=True)
def categoryScrapper(self):
    categoryNames = categories.objects.values_list('category_name', flat=True)
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../my_scraper")
    if not categoryNames:
        print("No Categories found in the database!")
    else:
        for categoryName in categoryNames:
            print(f"Scrapping data for Category: {categoryName}")
            subprocess.run(["scrapy", "crawl", "my_spider", "-a", f"query={categoryName}"], cwd=project_path)
    return "Category-Scrapping Done"

@shared_task(bind=True)
def productScrapper(self):
    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../my_scraper")
    subprocess.run(["scrapy", "crawl", "productSpider"], cwd=project_path)
    return "Product-Scrapping Done"

