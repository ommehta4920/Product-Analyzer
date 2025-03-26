from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse
from rest_framework.views import APIView
from .models import *
from django.contrib import messages
import subprocess
import os
import logging

class HomePage(APIView):
    def get(self, request):
        return render(request, "home.html")
    
class CategoryPage(APIView):
    def get(self, request):
        category = categories.objects.all()
        return render(request, "categories.html", {"categories": category})

class ProductListPage(APIView):
    def get(self, request, c_id):
        category = get_object_or_404(categories, category_id=c_id)
        products_list = products.objects.filter(category_id_id = category.category_id)
        return render(request, "products_list.html", {"products": products_list, "category": category})
    
class ProductDetailsPage(APIView):
    def get(self, request, c_id, p_id):
        # Fetching Product and Category data
        category = get_object_or_404(categories, category_id = c_id)
        c_name = category.category_name[:-1]
        product_data = get_object_or_404(products, product_id = p_id)
        
        # Fetching Latest Price 
        p_price = product_data.product_price
        if p_price:
            last_date = max(p_price.keys())  # Get the last date
            last_price = p_price[last_date]  # Get the price for the last date
        else:
            last_price = "N/A"
            
        # Fetching Data to display in the graphs
        labels = sorted(p_price.keys())
        values = (p_price[date] for date in labels)     
        context = {"chartLabels": labels, "chartValues": [int(value.replace(',', '')) for value in values], "c_name": c_name, "product_data": product_data, "last_price": last_price, "category": category}
        return render(request, "product_detail.html", context)
        
       
class ProductComparisonPage(APIView):
    def get(self, request, c_id = None):
        category_data = categories.objects.all()
        if c_id:
            logger = logging.getLogger(__name__)
            logger.debug(f"Category ID received: {c_id}")
            try:
                categoryData = categories.objects.get(category_id = c_id)
                product_data = products.objects.filter(category_id=categoryData.category_id)
                print(f"Category ID: {c_id}, Products Found: {product_data.count()}")

                if not product_data.exists():  # Ensure products exist
                    return JsonResponse({'products_detail': [], 'message': 'No products found'})
                product_list = [{'product_id': p.product_id, 'product_name': p.product_name, 'product_price': p.product_price, 'product_rating': p.product_ratings, 'product_image': p.product_image_url[0], 'product_details': p.product_details} for p in product_data]
                # print(product_list)
                return JsonResponse({'products_detail': product_list})
            except categories.DoesNotExist:
                return HttpResponseNotFound(JsonResponse({'error': 'category not found.'}))
        return render(request, "product_comparison.html", { "category_data": category_data, 'products_detail': []})

class ScraperPage(APIView):
    def get(self,request):
        return render(request, "search.html")
    
    def post(self, request):
        query = request.POST.get("query", "").strip()
        
        if not query:
            messages.error(request, "Please Provide Input")
            return redirect("/scraper")
        
        project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../my_scraper")

        # Set environment variables for Django
        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "product_analyzer.settings"
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            subprocess.run(["scrapy", "crawl", "my_spider", "-a", f"query={query}"], cwd=project_path, env=env, check=True)
            messages.success(request, f"Scraping started for: {query}")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Scrapy encountered an error: {e}")
        return redirect("/scraper")
        
class SignInPage(APIView):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        passwd = request.POST.get('password')
        try: 
            user = user_details.objects.get(user_email = email)
            if user.user_passwd == passwd:
                request.session["user_id"] = user.user_id
                messages.success(request, "Login Successful, Welcome Back!")
                return redirect('/profile')
            else:
                messages.error(request, "Invalid username or password.")
        except:
            messages.error(request, "Invalid!")
        return render(request, 'login.html')
        
class SignUpPage(APIView):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        username = request.POST["fullname"]
        email = request.POST["email"]
        password = request.POST["confirm-password"]
        print(username, email, password)
        if user_details.objects.filter(user_email = email).exists():
            messages.error(request, "Email already registered!")
            return redirect("/signup")
        
        user = user_details(user_name = username, user_email = email, user_passwd = password)
        user.save()
        return redirect("/signin")
    
class ProfilePage(APIView):
    def get(self, request):
        userid = request.session.get("user_id")
        if not userid:
            return redirect("/signin")
        else:
            user_data = user_details.objects.get(user_id = userid)
        
        return render(request, 'profile.html', {"user_data": user_data})

    def post(self, request):
        user_id = request.session.get("user_id")

        if not user_id:
            return redirect("/signin")

        # Get updated data from form
        name = request.POST.get("name")
        email = request.POST.get("email")

        # Update user details in the database
        user = user_details.objects.get(user_id=user_id)
        user.user_name = name
        user.user_email = email
        user.save()

        # Update session with new data
        request.session["user_name"] = name
        request.session["user_email"] = email

        messages.success(request, "Profile updated successfully!")
        return redirect("/profile")

def logout_user(request):
    request.session.flush()
    return redirect("/")