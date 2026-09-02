from django.urls import path
from . import views
from signup import views as signup_views


urlpatterns = [

    # =====================================================
    # CUSTOMER AUTHENTICATION
    # =====================================================

    path(
        "login/",
        signup_views.login_view,
        name="login"
    ),

    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),


    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # =====================================================
    # PRODUCTS
    # =====================================================

    path(
        "products/",
        views.products,
        name="products"
    ),

    path(
        "add-product/",
        views.add_product,
        name="add_product"
    ),


    # =====================================================
    # CART
    # =====================================================

    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/increase/<int:product_id>/",
        views.increase_quantity,
        name="increase_quantity"
    ),

    path(
        "cart/decrease/<int:product_id>/",
        views.decrease_quantity,
        name="decrease_quantity"
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),


    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),


    # =====================================================
    # CUSTOMER ORDERS
    # =====================================================

    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    path(
        "order-summary/",
        views.order_summary,
        name="order_summary"
    ),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    path(
        "cancel-order/<int:order_id>/",
        views.cancel_order,
        name="cancel_order"
    ),

    path(
        "return-order/<int:order_id>/",
        views.return_order,
        name="return_order"
    ),


    # =====================================================
    # ADMIN CUSTOMER ORDERS
    # =====================================================

    path(
        "admin/customer/<int:customer_id>/orders/",
        views.admin_customer_orders,
        name="admin_customer_orders"
    ),

    path(
        "customer-orders/<int:customer_id>/",
        views.customer_orders,
        name="customer_orders"
    ),


    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "update-profile/",
        views.update_profile,
        name="update_profile"
    ),


    # =====================================================
    # WISHLIST
    # =====================================================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist"
    ),

    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),


    # =====================================================
    # ADMIN ORDERS
    # =====================================================

    path(
        "admin-orders/",
        views.admin_orders,
        name="admin_orders"
    ),
    
]