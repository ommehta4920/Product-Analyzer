from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from rest_framework.views import APIView
from .models import *
from django.contrib import messages
import logging
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import update_session_auth_hash, logout
from django.views import View
from .models import user_details
from .models import products
# from .services import trackPrice

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
    
    def post(self, request, c_id, p_id):
        category = get_object_or_404(categories, category_id=c_id)
        c_name = category.category_name[:-1]
        product_data = get_object_or_404(products, product_id=p_id)
        
        userId = request.session.get("user_id")
        if not userId:
            return JsonResponse({"error": "User not authenticated"}, status=403)
        
        user = get_object_or_404(user_details, user_id=userId)
        
        # Fetching Latest Price 
        p_price = product_data.product_price
        if p_price:
            last_date = max(p_price.keys())  # Get the last date
            last_price = p_price[last_date]  # Get the price for the last date
        else:
            last_price = "N/A"

        # Get user input for desired price
        desired_price = request.POST.get("desiredPrice")

        if not desired_price:
            return JsonResponse({"error": "Desired price is required"}, status=400)
        
        existing_tracking = price_track.objects.filter(
            user_id = user,
            product_id = product_data,
            desired_price = desired_price,
            tracking_status = '1'
        ).exists()
        
        if existing_tracking:
            messages.error(request, "You have already placed a tracking for this product with the same price.")
            # return message
        else:
            tracking_entry = price_track.objects.create(
                user_id= user,  # Retrieved from session
                product_id=product_data,
                category_id=category,
                desired_price=desired_price,
                last_price=last_price,
                tracking_status='1'  # Active
            )
            
            tracking_entry.save()
            messages.success(request, 'Price tracking has been successfully saved!')
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
        
class SignInPage(APIView):
    def get(self, request):
        return render(request, "signin.html")
    
    def post(self, request):
        user_email = request.POST["user_email"]
        user_passwd = request.POST["user_passwd"]
        print("**********", user_email, "\n-*-*-*-", user_passwd)
        if user_details.objects.filter(user_email=user_email, user_passwd=user_passwd).exists():
            try:
                user_data = get_object_or_404(user_details, user_email=user_email)
                request.session["user_id"] = user_data.user_id
                print("User Details :- ", user_data)

                # messages.success(request, "Welcome "+ user_data.user_name)
                messages.success(request, "Login Successful, Welcome Back!")
                return redirect('/profile')
            except:
                print("--------", sys.exc_info())
        else:
            print("---------->>> Your Email or Password is incorrect!")
            messages.error(request, "Your Email isn't registered or Password is incorrect!")
            messages.info(request, "Please try again..")
            return render(request, "signin.html", {"user_email": user_email})

class SignUpPage(APIView):
    def get(self, request):
        return render(request, "signup.html")

    def post(self, request):
        user_name = request.POST["user_name"]
        user_email = request.POST["user_email"]
        user_passwd = request.POST["user_passwd"]
        user_c_passwd = request.POST["user_c_passwd"]
        # created_at = timezone.now()

        print(f" user_name : {user_name} \n user_email : {user_email} \n user_passwd : {user_passwd} \n user_c_passwd : {user_c_passwd}")

        if user_details.objects.filter(user_email=user_email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "signup.html", {"user_name": user_name, "user_passwd": user_passwd, "user_c_passwd": user_c_passwd})

        if user_passwd != user_c_passwd:
            print("-------- Both password must be same..! --------")
            messages.info(request, "Both password must be same..!")
            return render(request, "signup.html", {"user_name": user_name, "user_email": user_email})

        user = user_details(user_name=user_name, user_email=user_email, user_passwd=user_passwd)

        try:
            user.save()
            messages.success(request, "You are successfully registered...")
            return render(request, "signin.html", {})

        except:
            print("---------", sys.exc_info())
    
class ForgotPage(APIView):
    def get(self, request):
        return render(request, "forgot.html")

    def post(self, request):
        user_otp = request.POST["user_otp"]
        user_passwd = request.POST["user_passwd"]
        user_c_passwd = request.POST["user_c_passwd"]
        user_email = request.POST["login_user_email"]
        # user_email = 'ommehta4920@gmail.com'

        print("**********", user_otp, "\n-*-*-*-", user_passwd, "\n-*-*-*-", user_c_passwd, "\n-*-*-*-", user_email)

        if user_details.objects.filter(user_email=user_email, user_otp=user_otp).exists():

            if user_passwd != user_c_passwd:
                print("-------- Both password must be same..! --------")
                messages.info(request, "Both password must be same..!")

                return render(request, "forgot.html", {"visibility": True, "user_otp": user_otp, "email": user_email})

            try:
                user = user_details.objects.filter(user_email=user_email, user_otp=user_otp)
                user.update(user_passwd=user_passwd)

                print("<<--------- Password has been successfully reset... ---------->>")
                messages.success(request, "Password has been successfully reset...")

                return redirect("/signin")

            except:
                print("--------", sys.exc_info())

        else:
            print("-------- OTP is incorrect! --------")
            messages.error(request, "OTP is incorrect!")

        return render(request, "forgot.html", {"visibility": True, "email": user_email, "user_passwd": user_passwd, "user_c_passwd": user_c_passwd})

class Send_otpPage(APIView):
    def get(self):
        return redirect("/forgot")

    def post(self, request):
        otp = random.randint(1000, 9999)
        user_email = request.POST["user_email"]

        # request.session['temail'] = user_email
        #
        # print("Session temail :", request.session['temail'])

        if user_details.objects.filter(user_email=user_email).exists():

            try:
                user = user_details.objects.filter(user_email=user_email)
                user.update(user_otp=str(otp))

                subject = "Your Product Analyzer Portal OTP"
                message = "Dear user, you want to reset your password of your Product Analyzer account. \n\n Use OTP: " + str(otp) + "\n\nNote: Do not share the OTP with anyone else."
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user_email, ]

                send_mail(subject, message, email_from, recipient_list)

                print("**********", subject, "\n-*-*-*-", message, "\n-*-*-*-", email_from, "\n-*-*-*-", recipient_list)

                messages.info(request, "OTP has been sent to your registered email..!")

                return render(request, "forgot.html", {"visibility": True, "email": user_email})

            except:
                print("---------", sys.exc_info())
                return render(request, "forgot.html", {})

        else:
            messages.error(request, "Email is not registered!")
            return render(request, "forgot.html", {})
    
class ProfilePage(View):
    def get(self, request):
        userid = request.session.get("user_id")
        if not userid:
            return redirect("/signin")

        user_data = user_details.objects.get(user_id=userid)

        response = render(request, 'profile.html', {"user_data": user_data})
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def post(self, request):
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("/signin")

        user = user_details.objects.get(user_id=user_id)

        # Check if password change request
        if "current_password" in request.POST:
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            # Check if the current password is correct
            if  current_password !=user.user_passwd:
                messages.error(request, "Current password is incorrect.")
                return redirect("/profile")

            # Ensure new passwords match
            if new_password != confirm_password:
                messages.error(request, "New password and Confirm password do not match.")
                return redirect("/profile")

            # Hash and update the new password
            user.user_passwd = new_password
            user.save()

            # Ensure user stays logged in after password change
            update_session_auth_hash(request, user)

            messages.success(request, "Your password has been successfully updated.")
            return redirect("/profile")

        # Otherwise, update profile details
        name = request.POST.get("name")
        email = request.POST.get("email")

        user.user_name = name
        user.user_email = email
        user.save()

        # Update session with new data
        request.session["user_name"] = name
        request.session["user_email"] = email

        messages.success(request, "Profile updated successfully!")
        return redirect("/profile")

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect('/signin')
    response.delete_cookie('sessionid')
    return response

class AboutUs(APIView):
    def get(self, request):
        return render(request, "aboutus.html")
    
def search_suggestions(request):
    query = request.GET.get("query", "").strip()
    if query:
        product_results = products.objects.filter(product_name__icontains=query)[:5]
        suggestions = [product.product_name for product in product_results]
    else:
        suggestions = []
    
    return JsonResponse(suggestions, safe=False)

def product_list(request):
    query = request.GET.get("query", "").strip()  # Get search query
    filtered_products = products.objects.filter(product_name__icontains=query) if query else products.objects.all()

    return render(request, "products.html", {"products": filtered_products, "query": query})

def search_results(request):
    query = request.GET.get('query', '').strip()
    
    if query:
        products_list = products.objects.filter(product_name__icontains=query)

        # Filter out products that don't have a valid category_id
        products_list = [p for p in products_list if p.category_id]
    else:   
        products_list = []

    return render(request, 'products_list.html', {
        'products': products_list,
        'query': query,
    })
    


