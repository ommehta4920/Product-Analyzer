from django.db import models

# Stores user details
class user_details(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_email = models.EmailField(max_length=100, unique=True)
    user_passwd = models.CharField(max_length=20, null=False)
    user_name = models.CharField(max_length=50, null=False)
    
    def __str__(self):
        return f"{self.user_email} - {self.user_name}"

# Stores website details which are going to be scraped
class website_details(models.Model):
    website_id = models.AutoField(primary_key=True)
    website_name = models.CharField(max_length=100, null=False)
    base_url = models.URLField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.website_name} - {self.base_url}"
    
# Stores product categories
class categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, null=False)
    category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.category_id} {self.category_name}"

# Stores product details
class products(models.Model):
    product_id = models.CharField(primary_key=True, max_length=550)
    website_id = models.ForeignKey(website_details, on_delete=models.CASCADE)
    category_id = models.ForeignKey(categories, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=500, null=False)
    product_price = models.JSONField(null=False)
    product_ratings = models.FloatField(default=dict, null=False)
    currency = models.CharField(max_length=10, null=False)
    product_details = models.JSONField(null=True)
    is_available = models.BooleanField(default=True)
    product_url = models.URLField(max_length=500, null=False)
    product_image_url = models.JSONField(default=dict, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.product_price} - {self.product_url}"
    
# Stores user's search requests
class user_request(models.Model):
    request_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(user_details, on_delete=models.CASCADE)
    category_id = models.ForeignKey(categories, on_delete=models.CASCADE)
    request_name = models.CharField(max_length=255, null=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request_name}"
    
# Stores search requests' result
class request_result(models.Model):
    result_id = models.BigAutoField(primary_key=True)
    request_id = models.ForeignKey(user_request, on_delete=models.CASCADE)
    product_id = models.ForeignKey(products, on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)
    
# Stores the price tracking requests
class price_track(models.Model):
    track_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(user_details, on_delete=models.CASCADE)
    product_id = models.ForeignKey(products, on_delete=models.CASCADE)
    category_id = models.ForeignKey(categories, on_delete=models.CASCADE)
    desired_price = models.DecimalField(max_digits=19, decimal_places=2, null=False)
    last_price = models.DecimalField(max_digits=19, decimal_places=2, null=False)
    status = {
        '1': 'Active',
        '2': 'Completed',
        '3': 'Cancelled',
    }
    tracking_status = models.CharField(max_length=1, choices=status)

