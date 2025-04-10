from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home-page'),
    path('category/', CategoryPage.as_view(), name='categories-page'),
    path('category/<int:c_id>/', ProductListPage.as_view(), name='products-list-page'),
    path('category/<int:c_id>/<str:p_id>/', ProductDetailsPage.as_view(), name='product-detail-page'),
    path('comparison/', ProductComparisonPage.as_view(), name='product-comparison-page'),
    path('comparison/<int:c_id>', ProductComparisonPage.as_view(), name='product-comparison-page-with-id'),
    path('comparison/<int:c_id>/<str:p_id>/', ProductComparisonPage.as_view(), name='product-comparison-page'),
    path('signin/', SignInPage.as_view(), name='signin-page'),
    path('signup/', SignUpPage.as_view(), name='signup-page'),
    path('profile/', ProfilePage.as_view(), name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('aboutus/', AboutUs.as_view(), name='aboutus'),
    path("search-suggestions/", search_suggestions, name="search-suggestions"),
    path('products/', product_list, name='product-list'),
    path("search-results/", search_results, name="search-results"),
    path('forgot/', ForgotPage.as_view(), name='forgot-page'),
    path('send_otp/', Send_otpPage.as_view(), name='send_otp-page'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)