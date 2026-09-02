from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from home import views as home_views
from about import views as about_views
from dashboard import views as dashboard_views
from products import views as product_views
from signup import views as signup_views
from products import views as add_prod
urlpatterns = [
    path("admin/", admin.site.urls),

    path('', home_views.home, name="home"),
    path("about/", about_views.about, name="about"),
    path("logout/", signup_views.logout_view, name="logout"),
    path("signup/", signup_views.signup, name="signup"),
    path("products/", product_views.products, name="products"),
    path("", include("products.urls")),

]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )